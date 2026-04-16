"""
FastAPI Inference Server
========================
Production-ready API for real-time price predictions.
Supports both single product and batch predictions.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
import numpy as np
import joblib
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════
# API Models
# ═══════════════════════════════════════════════

class ProductInput(BaseModel):
    """Single product input for prediction"""
    catalog_content: str = Field(..., description="Product description text")
    image_link: Optional[str] = Field(None, description="Product image URL (optional)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "catalog_content": "Samsung Galaxy S23 Ultra 256GB - Premium Smartphone - IPQ: 1",
                "image_link": "https://example.com/product.jpg"
            }
        }


class BatchProductInput(BaseModel):
    """Batch prediction input"""
    products: List[ProductInput] = Field(..., description="List of products")


class PredictionOutput(BaseModel):
    """Prediction output"""
    predicted_price: float = Field(..., description="Predicted price in USD")
    confidence_interval: Optional[tuple] = Field(None, description="95% confidence interval")


class BatchPredictionOutput(BaseModel):
    """Batch prediction output"""
    predictions: List[PredictionOutput]
    total_processed: int


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    model_loaded: bool
    version: str


# ═══════════════════════════════════════════════
# Model Loader
# ═══════════════════════════════════════════════

class PricePredictorService:
    """Service class for loading and managing models"""
    
    def __init__(self, model_dir: str = "models"):
        self.model_dir = Path(model_dir)
        self.models = {}
        self.feature_extractor = None
        self.scaler = None
        self.loaded = False
        
    def load_models(self):
        """Load all required models and preprocessors"""
        try:
            logger.info("Loading models...")
            
            # Load ensemble models
            self.models['lgb'] = joblib.load(self.model_dir / "lightgbm_model.pkl")
            self.models['cat'] = joblib.load(self.model_dir / "catboost_model.pkl")
            self.models['xgb'] = joblib.load(self.model_dir / "xgboost_model.pkl")
            
            # Load preprocessors
            self.scaler = joblib.load(self.model_dir / "scaler.pkl")
            
            # Load ensemble weights
            weights_path = self.model_dir / "ensemble_weights.npy"
            if weights_path.exists():
                self.ensemble_weights = np.load(weights_path)
            else:
                # Default equal weights
                self.ensemble_weights = np.array([0.4, 0.3, 0.3])
            
            # Load multimodal feature extractor (optional)
            try:
                from src.multimodal_model import MultimodalFeatureExtractor
                self.feature_extractor = MultimodalFeatureExtractor()
                logger.info("Multimodal features enabled")
            except:
                logger.warning("Multimodal features not available - using text only")
                self.feature_extractor = None
            
            self.loaded = True
            logger.info("✓ All models loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            raise
    
    def extract_features(self, product: ProductInput) -> np.ndarray:
        """Extract features from a single product"""
        import re
        
        # Basic text features
        text = str(product.catalog_content).lower()
        
        features = {
            'text_len': len(text),
            'word_count': len(text.split()),
            'digit_count': len(re.findall(r'\d+', text)),
        }
        
        # Extract IPQ
        ipq_match = re.search(r'(?:pack\s+of|ipq|quantity)[:\s]*(\d+)', text)
        features['ipq'] = float(ipq_match.group(1)) if ipq_match else 1.0
        features['log_ipq'] = np.log1p(features['ipq'])
        
        # Max digit
        nums = re.findall(r'\b(\d+(?:\.\d+)?)\b', text)
        features['max_digit'] = max((float(x) for x in nums), default=0.0)
        features['log_maxd'] = np.log1p(features['max_digit'])
        
        # Brand indicators
        brands = ["samsung","apple","sony","lg","philips","bosch","havells",
                  "prestige","bajaj","whirlpool","godrej","amul","nestle"]
        for brand in brands:
            features[f'b_{brand}'] = int(brand in text)
        
        # Unit indicators
        units = ["ml","litre","ltr","kg","gram","gm","watt","inch","cm","gb","mah"]
        for unit in units:
            features[f'u_{unit}'] = int(unit in text)
        
        # Convert to array
        feature_vector = np.array(list(features.values()), dtype=np.float32).reshape(1, -1)
        
        # Scale
        if self.scaler:
            feature_vector = self.scaler.transform(feature_vector)
        
        # Add multimodal features if available
        if self.feature_extractor and product.image_link:
            try:
                # Download and process image
                img = self.feature_extractor.download_image(product.image_link)
                if img:
                    img_features = self.feature_extractor.extract_image_features(img)
                    feature_vector = np.hstack([feature_vector, img_features.reshape(1, -1)])
                
                # Add text embeddings
                text_emb = self.feature_extractor.extract_text_embeddings([product.catalog_content])
                feature_vector = np.hstack([feature_vector, text_emb])
            except Exception as e:
                logger.warning(f"Error extracting multimodal features: {e}")
        
        return feature_vector
    
    def predict(self, features: np.ndarray) -> float:
        """Make prediction using ensemble"""
        if not self.loaded:
            raise RuntimeError("Models not loaded")
        
        # Get predictions from each model
        pred_lgb = self.models['lgb'].predict(features)
        pred_cat = self.models['cat'].predict(features)
        pred_xgb = self.models['xgb'].predict(features)
        
        # Weighted ensemble
        w = self.ensemble_weights
        ensemble_pred = w[0] * pred_lgb + w[1] * pred_cat + w[2] * pred_xgb
        
        # Convert from log space to price
        price = np.maximum(np.expm1(ensemble_pred[0]), 0.01)
        
        return float(price)


# ═══════════════════════════════════════════════
# Initialize FastAPI
# ═══════════════════════════════════════════════

app = FastAPI(
    title="Product Price Prediction API",
    description="ML-powered API for predicting e-commerce product prices",
    version="1.0.0"
)

# Initialize service
predictor_service = PricePredictorService()


@app.on_event("startup")
async def startup_event():
    """Load models on startup"""
    logger.info("Starting up API server...")
    predictor_service.load_models()
    logger.info("API server ready")


# ═══════════════════════════════════════════════
# API Endpoints
# ═══════════════════════════════════════════════

@app.get("/", response_model=dict)
async def root():
    """Root endpoint"""
    return {
        "message": "Product Price Prediction API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "predict": "/predict",
            "batch_predict": "/batch_predict",
            "docs": "/docs"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy" if predictor_service.loaded else "unhealthy",
        model_loaded=predictor_service.loaded,
        version="1.0.0"
    )


@app.post("/predict", response_model=PredictionOutput)
async def predict_price(product: ProductInput):
    """
    Predict price for a single product.
    
    Args:
        product: Product information including catalog content and optional image link
        
    Returns:
        Predicted price
    """
    try:
        # Extract features
        features = predictor_service.extract_features(product)
        
        # Predict
        predicted_price = predictor_service.predict(features)
        
        return PredictionOutput(
            predicted_price=round(predicted_price, 2),
            confidence_interval=None  # Can add confidence intervals later
        )
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/batch_predict", response_model=BatchPredictionOutput)
async def batch_predict(batch: BatchProductInput):
    """
    Predict prices for multiple products.
    
    Args:
        batch: List of products
        
    Returns:
        List of predictions
    """
    try:
        predictions = []
        
        for product in batch.products:
            features = predictor_service.extract_features(product)
            predicted_price = predictor_service.predict(features)
            
            predictions.append(PredictionOutput(
                predicted_price=round(predicted_price, 2),
                confidence_interval=None
            ))
        
        return BatchPredictionOutput(
            predictions=predictions,
            total_processed=len(predictions)
        )
        
    except Exception as e:
        logger.error(f"Batch prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/model/info")
async def model_info():
    """Get information about loaded models"""
    if not predictor_service.loaded:
        raise HTTPException(status_code=503, detail="Models not loaded")
    
    return {
        "models_loaded": list(predictor_service.models.keys()),
        "ensemble_weights": predictor_service.ensemble_weights.tolist(),
        "multimodal_enabled": predictor_service.feature_extractor is not None
    }


# ═══════════════════════════════════════════════
# Run server
# ═══════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )