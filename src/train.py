"""
Integrated Training Pipeline — Text + Image Features
=====================================================
Combines your existing optimized text pipeline with multimodal features.
"""

import os, re, warnings, gc, sys
import numpy as np
import pandas as pd
from pathlib import Path
from tqdm import tqdm

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import RobustScaler
from sklearn.decomposition import TruncatedSVD, PCA
from sklearn.model_selection import KFold
from scipy.sparse import hstack, csr_matrix

import lightgbm as lgb
import catboost as cb
import xgboost as xgb

warnings.filterwarnings("ignore")

# ═══════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════
DATA_DIR        = Path("dataset")
OUTPUT_FILE     = DATA_DIR / "test_out.csv"
FEATURE_CACHE   = Path("C:/temp/ml_features")  # Local drive instead of OneDrive!

# Multimodal settings
USE_IMAGES      = False   # Set True to enable image processing (slower but better)
USE_EMBEDDINGS  = True    # Sentence embeddings
EMBEDDING_MODEL = "paraphrase-MiniLM-L6-v2"
EMB_PCA_DIMS    = 128

# Text features
TFIDF_FEATURES  = 30_000
SVD_DIMS        = 100

# Training
N_FOLDS         = 5
SEED            = 42

print("="*60)
print("MULTIMODAL PRODUCT PRICE PREDICTION PIPELINE")
print("="*60)
print(f"\nConfiguration:")
print(f"  Images enabled:     {USE_IMAGES}")
print(f"  Embeddings enabled: {USE_EMBEDDINGS}")
print(f"  N-Folds:            {N_FOLDS}")

# ═══════════════════════════════════════════════
# LOAD DATA
# ═══════════════════════════════════════════════
print("\n[1/10] Loading data...")
train = pd.read_csv(DATA_DIR / "train.csv")
test  = pd.read_csv(DATA_DIR / "test.csv")

# Outlier removal
q01, q99 = train["price"].quantile(0.01), train["price"].quantile(0.99)
train = train[(train["price"] >= q01) & (train["price"] <= q99)].reset_index(drop=True)
print(f"  Train: {len(train):,}  Test: {len(test):,}")

# ═══════════════════════════════════════════════
# MULTIMODAL FEATURES (Images + Text Embeddings)
# ═══════════════════════════════════════════════
print("\n[2/10] Extracting multimodal features...")

tr_img = te_img = None
tr_emb = te_emb = None

if USE_IMAGES or USE_EMBEDDINGS:
    try:
        # Try to import multimodal feature extractor
        # Fix import path - add src to path if needed
        src_path = Path(__file__).parent / "src"
        if src_path.exists() and str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))
        
        from multimodal_model import extract_multimodal_features
        
        # Extract or load cached features
        train_mm_feats, test_mm_feats = extract_multimodal_features(
            train, test,
            output_dir=str(FEATURE_CACHE),
            use_cache=True  # Will use cache if available
        )
        
        # Get arrays
        if USE_IMAGES:
            tr_img = train_mm_feats.get('image_features')  # (N, 512) or None
            te_img = test_mm_feats.get('image_features')
            if tr_img is not None:
                print(f"  ✓ Image features loaded: {tr_img.shape}")
        
        if USE_EMBEDDINGS:
            tr_emb_raw = train_mm_feats.get('text_embeddings')  # (N, 384) or None
            te_emb_raw = test_mm_feats.get('text_embeddings')
            
            # Apply PCA to embeddings to reduce memory
            if tr_emb_raw is not None:
                print(f"  Applying PCA to embeddings: 384 → {EMB_PCA_DIMS}...")
                pca = PCA(n_components=EMB_PCA_DIMS, random_state=SEED)
                tr_emb = pca.fit_transform(tr_emb_raw).astype(np.float32)
                te_emb = pca.transform(te_emb_raw).astype(np.float32)
                del tr_emb_raw, te_emb_raw; gc.collect()
                print(f"  ✓ Embeddings PCA: {tr_emb.shape}")
        
    except ImportError as e:
        print(f"  ⚠️  Multimodal features not available: {e}")
        print(f"  ⚠️  Continuing with text features only...")
        print(f"  💡 To enable: create src/multimodal_model.py")
        tr_img = te_img = None
        tr_emb = te_emb = None

# ═══════════════════════════════════════════════
# TEXT CLEANING
# ═══════════════════════════════════════════════
print("\n[3/10] Cleaning text...")

