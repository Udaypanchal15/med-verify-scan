# AI Services Guide

## Overview

The AI services provide OCR, image verification, and LLM summarization capabilities for medicine verification. These services enhance the security and user experience of the medicine verification system.

## Components

### 1. OCR Service (`ocr_service.py`)

Extracts text from medicine packaging images using pytesseract with OpenCV preprocessing.

#### Features

- **Image Preprocessing**: Grayscale conversion, noise reduction, contrast enhancement, thresholding
- **Text Extraction**: Extract text from images using OCR
- **Medicine Information Parsing**: Parse extracted text to find medicine name, batch number, dates, dosage, etc.
- **Confidence Scoring**: Calculate confidence score based on extracted text quality

#### Usage

```python
from services.ocr_service import OCRService

# Initialize OCR service
ocr_service = OCRService()

# Extract text from image
text = ocr_service.extract_text(image_array)

# Extract medicine information
info = ocr_service.extract_medicine_info(image_array)

# From file
info = extract_medicine_info_from_image(image_file)
```

#### Output

```python
{
    "raw_text": "Extracted text from image...",
    "parsed_info": {
        "medicine_name": "Paracetamol",
        "batch_number": "BATCH001",
        "manufacture_date": "2024-01-01",
        "expiry_date": "2026-01-01",
        "dosage": "500mg",
        "strength": "500mg",
        "manufacturer": "PharmaCorp Ltd"
    },
    "confidence": 0.85
}
```

### 2. Image Verification Service (`image_verification.py`)

Verifies medicine packaging images using deep learning models (MobileNet/ResNet).

#### Features

- **Feature Extraction**: Extract features from images using pre-trained CNN models
- **Image Similarity**: Compare images using cosine similarity
- **Golden Image Storage**: Store reference images for verification
- **Threshold-based Verification**: Verify images against golden images with configurable threshold

#### Usage

```python
from services.image_verification import ImageVerificationService

# Initialize service
image_verification = ImageVerificationService(model_type='mobilenet')

# Add golden image
image_verification.add_golden_image("medicine-123", golden_image_array)

# Verify image
result = image_verification.verify_medicine_image(
    test_image_array, 
    "medicine-123", 
    threshold=0.85
)

# Compare two images
similarity = image_verification.compare_images(image1, image2)
```

#### Output

```python
{
    "matches": True,
    "similarity": 0.92,
    "threshold": 0.85,
    "confidence": 92.0
}
```

### 3. LLM Service (`llm_service.py`)

Generates AI summaries of medicine information using OpenAI API or fallback knowledge base.

#### Features

- **Medicine Summarization**: Generate structured summaries of medicine information
- **Side Effects**: List common side effects
- **Drug Interactions**: Identify important drug interactions
- **Contraindications**: List contraindications
- **Dosage Instructions**: Provide dosage instructions
- **Fallback Support**: Use knowledge base when LLM is unavailable

#### Usage

```python
from services.llm_service import LLMService

# Initialize service
llm_service = LLMService(api_key="your-api-key", model="gpt-3.5-turbo")

# Generate summary
medicine_data = {
    "name": "Paracetamol",
    "dosage": "500mg",
    "strength": "500mg",
    "description": "Pain reliever"
}

summary = llm_service.summarize_medicine_info(medicine_data)
text_summary = llm_service.generate_ai_summary(medicine_data)
```

#### Output

```python
{
    "description": "Paracetamol is a common pain reliever...",
    "side_effects": ["Nausea", "Rash", "Headache"],
    "drug_interactions": ["Avoid alcohol", "Avoid other hepatotoxic drugs"],
    "contraindications": ["Severe liver disease", "Allergy to paracetamol"],
    "dosage_instructions": "500mg every 4-6 hours, max 4g per day",
    "source": "llm",
    "medicine_name": "Paracetamol",
    "model": "gpt-3.5-turbo"
}
```

### 4. Unified AI Service (`ai_service.py`)

Integrates all AI services into a single unified interface.

#### Features

- **Package Verification**: Combine OCR and image verification
- **Medicine Summarization**: Generate AI summaries
- **Text Extraction**: Extract text from images
- **Image Similarity**: Compare images

#### Usage

