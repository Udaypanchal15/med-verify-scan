"""
OCR Service for extracting text from medicine packaging images
Uses pytesseract with OpenCV preprocessing for better accuracy
"""
import os
import pytesseract
import cv2
import numpy as np
from PIL import Image
import io
from typing import Dict, Any, Optional, List
import re

class OCRService:
    """OCR service for medicine packaging text extraction"""
    
    def __init__(self, tesseract_cmd: Optional[str] = None):
        """
        Initialize OCR service
        tesseract_cmd: Path to tesseract executable (if not in PATH)
        """
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        else:
            # Try to get from environment variable
            tesseract_cmd = os.getenv('TESSERACT_CMD')
            if tesseract_cmd:
                pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for better OCR accuracy
        - Convert to grayscale
        - Apply noise reduction
        - Enhance contrast
        - Thresholding
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Apply morphological operations to clean up
        kernel = np.ones((2, 2), np.uint8)
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        # Enhance contrast using CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(cleaned)
        
        return enhanced
    
    def extract_text(self, image: np.ndarray, preprocess: bool = True) -> str:
        """
        Extract text from image using OCR
        Returns extracted text
        """
        try:
            # Preprocess image if requested
            if preprocess:
                processed_image = self.preprocess_image(image)
            else:
                processed_image = image
            
            # Extract text using pytesseract
            text = pytesseract.image_to_string(
                processed_image,
                lang='eng',
                config='--psm 6'  # Assume uniform block of text
            )
            
            return text.strip()
        except Exception as e:
            print(f"OCR extraction error: {e}")
            return ""
    
    def extract_medicine_info(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Extract medicine information from packaging image
        Returns structured medicine information
        """
        # Extract raw text
        raw_text = self.extract_text(image, preprocess=True)
        
        # Parse medicine information
        info = self.parse_medicine_text(raw_text)
        
        return {
            "raw_text": raw_text,
            "parsed_info": info,
            "confidence": self._calculate_confidence(raw_text)
        }
    
    def parse_medicine_text(self, text: str) -> Dict[str, Any]:
        """
        Parse extracted text to extract medicine information
        Uses regex patterns to find medicine name, batch number, dates, etc.
        """
        info = {
            "medicine_name": None,
            "batch_number": None,
            "manufacture_date": None,
            "expiry_date": None,
            "dosage": None,
            "strength": None,
            "manufacturer": None
        }
        
        # Extract medicine name (usually at the beginning, uppercase)
        name_pattern = r'\b([A-Z][A-Z\s]{3,30})\b'
        names = re.findall(name_pattern, text[:200])
        if names:
            info["medicine_name"] = names[0].strip()
        
        # Extract batch number (BATCH, LOT, BATCH NO, etc.)
        batch_patterns = [
            r'(?:BATCH|LOT|BATCH\s*NO|BATCH\s*#)[:\s]*([A-Z0-9\-]+)',
            r'BATCH\s*([A-Z0-9]{4,20})',
            r'LOT\s*([A-Z0-9]{4,20})'
        ]
        for pattern in batch_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info["batch_number"] = match.group(1).strip()
                break
        
        # Extract manufacture date
        mfg_patterns = [
            r'(?:MFG|MANUFACTURE|MANUFACTURED)[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'MFG[:\s]*(\d{2}[/-]\d{2}[/-]\d{4})'
        ]
        for pattern in mfg_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info["manufacture_date"] = match.group(1).strip()
                break
        
        # Extract expiry date
        exp_patterns = [
            r'(?:EXP|EXPIRY|EXPIRES|EXP DATE)[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'EXP[:\s]*(\d{2}[/-]\d{2}[/-]\d{4})',
            r'USE\s*BY[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
        ]
        for pattern in exp_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info["expiry_date"] = match.group(1).strip()
                break
        
        # Extract dosage
        dosage_patterns = [
            r'(\d+\s*(?:mg|g|ml|mcg|IU|units?))',
            r'DOSAGE[:\s]*(\d+\s*(?:mg|g|ml|mcg))'
        ]
        for pattern in dosage_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info["dosage"] = match.group(1).strip()
                break
        
        # Extract strength
        strength_patterns = [
            r'STRENGTH[:\s]*(\d+\s*(?:mg|g|ml|mcg))',
            r'(\d+\s*(?:mg|g|ml|mcg)\s*/\s*\d+\s*(?:mg|g|ml|mcg))'
        ]
        for pattern in strength_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info["strength"] = match.group(1).strip()
                break
        
        # Extract manufacturer (usually company name)
        manufacturer_patterns = [
            r'(?:MADE\s*BY|MANUFACTURED\s*BY|MANUFACTURER)[:\s]*([A-Z][A-Z\s&]{5,50})',
            r'([A-Z][A-Z\s&]{5,50})\s*(?:PVT|LTD|INC|CORP)'
        ]
        for pattern in manufacturer_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info["manufacturer"] = match.group(1).strip()
                break
        
        return info
    
    def _calculate_confidence(self, text: str) -> float:
        """
        Calculate confidence score based on extracted text
        Returns confidence score between 0 and 1
        """
        if not text or len(text.strip()) < 10:
            return 0.0
        
        # Base confidence on text length and keyword presence
        confidence = 0.3
        
        # Check for medicine-related keywords
        keywords = ['BATCH', 'EXP', 'MFG', 'DOSAGE', 'STRENGTH', 'MEDICINE', 'TABLET', 'CAPSULE']
        found_keywords = sum(1 for keyword in keywords if keyword in text.upper())
        confidence += min(found_keywords * 0.1, 0.4)
        
        # Check for dates
        date_pattern = r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}'
        dates = re.findall(date_pattern, text)
        if dates:
            confidence += 0.2
        
        # Check for alphanumeric batch numbers
        batch_pattern = r'[A-Z0-9]{4,20}'
        batches = re.findall(batch_pattern, text)
        if batches:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def extract_text_from_file(self, image_file) -> str:
        """
        Extract text from uploaded image file
        Returns extracted text
        """
        try:
            # Read image from file
            image_data = image_file.read()
            image = Image.open(io.BytesIO(image_data))
            
            # Convert PIL image to numpy array
            image_array = np.array(image)
            
            # Convert RGB to BGR for OpenCV
            if len(image_array.shape) == 3 and image_array.shape[2] == 3:
                image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
            
            # Extract text
            return self.extract_text(image_array, preprocess=True)
        except Exception as e:
            print(f"Error extracting text from file: {e}")
            return ""

def extract_medicine_info_from_image(image_file) -> Dict[str, Any]:
    """
    Standalone function to extract medicine info from image file
    """
    ocr_service = OCRService()
    image_data = image_file.read()
    image = Image.open(io.BytesIO(image_data))
    image_array = np.array(image)
    
    if len(image_array.shape) == 3 and image_array.shape[2] == 3:
        image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
    
    return ocr_service.extract_medicine_info(image_array)