def clean(t):
    t = re.sub(r"https?://\S+", " ", str(t).lower())
    t = re.sub(r"[^a-z0-9\s\.\-\/\+]", " ", t)
    return re.sub(r"\s+", " ", t).strip()

train["tc"] = train["catalog_content"].apply(clean)
test["tc"]  = test["catalog_content"].apply(clean)

# ═══════════════════════════════════════════════
# ENGINEERED FEATURES
# ═══════════════════════════════════════════════
print("\n[4/10] Engineering features...")

def extract_ipq(text):
    m = re.search(r"(?:pack\s+of|ipq|quantity)[:\s]*(\d+)", str(text).lower())
    if m: return float(m.group(1))
    m = re.search(r"(\d+)\s*(?:pack|pcs|pieces|count|units)", str(text).lower())
    return float(m.group(1)) if m else 1.0

def max_digit(text):
    nums = re.findall(r"\b(\d+(?:\.\d+)?)\b", str(text))
    return max((float(x) for x in nums), default=0.0)

def engineer(df):
    f = pd.DataFrame()
    f["text_len"]   = df["tc"].str.len().astype(np.float32)
    f["word_count"] = df["tc"].str.split().str.len().astype(np.float32)
    f["digit_count"]= df["tc"].apply(lambda x: len(re.findall(r"\d+",x))).astype(np.float32)
    f["ipq"]        = df["catalog_content"].apply(extract_ipq).astype(np.float32)
    f["log_ipq"]    = np.log1p(f["ipq"]).astype(np.float32)
    f["max_digit"]  = df["tc"].apply(max_digit).astype(np.float32)
    f["log_maxd"]   = np.log1p(f["max_digit"]).astype(np.float32)
    
    # Brand indicators
    for kw in ["samsung","apple","sony","lg","philips","bosch","havells",
               "prestige","bajaj","whirlpool","godrej","amul","nestle",
               "himalaya","patanjali","britannia"]:
        f[f"b_{kw}"] = df["tc"].str.contains(kw,na=False).astype(np.int8)
    
    # Unit indicators
    for kw in ["ml","litre","ltr","kg","gram","gm","watt","inch","cm","gb","mah"]:
        f[f"u_{kw}"] = df["tc"].str.contains(kw,na=False).astype(np.int8)
    
    return f

tr_eng = engineer(train)
te_eng = engineer(test)

scaler = RobustScaler()
tr_eng_s = scaler.fit_transform(tr_eng.fillna(0)).astype(np.float32)
te_eng_s = scaler.transform(te_eng.fillna(0)).astype(np.float32)

print(f"  ✓ Engineered {tr_eng.shape[1]} features")

# ═══════════════════════════════════════════════
# TF-IDF
# ═══════════════════════════════════════════════
print(f"\n[5/10] TF-IDF ({TFIDF_FEATURES} features)...")

tfidf = TfidfVectorizer(
    max_features=TFIDF_FEATURES,
    ngram_range=(1,2),
    min_df=3,
    sublinear_tf=True,
    dtype=np.float32
)
tfidf.fit(pd.concat([train["tc"], test["tc"]]))
X_tr_tf = tfidf.transform(train["tc"])
X_te_tf = tfidf.transform(test["tc"])

print(f"  ✓ TF-IDF: {X_tr_tf.shape}  ~{X_tr_tf.data.nbytes/1e6:.0f} MB")

# ═══════════════════════════════════════════════
# LSA (for dense models)
# ═══════════════════════════════════════════════
print(f"\n[6/10] LSA {SVD_DIMS}d...")

svd = TruncatedSVD(n_components=SVD_DIMS, random_state=SEED)
X_tr_svd = svd.fit_transform(X_tr_tf).astype(np.float32)
X_te_svd = svd.transform(X_te_tf).astype(np.float32)

# ═══════════════════════════════════════════════
# ASSEMBLE FEATURE MATRICES
# ═══════════════════════════════════════════════
print("\n[7/10] Assembling feature matrices...")

# For LightGBM: sparse TF-IDF + engineered
X_lgb_tr = hstack([X_tr_tf, csr_matrix(tr_eng_s)], format="csr")
X_lgb_te = hstack([X_te_tf, csr_matrix(te_eng_s)], format="csr")

# For CatBoost/XGBoost: dense features only
dense_parts_tr = [X_tr_svd, tr_eng_s]
dense_parts_te = [X_te_svd, te_eng_s]