```python
from services.ai_service import get_ai_service

# Get AI service instance
ai_service = get_ai_service()

# Verify medicine package
result = ai_service.verify_medicine_package(
    image_file,
    medicine_id="medicine-123",
    golden_image_path="./golden_images/medicine-123.jpg"
)

# Get AI summary
summary = ai_service.get_medicine_ai_summary(medicine_data)

# Extract text
text = ai_service.extract_text_from_image(image_file)

# Verify image similarity
similarity = ai_service.verify_image_similarity(image1_file, image2_file)
```

## Setup

### 1. Install Dependencies

```bash
pip install pytesseract opencv-python tensorflow scikit-learn openai pillow numpy
```

### 2. Install Tesseract OCR

#### Windows
1. Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
2. Install and add to PATH
3. Set `TESSERACT_CMD` environment variable

#### Linux
```bash
sudo apt-get install tesseract-ocr
```

#### macOS
```bash
brew install tesseract
```

### 3. Configure OpenAI API

Add to `.env`:
```env
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-3.5-turbo
```

### 4. Configure Tesseract

Add to `.env`:
```env
TESSERACT_CMD=/usr/bin/tesseract  # Linux/Mac
# TESSERACT_CMD=C:\\Program Files\\Tesseract-OCR\\tesseract.exe  # Windows
```

## API Integration

### OCR Endpoint

```python
# POST /ai/ocr
{
    "image": "<base64_encoded_image>"
}

# Response
{
    "raw_text": "...",
    "parsed_info": {...},
    "confidence": 0.85
}
```

### Image Verification Endpoint

```python
# POST /ai/verify-image
{
    "image": "<base64_encoded_image>",
    "medicine_id": "medicine-123"
}

# Response
{
    "matches": true,
    "similarity": 0.92,
    "confidence": 92.0
}
```

### LLM Summary Endpoint

```python
# POST /ai/summarize
{
    "medicine_data": {
        "name": "Paracetamol",
        "dosage": "500mg"
    }
}

# Response
{
    "summary": {...},
    "text_summary": "...",
    "source": "llm"
}
```

## Best Practices

### OCR

1. **Image Quality**: Use high-resolution images for better OCR accuracy
2. **Preprocessing**: Always use preprocessing for better results
3. **Lighting**: Ensure good lighting when capturing images
4. **Angle**: Capture images straight-on for best results
5. **Confidence Threshold**: Use confidence scores to filter low-quality results

### Image Verification

1. **Golden Images**: Use high-quality reference images
2. **Threshold**: Adjust threshold based on use case (0.85 default)
3. **Model Selection**: Use MobileNet for speed, ResNet for accuracy
4. **Storage**: Save golden images for faster verification
5. **Updates**: Update golden images when packaging changes

### LLM

1. **API Key**: Keep API key secure
2. **Rate Limiting**: Implement rate limiting for API calls
3. **Fallback**: Always have fallback knowledge base
4. **Caching**: Cache summaries for frequently accessed medicines
5. **Validation**: Validate LLM responses before using

## Troubleshooting

### OCR Issues

- **Low Accuracy**: Improve image quality, adjust preprocessing
- **Missing Text**: Check image resolution, lighting
- **Wrong Parsing**: Adjust regex patterns in `parse_medicine_text`

### Image Verification Issues

- **Low Similarity**: Check image quality, adjust threshold
- **Model Loading**: Ensure TensorFlow is installed correctly
- **Memory Issues**: Use MobileNet for lower memory usage

### LLM Issues

- **API Errors**: Check API key, rate limits
- **Timeout**: Increase timeout, use fallback
- **Cost**: Monitor API usage, use caching

## Performance

### OCR
- Processing time: ~1-3 seconds per image
- Accuracy: ~85-95% with good images
- Memory: Low (~100MB)

### Image Verification
- Processing time: ~0.5-1 second per image (MobileNet)
- Accuracy: ~90-95% similarity detection
- Memory: Medium (~500MB with MobileNet, ~1GB with ResNet)

### LLM
- Processing time: ~2-5 seconds per request
- Accuracy: High (depends on model)
- Cost: ~$0.002 per request (GPT-3.5-turbo)

## Security

1. **API Keys**: Store securely, never commit to version control
2. **Image Data**: Sanitize image data before processing
3. **Rate Limiting**: Implement rate limiting for AI services
4. **Validation**: Validate all AI service outputs
5. **Fallbacks**: Always have fallback mechanisms

## References

- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- [OpenCV Documentation](https://docs.opencv.org/)
- [TensorFlow Documentation](https://www.tensorflow.org/)
- [OpenAI API Documentation](https://platform.openai.com/docs/)



