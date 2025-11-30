"""
Unified AI Service integrating OCR, Image Verification, and LLM
"""
import os
import numpy as np
from typing import Dict, Any, Optional
from services.ocr_service import OCRService, extract_medicine_info_from_image
from services.image_verification import ImageVerificationService, load_image_from_file
from services.llm_service import LLMService

class AIService:
    """Unified AI service for medicine verification and information"""
    
    def __init__(self):
        """Initialize AI service with all components"""
        # Initialize OCR service
        self.ocr_service = OCRService()
        
        # Initialize image verification service
        self.image_verification = ImageVerificationService(model_type='mobilenet')
        
        # Initialize LLM service
        self.llm_service = LLMService()
    
    def verify_medicine_package(self, image_file, medicine_id: Optional[str] = None,
                               golden_image_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Comprehensive medicine package verification
        Combines OCR and image verification
        """
        result = {
            "ocr_result": None,
            "image_verification": None,
            "overall_verification": False,
            "confidence": 0.0,
            "details": {}
        }
        
        try:
            # Load image
            image = load_image_from_file(image_file)
            if image is None:
                return {
                    **result,
                    "error": "Failed to load image"
                }
            
            # Perform OCR
            ocr_result = self.ocr_service.extract_medicine_info(image)
            result["ocr_result"] = ocr_result
            
            # Perform image verification if golden image available
            if medicine_id and golden_image_path:
                golden_image = load_image_from_file(open(golden_image_path, 'rb'))
                if golden_image is not None:
                    # Add golden image if not already added
                    if medicine_id not in self.image_verification.golden_images:
                        self.image_verification.add_golden_image(medicine_id, golden_image)
                    
                    # Verify image
                    image_verification = self.image_verification.verify_medicine_image(
                        image, medicine_id, threshold=0.85
                    )
                    result["image_verification"] = image_verification
                else:
                    result["image_verification"] = {
                        "error": "Failed to load golden image"
                    }
            
            # Calculate overall verification
            ocr_confidence = ocr_result.get("confidence", 0.0)
            image_confidence = result["image_verification"].get("confidence", 0.0) if result["image_verification"] else 0.0
            
            # Weighted confidence calculation
            if result["image_verification"] and not result["image_verification"].get("error"):
                # Both OCR and image verification available
                overall_confidence = (ocr_confidence * 0.4) + (image_confidence / 100 * 0.6)
                result["overall_verification"] = (
                    ocr_confidence > 0.5 and 
                    result["image_verification"].get("matches", False)
                )
            else:
                # Only OCR available
                overall_confidence = ocr_confidence
                result["overall_verification"] = ocr_confidence > 0.6
            
            result["confidence"] = overall_confidence
            result["details"] = {
                "ocr_confidence": ocr_confidence,
                "image_confidence": image_confidence,
                "parsed_info": ocr_result.get("parsed_info", {})
            }
            
        except Exception as e:
            result["error"] = str(e)
            print(f"Error in medicine package verification: {e}")
        
        return result
    
    def get_medicine_ai_summary(self, medicine_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get AI-generated summary of medicine information
        """
        try:
            summary = self.llm_service.summarize_medicine_info(medicine_data)
            text_summary = self.llm_service.generate_ai_summary(medicine_data)
            
            return {
                "summary": summary,
                "text_summary": text_summary,
                "source": summary.get("source", "unknown")
            }
        except Exception as e:
            print(f"Error generating AI summary: {e}")
            return {
                "summary": self.llm_service._generate_fallback_summary(medicine_data),
                "text_summary": "AI summary not available",
                "source": "fallback",
                "error": str(e)
            }
    
    def extract_text_from_image(self, image_file) -> str:
        """Extract text from image using OCR"""
        return self.ocr_service.extract_text_from_file(image_file)
    
    def verify_image_similarity(self, image1_file, image2_file) -> Dict[str, Any]:
        """Verify similarity between two images"""
        try:
            image1 = load_image_from_file(image1_file)
            image2 = load_image_from_file(image2_file)
            
            if image1 is None or image2 is None:
                return {
                    "error": "Failed to load images"
                }
            
            return self.image_verification.compare_images(image1, image2)
        except Exception as e:
            return {
                "error": str(e)
            }
    
    def add_golden_image(self, medicine_id: str, image_file):
        """Add golden image for medicine"""
        try:
            image = load_image_from_file(image_file)
            if image is None:
                return False
            
            self.image_verification.add_golden_image(medicine_id, image)
            return True
        except Exception as e:
            print(f"Error adding golden image: {e}")
            return False

# Global AI service instance
_ai_service = None

def get_ai_service() -> AIService:
    """Get global AI service instance"""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service