# Add multimodal features to dense matrix
if tr_img is not None and USE_IMAGES:
    dense_parts_tr.append(tr_img)
    dense_parts_te.append(te_img)
    print(f"  ✓ Added image features: {tr_img.shape}")

if tr_emb is not None and USE_EMBEDDINGS:
    dense_parts_tr.append(tr_emb)
    dense_parts_te.append(te_emb)
    print(f"  ✓ Added text embeddings: {tr_emb.shape}")

X_den_tr = np.hstack(dense_parts_tr).astype(np.float32)
X_den_te = np.hstack(dense_parts_te).astype(np.float32)

print(f"\n  LightGBM (sparse): {X_lgb_tr.shape}  ~{X_lgb_tr.data.nbytes/1e6:.0f} MB")
print(f"  CatBoost/XGBoost (dense): {X_den_tr.shape}  ~{X_den_tr.nbytes/1e6:.0f} MB")

y_tr = np.log1p(train["price"].values).astype(np.float32)

# ═══════════════════════════════════════════════
# METRICS
# ═══════════════════════════════════════════════
def smape(yt, yp):
    yt = np.asarray(yt, np.float64)
    yp = np.maximum(np.asarray(yp, np.float64), 1e-9)
    return np.mean(np.abs(yt-yp)/((np.abs(yt)+np.abs(yp))/2))*100

def to_price(a):
    return np.maximum(np.expm1(a.astype(np.float64)), 0.01)

# ═══════════════════════════════════════════════
# CROSS-VALIDATION SETUP
# ═══════════════════════════════════════════════
kf = KFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)
oof_lgb = np.zeros(len(train), np.float32)
oof_cb  = np.zeros(len(train), np.float32)
oof_xgb = np.zeros(len(train), np.float32)
p_lgb = np.zeros(len(test), np.float64)
p_cb  = np.zeros(len(test), np.float64)
p_xgb = np.zeros(len(test), np.float64)

# ═══════════════════════════════════════════════
# LIGHTGBM
# ═══════════════════════════════════════════════
print("\n[8/10] Training LightGBM...")

lgb_p = dict(
    objective="regression_l1", metric="mae",
    learning_rate=0.05, num_leaves=127, max_depth=8,
    min_child_samples=30, feature_fraction=0.4,
    bagging_fraction=0.8, bagging_freq=5,
    lambda_l1=0.1, lambda_l2=0.1,
    num_threads=4,
    verbose=-1, random_state=SEED,
)

for fold,(tri,vai) in enumerate(kf.split(X_lgb_tr),1):
    dtrain = lgb.Dataset(X_lgb_tr[tri], label=y_tr[tri], free_raw_data=True)
    dval   = lgb.Dataset(X_lgb_tr[vai], label=y_tr[vai], reference=dtrain, free_raw_data=True)
    m = lgb.train(lgb_p, dtrain, num_boost_round=2000, valid_sets=[dval],
                  callbacks=[lgb.early_stopping(50,verbose=False), lgb.log_evaluation(400)])
    oof_lgb[vai] = m.predict(X_lgb_tr[vai])
    p_lgb += m.predict(X_lgb_te) / N_FOLDS
    del m, dtrain, dval; gc.collect()
    print(f"  Fold {fold}  SMAPE: {smape(train.price.values[vai], to_price(oof_lgb[vai])):.3f}%")

lgb_oof_score = smape(train.price.values, to_price(oof_lgb))
print(f"  OOF: {lgb_oof_score:.3f}%")

# ═══════════════════════════════════════════════
# CATBOOST
# ═══════════════════════════════════════════════
print("\n[9/10] Training CatBoost...")

for fold,(tri,vai) in enumerate(kf.split(X_den_tr),1):
    m = cb.CatBoostRegressor(
        iterations=2000, learning_rate=0.05, depth=8,
        loss_function="MAE", eval_metric="MAE", l2_leaf_reg=3,
        od_type="Iter", od_wait=50, verbose=400,
        random_seed=SEED, thread_count=4
    )
    m.fit(X_den_tr[tri], y_tr[tri],
          eval_set=(X_den_tr[vai], y_tr[vai]), use_best_model=True)
    oof_cb[vai] = m.predict(X_den_tr[vai])
    p_cb += m.predict(X_den_te) / N_FOLDS
    del m; gc.collect()
    print(f"  Fold {fold}  SMAPE: {smape(train.price.values[vai], to_price(oof_cb[vai])):.3f}%")

