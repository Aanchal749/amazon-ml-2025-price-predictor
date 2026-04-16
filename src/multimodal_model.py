"""
Multimodal Product Price Predictor
===================================
Production-ready class that processes images + text for price prediction.
Integrates with existing pipeline from pipeline.py
"""

import numpy as np
import pandas as pd
import torch
from PIL import Image
import requests
from io import BytesIO
from tqdm.auto import tqdm
import warnings
import gc
from pathlib import Path
from typing import Optional, Tuple

warnings.filterwarnings('ignore')

# Import models
from transformers import CLIPProcessor, CLIPModel
from sentence_transformers import SentenceTransformer


class MultimodalFeatureExtractor:
    """
    Extracts visual + textual features from product data.
    Designed to work alongside existing TF-IDF/engineered features.
    """
    
    def __init__(
        self,
        clip_model_name: str = "openai/clip-vit-base-patch32",
        text_model_name: str = "paraphrase-MiniLM-L6-v2",
        use_gpu: bool = True,
        cache_dir: Optional[Path] = None
    ):
        """
        Initialize multimodal feature extractor.
        
        Args:
            clip_model_name: HuggingFace CLIP model identifier
            text_model_name: Sentence transformer model name
            use_gpu: Use GPU if available
            cache_dir: Directory to cache downloaded images
        """
        self.device = 'cuda' if (use_gpu and torch.cuda.is_available()) else 'cpu'
        self.cache_dir = Path(cache_dir) if cache_dir else None
        
        print(f"Initializing MultimodalFeatureExtractor on {self.device}...")
        
        # Load CLIP for image features
        self.clip_model = CLIPModel.from_pretrained(clip_model_name)
        self.clip_processor = CLIPProcessor.from_pretrained(clip_model_name)
        self.clip_model.eval()
        
        if self.device == 'cuda':
            self.clip_model = self.clip_model.cuda()
        
        # Load sentence transformer for text embeddings
        self.text_model = SentenceTransformer(text_model_name)
        
        print(f"✓ Models loaded on {self.device}")
    
    def download_image(
        self,
        url: str,
        timeout: int = 10,
        max_retries: int = 3
    ) -> Optional[Image.Image]:
        """
        Download image from URL with retry logic.
        
        Args:
            url: Image URL
            timeout: Request timeout in seconds
            max_retries: Number of retry attempts
            
        Returns:
            PIL Image or None if failed
        """
        # Check cache first
        if self.cache_dir:
            cache_path = self.cache_dir / f"{hash(url)}.jpg"
            if cache_path.exists():
                try:
                    return Image.open(cache_path).convert('RGB')
                except:
                    pass
        
        # Download from URL
        for attempt in range(max_retries):
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                response = requests.get(url, timeout=timeout, headers=headers)
                
                if response.status_code == 200:
                    img = Image.open(BytesIO(response.content)).convert('RGB')
                    
                    # Cache if enabled
                    if self.cache_dir:
                        self.cache_dir.mkdir(exist_ok=True)
                        img.save(cache_path, 'JPEG', quality=85)
                    
                    return img
            except Exception as e:
                if attempt == max_retries - 1:
                    return None
                continue
        
        return None
    
    def extract_image_features(self, image: Image.Image) -> np.ndarray:
        """
        Extract CLIP features from image.
        
        Args:
            image: PIL Image
            
        Returns:
            512-dimensional feature vector
        """
        try:
            inputs = self.clip_processor(images=image, return_tensors="pt")
            
            if self.device == 'cuda':
                inputs = {k: v.cuda() for k, v in inputs.items()}
            
            with torch.no_grad():
                features = self.clip_model.get_image_features(**inputs)
            
            return features.cpu().numpy().flatten()
        
        except Exception as e:
            # Return zero vector on failure
            return np.zeros(512, dtype=np.float32)
    
    def process_images_batch(
        self,
        df: pd.DataFrame,
        image_col: str = 'image_link',
        batch_size: int = 100,
        desc: str = "Processing images"
    ) -> np.ndarray:
        """
        Process all images in dataframe.
        
        Args:
            df: DataFrame with image URLs
            image_col: Column name containing image URLs
            batch_size: Batch size for processing
            desc: Progress bar description
            
        Returns:
            Array of shape (n_samples, 512) with image features
        """
        all_features = []
        success_count = 0
        
        print(f"\n{desc} ({len(df)} images)...")
        
        for idx in tqdm(range(len(df)), desc=desc):
            url = df.iloc[idx][image_col]
            
            # Download and extract
            img = self.download_image(url)
            
            if img is not None:
                features = self.extract_image_features(img)
                success_count += 1
            else:
                features = np.zeros(512, dtype=np.float32)
            
            all_features.append(features)
            
            # Memory cleanup every batch
            if (idx + 1) % batch_size == 0:
                gc.collect()
        
        features_array = np.array(all_features, dtype=np.float32)
        
        print(f"✓ Success rate: {success_count}/{len(df)} ({success_count/len(df)*100:.1f}%)")
        print(f"  Feature shape: {features_array.shape}")
        
        return features_array
    
    def extract_text_embeddings(
        self,
        texts: list,
        batch_size: int = 64,
        max_length: int = 256,
        desc: str = "Text embeddings"
    ) -> np.ndarray:
        """
        Extract sentence embeddings from text.
        
        Args:
            texts: List of text strings
            batch_size: Encoding batch size
            max_length: Maximum text length
            desc: Progress description
            
        Returns:
            Array of shape (n_samples, 384) with text embeddings
        """
        print(f"\n{desc} ({len(texts)} samples)...")
        
        # Truncate texts
        truncated = [str(t)[:max_length] for t in texts]
        
        # Encode in batches
        embeddings = self.text_model.encode(
            truncated,
            batch_size=batch_size,
            show_progress_bar=True,
            normalize_embeddings=True
        )
        
        print(f"✓ Embedding shape: {embeddings.shape}")
        
        return embeddings.astype(np.float32)
    
    def extract_all_features(
        self,
        df: pd.DataFrame,
        text_col: str = 'catalog_content',
        image_col: str = 'image_link',
        extract_images: bool = True,
        extract_text: bool = True
    ) -> dict:
        """
        Extract all multimodal features.
        
        Args:
            df: Input dataframe
            text_col: Text column name
            image_col: Image URL column name
            extract_images: Whether to process images
            extract_text: Whether to extract text embeddings
            
        Returns:
            Dictionary with 'image_features' and 'text_embeddings'
        """
        features = {}
        
        if extract_images and image_col in df.columns:
            features['image_features'] = self.process_images_batch(df, image_col)
        
        if extract_text and text_col in df.columns:
            features['text_embeddings'] = self.extract_text_embeddings(
                df[text_col].fillna('').tolist()
            )
        
        return features
    
    def save_features(self, features: dict, output_dir: Path):
        """Save extracted features to disk."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for name, array in features.items():
            path = output_dir / f"{name}.npy"
            np.save(path, array)
            print(f"✓ Saved {name}: {array.shape} → {path}")
    
    def load_features(self, feature_dir: Path) -> dict:
        """Load pre-extracted features from disk."""
        feature_dir = Path(feature_dir)
        features = {}
        
        for path in feature_dir.glob("*.npy"):
            name = path.stem
            features[name] = np.load(path)
            print(f"✓ Loaded {name}: {features[name].shape}")
        
        return features
    
    def cleanup(self):
        """Free memory."""
        if hasattr(self, 'clip_model'):
            del self.clip_model
        if hasattr(self, 'clip_processor'):
            del self.clip_processor
        if hasattr(self, 'text_model'):
            del self.text_model
        
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()


# ── Convenience function ──
def extract_multimodal_features(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    output_dir: str = "features",
    use_cache: bool = True
) -> Tuple[dict, dict]:
    """
    High-level function to extract features for train and test sets.
    
    Args:
        train_df: Training dataframe
        test_df: Test dataframe  
        output_dir: Where to save/load features
        use_cache: Use cached features if available
        
    Returns:
        (train_features, test_features) dictionaries
    """
    output_path = Path(output_dir)
    
    # Check for cached features
    if use_cache and output_path.exists():
        train_cache = output_path / "train"
        test_cache = output_path / "test"
        
        if train_cache.exists() and test_cache.exists():
            print("✓ Loading cached features...")
            # Check if both train and test have the required .npy files
            train_files = list(train_cache.glob("*.npy"))
            test_files = list(test_cache.glob("*.npy"))
            
            if train_files and test_files:
                extractor = MultimodalFeatureExtractor()
                train_feats = extractor.load_features(train_cache)
                test_feats = extractor.load_features(test_cache)
                extractor.cleanup()
                return train_feats, test_feats
            else:
                print("⚠️  Cache incomplete, extracting fresh features...")
    
    # Extract fresh features
    print("Extracting fresh multimodal features...")
    extractor = MultimodalFeatureExtractor()
    
    print("\n=== TRAINING SET ===")
    train_feats = extractor.extract_all_features(train_df)
    
    print("\n=== TEST SET ===")
    test_feats = extractor.extract_all_features(test_df)
    
    # Save for future use (DISABLED to avoid disk space issues)
    if use_cache and False:  # Disabled - skip saving to disk
        try:
            print("\n💾 Caching features for future runs...")
            extractor.save_features(train_feats, output_path / "train")
            extractor.save_features(test_feats, output_path / "test")
        except Exception as e:
            print(f"⚠️  Could not save cache: {e}")
            print("   Continuing without cache...")
    
    extractor.cleanup()
    
    return train_feats, test_feats