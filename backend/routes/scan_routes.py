from flask import Blueprint, request, jsonify
from middleware.auth import login_required
from services.qr_signer import verify_qr_signature
from services.ai_service import get_ai_service
from services.ocr_service import extract_medicine_info_from_image
from database.models import ScanLog, Medicine, Seller, RevokedKeys, QRCode
from database import execute_query
import os, json
try:
    from pyzbar import pyzbar
    QR_DECODE_AVAILABLE = True
except ImportError:
    QR_DECODE_AVAILABLE = False
    print("[Warning] pyzbar not installed. QR code image scanning will be limited.")

import cv2
import numpy as np
from PIL import Image
import io

scan_bp = Blueprint('scan_bp', __name__, url_prefix='/scan')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@scan_bp.route('', methods=['POST'])
@login_required
def scan_qr(current_user, user_id):
    """QR Scan without blockchain"""
    try:
        data = request.get_json()
        qr_data = data.get('qr_data')

        if isinstance(qr_data, str):
            try:
                qr_data = json.loads(qr_data)
            except:
                return jsonify({"error": "Invalid QR JSON"}), 400

        if not qr_data:
            return jsonify({"error": "QR data missing"}), 400

        signature = qr_data.get('signature')
        payload_data = {k: v for k, v in qr_data.items() if k != 'signature'}

        if not signature:
            return jsonify({"error": "Missing signature"}), 400

        seller_id = payload_data.get('seller_id')
        if not seller_id:
            return jsonify({"error": "Missing seller_id"}), 400

        seller = Seller.get_by_id(seller_id)
        if not seller:
            return jsonify({"error": "Seller not found"}), 404

        public_key_pem = seller.get('public_key')
        if not public_key_pem:
            return jsonify({"error": "Seller public key missing"}), 400

        if RevokedKeys.is_revoked(public_key_pem):
            result_status = "revoked"
            verified = False
        else:
            signature_valid = verify_qr_signature(payload_data, signature, public_key_pem)
            verified = signature_valid
            result_status = "verified" if signature_valid else "counterfeit"

        # Medicine Lookup
        medicine = None
        ai_summary = None
        if payload_data.get('medicine_id'):
            medicine = Medicine.get_by_id(payload_data['medicine_id'])
            if medicine:
                # Check if medicine is approved
                if medicine.get('approval_status') != 'approved':
                    return jsonify({
                        "error": "Medicine not verified by this platform. Use at your own risk.",
                        "warning": True,
                        "data": {
                            "verified": False,
                            "result": "unverified",
                            "medicine": medicine,
                            "message": "This medicine has not been verified by our platform."
                        }
                    }), 200
                try:
                    ai_service = get_ai_service()
                    ai_summary = ai_service.get_medicine_ai_summary({
                        "name": medicine.get("name"),
                        "dosage": medicine.get("dosage"),
                        "strength": medicine.get("strength"),
                        "description": medicine.get("description")
                    })
                except:
                    ai_summary = None

        # OCR (optional image)
        ocr_result = None
        if "file" in request.files:
            file = request.files["file"]
            if file.filename and allowed_file(file.filename):
                file.seek(0)
                ocr_result = extract_medicine_info_from_image(file)

        # Log Scan
        ScanLog.create(
            user_id=user_id,
            qr_id=None,
            raw_payload=json.dumps(qr_data),
            result=result_status,
            details={"signature_valid": verified},
            ip_address=request.remote_addr,
            user_agent=request.headers.get("User-Agent")
        )

        return jsonify({
            "message": "QR scanned",
            "data": {
                "verified": verified,
                "result": result_status,
                "medicine": medicine,
                "seller": {
                    "id": str(seller['id']),
                    "company_name": seller.get('company_name'),
                    "status": seller.get('status')
                },
                "ai_summary": ai_summary.get("summary") if ai_summary else None,
                "ocr_result": ocr_result,
                "blockchain": None  # <== REMOVED WEB3 ENTIRELY
            }
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@scan_bp.route('/verify-qr/<qr_id>', methods=['GET'])
@login_required
def verify_qr_by_id(current_user, user_id, qr_id):
    """Verify a QR code by its ID and return medicine information"""
    try:
        # Get QR code from database
        qr_code = QRCode.get_by_id(qr_id)
        if not qr_code:
            return jsonify({"error": "QR code not found"}), 404
        
        # Get medicine information
        medicine = Medicine.get_by_id(qr_code.get('medicine_id'))
        if not medicine:
            return jsonify({"error": "Medicine not found"}), 404
        
        # Get seller information
        seller = Seller.get_by_id(medicine['seller_id'])
        if not seller:
            return jsonify({"error": "Seller not found"}), 404
        
        # Get payload
        payload = qr_code.get('payload_json')
        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except:
                payload = {}
        
        # Check if medicine is approved
        if medicine.get('approval_status') != 'approved':
            return jsonify({
                "error": "Medicine not verified by this platform. Use at your own risk.",
                "warning": True,
                "data": {
                    "verified": False,
                    "result": "unverified",
                    "qr_id": qr_id,
                    "medicine": medicine,
                    "seller": {
                        "id": str(seller['id']),
                        "company_name": seller.get('company_name'),
                        "status": seller.get('status')
                    },
                    "payload": payload,
                    "message": "This medicine has not been verified by our platform."
                }
            }), 200
        
        # Get AI summary
        ai_summary = None
        try:
            ai_service = get_ai_service()
            ai_summary = ai_service.get_medicine_ai_summary({
                "name": medicine.get("name"),
                "dosage": medicine.get("dosage"),
                "strength": medicine.get("strength"),
                "description": medicine.get("description")
            })
        except:
            ai_summary = None
        
        # Log scan
        ScanLog.create(
            user_id=user_id,
            qr_id=qr_id,
            raw_payload=json.dumps(payload) if payload else None,
            result="verified",
            details={"qr_verified": True},
            ip_address=request.remote_addr,
            user_agent=request.headers.get("User-Agent")
        )
        
        return jsonify({
            "message": "QR verified successfully",
            "data": {
                "verified": True,
                "result": "verified",
                "qr_id": qr_id,
                "medicine": {
                    "id": str(medicine['id']),
                    "name": medicine.get('name'),
                    "batch_no": medicine.get('batch_no'),
                    "manufacturer": medicine.get('manufacturer'),
                    "category": medicine.get('category'),
                    "dosage": medicine.get('dosage'),
                    "strength": medicine.get('strength'),
                    "description": medicine.get('description'),
                    "usage": medicine.get('usage'),
                    "mfg_date": str(medicine.get('mfg_date')) if medicine.get('mfg_date') else None,
                    "expiry_date": str(medicine.get('expiry_date')) if medicine.get('expiry_date') else None,
                    "approval_status": medicine.get('approval_status')
                },
                "seller": {
                    "id": str(seller['id']),
                    "company_name": seller.get('company_name'),
                    "status": seller.get('status')
                },
                "ai_summary": ai_summary.get("summary") if ai_summary else None,
                "payload": payload
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@scan_bp.route('/image', methods=['POST'])
def scan_image():
    """Scan QR code from uploaded image"""
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        
        if not file or file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({"error": "Invalid file type. Allowed: png, jpg, jpeg, gif"}), 400
        
        # Check file size
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({"error": "File too large. Max 5MB"}), 400
        
        try:
            # Read and decode image
            image_data = file.read()
            image = Image.open(io.BytesIO(image_data))
            image_array = np.array(image)
            
            # Convert RGB to BGR for OpenCV if needed
            if len(image_array.shape) == 3 and image_array.shape[2] == 3:
                image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
            
            qr_data_found = None
            
            # Try to decode QR code from image
            if QR_DECODE_AVAILABLE:
                try:
                    decoded_objects = pyzbar.decode(image_array)
                    if decoded_objects:
                        qr_data_found = decoded_objects[0].data.decode('utf-8')
                except Exception as qr_error:
                    print(f"[QR Decode Error] {str(qr_error)}")
            
            if not qr_data_found:
                return jsonify({"error": "No QR code found in image. Make sure the QR code is clear and properly positioned."}), 400
            
            # Try to parse QR result as JSON (for seller-generated QR codes)
            qr_data = None
            try:
                qr_data = json.loads(qr_data_found)
            except:
                pass
            
            # If QR data contains qr_id, verify using that
            if qr_data and qr_data.get('qr_id'):
                qr_code = QRCode.get_by_id(qr_data.get('qr_id'))
                if not qr_code:
                    return jsonify({"error": "QR code not found in database"}), 404
                
                medicine = Medicine.get_by_id(qr_code.get('medicine_id'))
                if not medicine:
                    return jsonify({"error": "Medicine not found"}), 404
                
                return jsonify({
                    "message": "QR code scanned successfully",
                    "name": medicine.get('name'),
                    "manufacturer": medicine.get('manufacturer'),
                    "batch_number": medicine.get('batch_no'),
                    "manufacture_date": str(medicine.get('mfg_date')) if medicine.get('mfg_date') else None,
                    "expiry_date": str(medicine.get('expiry_date')) if medicine.get('expiry_date') else None,
                    "category": medicine.get('category'),
                    "dosage": medicine.get('dosage'),
                    "strength": medicine.get('strength'),
                    "description": medicine.get('description'),
                    "usage": medicine.get('usage'),
                    "qr_id": qr_data.get('qr_id')
                }), 200
            
            # If no valid QR data, return error
            return jsonify({"error": "QR code is not valid or unreadable"}), 400
            
        except Exception as ocr_error:
            print(f"[Image Processing Error] {str(ocr_error)}")
            import traceback
            traceback.print_exc()
            return jsonify({"error": f"Failed to process image: {str(ocr_error)}"}), 400
        
    except Exception as e:
        print(f"[Image Scan Error] {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