cb_oof_score = smape(train.price.values, to_price(oof_cb))
print(f"  OOF: {cb_oof_score:.3f}%")

# ═══════════════════════════════════════════════
# XGBOOST
# ═══════════════════════════════════════════════
print("\n[10/10] Training XGBoost...")

for fold,(tri,vai) in enumerate(kf.split(X_den_tr),1):
    m = xgb.XGBRegressor(
        objective="reg:absoluteerror", max_depth=7, learning_rate=0.05,
        n_estimators=2000, subsample=0.8, colsample_bytree=0.6,
        min_child_weight=10, tree_method="hist", device="cpu",
        n_jobs=4, random_state=SEED, verbosity=0,
        early_stopping_rounds=50, eval_metric="mae"
    )
    m.fit(X_den_tr[tri], y_tr[tri],
          eval_set=[(X_den_tr[vai], y_tr[vai])], verbose=400)
    oof_xgb[vai] = m.predict(X_den_tr[vai])
    p_xgb += m.predict(X_den_te) / N_FOLDS
    del m; gc.collect()
    print(f"  Fold {fold}  SMAPE: {smape(train.price.values[vai], to_price(oof_xgb[vai])):.3f}%")

xgb_oof_score = smape(train.price.values, to_price(oof_xgb))
print(f"  OOF: {xgb_oof_score:.3f}%")

# ═══════════════════════════════════════════════
# ENSEMBLE WEIGHT SEARCH
# ═══════════════════════════════════════════════
print("\n" + "="*60)
print("ENSEMBLE OPTIMIZATION")
print("="*60)

best_w, best_s = (0.5,0.3,0.2), 999.0
for w1 in np.arange(0.1, 0.81, 0.05):
    for w2 in np.arange(0.05, 0.81-w1, 0.05):
        w3 = round(1-w1-w2, 6)
        if w3 < 0.05: continue
        s = smape(train.price.values, to_price(w1*oof_lgb+w2*oof_cb+w3*oof_xgb))
        if s < best_s:
            best_s, best_w = s, (w1, w2, w3)

print(f"Optimal weights:")
print(f"  LightGBM: {best_w[0]:.2f}")
print(f"  CatBoost: {best_w[1]:.2f}")
print(f"  XGBoost:  {best_w[2]:.2f}")
print(f"  Ensemble SMAPE: {best_s:.3f}%")

# ═══════════════════════════════════════════════
# GENERATE SUBMISSION
# ═══════════════════════════════════════════════
print("\n" + "="*60)
print("GENERATING SUBMISSION")
print("="*60)

final = to_price(best_w[0]*p_lgb + best_w[1]*p_cb + best_w[2]*p_xgb)
final = np.maximum(final, train["price"].quantile(0.01))

out = pd.DataFrame({
    "sample_id": test["sample_id"],
    "price": np.round(final, 2)
})

out.to_csv(OUTPUT_FILE, index=False)

print(f"\n✓ Saved {len(out):,} predictions → {OUTPUT_FILE}")
print(f"\nSample predictions:")
print(out.head(10).to_string(index=False))
print(f"\nPrice statistics:")
print(f"  Min:    ${out.price.min():.2f}")
print(f"  Median: ${out.price.median():.2f}")
print(f"  Max:    ${out.price.max():.2f}")

print("\n" + "="*60)
print("TRAINING COMPLETE!")
print("="*60)
print(f"Model Performance:")
print(f"  LightGBM OOF:     {lgb_oof_score:.3f}%")
print(f"  CatBoost OOF:     {cb_oof_score:.3f}%")
print(f"  XGBoost OOF:      {xgb_oof_score:.3f}%")
print(f"  Ensemble OOF:     {best_s:.3f}%")
print(f"\nFeatures used:")
print(f"  TF-IDF:           ✓ ({TFIDF_FEATURES} features)")
print(f"  Engineered:       ✓ ({tr_eng.shape[1]} features)")
print(f"  LSA:              ✓ ({SVD_DIMS}d)")
print(f"  Image (CLIP):     {'✓ (512d)' if USE_IMAGES and tr_img is not None else '✗'}")
print(f"  Text embeddings:  {'✓ ('+str(EMB_PCA_DIMS)+'d PCA)' if USE_EMBEDDINGS and tr_emb is not None else '✗'}")
print("="*60)