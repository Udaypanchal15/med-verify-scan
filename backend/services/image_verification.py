"""
Image Verification Service for medicine packaging
Uses pre-trained CNN models (MobileNet/ResNet) for image similarity checking
"""
import os
import numpy as np
import cv2
from PIL import Image
import io
from typing import Dict, Any, Optional, Tuple
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2, ResNet50
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input as mobilenet_preprocess
from tensorflow.keras.applications.resnet50 import preprocess_input as resnet_preprocess
from tensorflow.keras.preprocessing import image as keras_image
from sklearn.metrics.pairwise import cosine_similarity
import pickle

class ImageVerificationService:
    """Image verification service using deep learning models"""
    
    def __init__(self, model_type: str = 'mobilenet', model_path: Optional[str] = None):
        """
        Initialize image verification service
        model_type: 'mobilenet' or 'resnet'
        model_path: Path to saved model (optional)
        """
        self.model_type = model_type.lower()
        self.model = None
        self.feature_extractor = None
        self.golden_images = {}  # Store golden/reference images
        
        # Load pre-trained model
        self._load_model()
    
    def _load_model(self):
        """Load pre-trained CNN model for feature extraction"""
        try:
            if self.model_type == 'mobilenet':
                # Load MobileNetV2 (lightweight, fast)
                base_model = MobileNetV2(
                    weights='imagenet',
                    include_top=False,
                    pooling='avg',
                    input_shape=(224, 224, 3)
                )
                self.feature_extractor = tf.keras.Model(
                    inputs=base_model.input,
                    outputs=base_model.output
                )
                self.preprocess_input = mobilenet_preprocess
            elif self.model_type == 'resnet':
                # Load ResNet50 (more accurate, slower)
                base_model = ResNet50(
                    weights='imagenet',
                    include_top=False,
                    pooling='avg',
                    input_shape=(224, 224, 3)
                )
                self.feature_extractor = tf.keras.Model(
                    inputs=base_model.input,
                    outputs=base_model.output
                )
                self.preprocess_input = resnet_preprocess
            else:
                raise ValueError(f"Unsupported model type: {self.model_type}")
            
            print(f"Loaded {self.model_type} model successfully")
        except Exception as e:
            print(f"Error loading model: {e}")
            # Fallback to MobileNet if ResNet fails
            if self.model_type == 'resnet':
                print("Falling back to MobileNet")
                self.model_type = 'mobilenet'
                self._load_model()
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for model input
        - Resize to 224x224
        - Convert to RGB
        - Normalize
        """
        # Resize image
        resized = cv2.resize(image, (224, 224))
        
        # Convert BGR to RGB if needed
        if len(resized.shape) == 3 and resized.shape[2] == 3:
            resized = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        
        # Convert to array and add batch dimension
        img_array = np.expand_dims(resized, axis=0)
        
        # Preprocess for model
        preprocessed = self.preprocess_input(img_array)
        
        return preprocessed
    
    def extract_features(self, image: np.ndarray) -> np.ndarray:
        """
        Extract features from image using CNN
        Returns feature vector
        """
        try:
            # Preprocess image
            preprocessed = self.preprocess_image(image)
            
            # Extract features
            features = self.feature_extractor.predict(preprocessed, verbose=0)
            
            # Normalize features
            features = features / (np.linalg.norm(features) + 1e-8)
            
            return features.flatten()
        except Exception as e:
            print(f"Error extracting features: {e}")
            return np.zeros(1280 if self.model_type == 'mobilenet' else 2048)
    
    def add_golden_image(self, medicine_id: str, image: np.ndarray):
        """
        Add a golden/reference image for a medicine
        This is the authentic packaging image
        """
        features = self.extract_features(image)
        self.golden_images[medicine_id] = features
        return features
    
    def verify_image(self, image: np.ndarray, golden_features: np.ndarray,
                    threshold: float = 0.85) -> Dict[str, Any]:
        """
        Verify if image matches golden image
        Returns verification result with similarity score
        """
        # Extract features from input image
        input_features = self.extract_features(image)
        
        # Calculate cosine similarity
        similarity = cosine_similarity(
            input_features.reshape(1, -1),
            golden_features.reshape(1, -1)
        )[0][0]
        
        # Determine if image matches
        matches = similarity >= threshold
        
        return {
            "matches": matches,
            "similarity": float(similarity),
            "threshold": threshold,
            "confidence": min(similarity * 100, 100.0)
        }
    
    def verify_medicine_image(self, image: np.ndarray, medicine_id: str,
                             threshold: float = 0.85) -> Dict[str, Any]:
        """
        Verify medicine image against stored golden image
        Returns verification result
        """
        # Check if golden image exists
        if medicine_id not in self.golden_images:
            return {
                "matches": False,
                "similarity": 0.0,
                "error": "Golden image not found for this medicine",
                "confidence": 0.0
            }
        
        # Get golden features
        golden_features = self.golden_images[medicine_id]
        
        # Verify image
        return self.verify_image(image, golden_features, threshold)
    
    def compare_images(self, image1: np.ndarray, image2: np.ndarray) -> Dict[str, Any]:
        """
        Compare two images and return similarity score
        """
        # Extract features from both images
        features1 = self.extract_features(image1)
        features2 = self.extract_features(image2)
        
        # Calculate similarity
        similarity = cosine_similarity(
            features1.reshape(1, -1),
            features2.reshape(1, -1)
        )[0][0]
        
        return {
            "similarity": float(similarity),
            "confidence": min(similarity * 100, 100.0)
        }
    
    def save_golden_images(self, filepath: str):
        """Save golden images to file"""
        try:
            with open(filepath, 'wb') as f:
                pickle.dump(self.golden_images, f)
            return True
        except Exception as e:
            print(f"Error saving golden images: {e}")
            return False
    
    def load_golden_images(self, filepath: str):
        """Load golden images from file"""
        try:
            with open(filepath, 'rb') as f:
                self.golden_images = pickle.load(f)
            return True
        except Exception as e:
            print(f"Error loading golden images: {e}")
            return False

def load_image_from_file(image_file) -> np.ndarray:
    """Load image from file and convert to numpy array"""
    try:
        image_data = image_file.read()
        image = Image.open(io.BytesIO(image_data))
        image_array = np.array(image)
        
        # Convert RGB to BGR for OpenCV
        if len(image_array.shape) == 3 and image_array.shape[2] == 3:
            image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        
        return image_array
    except Exception as e:
        print(f"Error loading image: {e}")
        return None



