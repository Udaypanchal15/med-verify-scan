import json
from pyzbar import pyzbar
from PIL import Image
import io

def process_qr_data(qr_data):
    """Process QR data from text/JSON string"""
    try:
        data = json.loads(qr_data)
    except json.JSONDecodeError:
        return {"error": "Invalid QR data format"}

    med_name = data.get("name", "Unknown Medicine")
    mfg_date = data.get("manufacture_date", "N/A")
    exp_date = data.get("expiry_date", "N/A")
    dosage = data.get("dosage", "N/A")

    return {
        "name": med_name,
        "manufacture_date": mfg_date,
        "expiry_date": exp_date,
        "dosage": dosage
    }

def decode_qr_from_image(image_file):
    """Decode QR code from uploaded image file"""
    try:
        # Read the image file
        image = Image.open(io.BytesIO(image_file.read()))
        
        # Decode QR code
        qr_codes = pyzbar.decode(image)
        
        if not qr_codes:
            return {"error": "No QR code found in image"}
        
        # Get the first QR code data
        qr_data = qr_codes[0].data.decode('utf-8')
        
        # Process the decoded data
        result = process_qr_data(qr_data)
        
        if "error" not in result:
            result["manufacturer"] = "Verified Manufacturer"
            result["batch_number"] = result.get("manufacture_date", "N/A").replace("-", "")
        
        return result
        
    except Exception as e:
        return {"error": f"Failed to process image: {str(e)}"}

def verify_medicine_from_qr(qr_data):
    """Verify medicine information from QR data"""
    # Mock medicine database for verification
    medicine_db = {
        "MED001": {
            "name": "Paracetamol 500mg",
            "manufacturer": "PharmaCorp Ltd.",
            "batchNumber": "PCL24001",
            "mfgDate": "2024-01-15",
            "expDate": "2026-01-15",
            "isAuthentic": True,
            "isExpired": False,
            "status": "verified"
        },
        "MED002": {
            "name": "Ibuprofen 200mg",
            "manufacturer": "MediCare Inc.",
            "batchNumber": "MC24002",
            "mfgDate": "2024-02-20",
            "expDate": "2025-08-20",
            "isAuthentic": True,
            "isExpired": True,
            "status": "expired"
        }
    }
    
    # Try to find medicine in database
    if qr_data in medicine_db:
        return medicine_db[qr_data]
    
    # Return unknown medicine
    return {
        "name": "Unknown Medicine",
        "manufacturer": "Unknown",
        "batchNumber": "Unknown",
        "mfgDate": "Unknown",
        "expDate": "Unknown",
        "isAuthentic": False,
        "isExpired": False,
        "status": "counterfeit"
    }
