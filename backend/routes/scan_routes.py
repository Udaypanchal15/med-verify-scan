from flask import Blueprint, request, jsonify
from middleware.auth import login_required
from services.qr_signer import verify_qr_signature
from services.ai_service import get_ai_service
from services.ocr_service import extract_medicine_info_from_image
from database.models import ScanLog, Medicine, Seller, RevokedKeys
from database import execute_query
import os, json

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
