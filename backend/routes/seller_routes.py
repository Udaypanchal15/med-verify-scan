"""
Seller routes for KYC, medicine management, and QR code issuance
"""
from flask import Blueprint, request, jsonify
from middleware.auth import login_required, seller_required, admin_or_seller_required
from database.models import Seller, Medicine, QRCode, User
from services.qr_service import QRCodeService
from services.qr_signer import QRCodeSigner, generate_key_pair_files
from services.ai_service import get_ai_service
from services.seller_notification_service import get_seller_notification_service
from werkzeug.utils import secure_filename
import os
import uuid
import hashlib
import json
from datetime import datetime, timezone

seller_bp = Blueprint('seller_bp', __name__, url_prefix='/seller')

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
ALLOWED_FILE_TYPES = {'image/png', 'image/jpeg', 'application/pdf'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB per file
MAX_FILES = 5  # Maximum 5 files per application

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def compute_sha256(file_obj):
    """Compute SHA256 checksum of file"""
    hasher = hashlib.sha256()
    while True:
        chunk = file_obj.read(8192)
        if not chunk:
            break
        hasher.update(chunk)
    return hasher.hexdigest()

def validate_documents(files_list):
    """Validate documents for upload
    Returns tuple: (is_valid, error_message, processed_files)
    """
    if not files_list or len(files_list) == 0:
        return True, None, []  # Documents optional
    
    if len(files_list) > MAX_FILES:
        return False, f"Maximum {MAX_FILES} files allowed", []
    
    processed = []
    for file in files_list:
        if not file.filename:
            continue
        
        if not allowed_file(file.filename):
            return False, f"File type not allowed: {file.filename}. Allowed: PDF, PNG, JPEG", []
        
        # Check file size
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)
        
        if size > MAX_FILE_SIZE:
            return False, f"File {file.filename} exceeds {MAX_FILE_SIZE / (1024*1024):.1f}MB limit", []
        
        processed.append(file)
    
    return True, None, processed

@seller_bp.route('/apply', methods=['POST'])
@login_required
def apply_kyc(current_user, user_id):
    """Apply for seller KYC with full KYC documents and metadata"""
    try:
        # Check if user is already a seller with active/pending status
        existing_seller = Seller.get_by_user_id(user_id)
        if existing_seller and existing_seller.get('status') in ['pending', 'viewed', 'verifying', 'approved']:
            return jsonify({
                "error": "Seller application already exists",
                "status": existing_seller.get('status')
            }), 400
        
        # Parse multipart form data
        company_name = request.form.get('company_name', '').strip()
        license_number = request.form.get('license_number', '').strip()
        license_type = request.form.get('license_type', '').strip()
        license_expiry = request.form.get('license_expiry', '').strip()
        gstin = request.form.get('gstin', '').strip()
        address = request.form.get('address', '').strip()
        authorized_person = request.form.get('authorized_person', '').strip()
        authorized_person_contact = request.form.get('authorized_person_contact', '').strip()
        email_company = request.form.get('email_company', '').strip()
        
        # Validate required fields
        required_fields = {
            'company_name': company_name,
            'license_number': license_number,
            'license_type': license_type,
            'license_expiry': license_expiry,
            'address': address,
            'authorized_person': authorized_person,
            'authorized_person_contact': authorized_person_contact,
            'email_company': email_company
        }
        
        missing_fields = [k for k, v in required_fields.items() if not v]
        if missing_fields:
            return jsonify({
                "error": "Missing required fields",
                "fields": missing_fields
            }), 400
        
        # Validate phone format (10 digits)
        if not authorized_person_contact.isdigit() or len(authorized_person_contact) != 10:
            return jsonify({
                "error": "Contact must be 10 digits"
            }), 400
        
        # Check duplicate license_number for this user
        # (A user can reapply with different/updated docs, but not duplicate active applications)
        # This check is already handled above with status check
        
        # Handle document uploads
        documents = request.files.getlist('documents')
        is_valid, error_msg, processed_files = validate_documents(documents)
        
        if not is_valid:
            return jsonify({"error": error_msg}), 400
        
        # Save files with checksums
        seller_id = str(uuid.uuid4())
        document_urls = []
        document_checksums = {}
        
        for file in processed_files:
            if not file.filename:
                continue
            
            # Create unique filename: {seller_id}_{uuid}_{original}
            filename = f"{seller_id}_{uuid.uuid4()}_{secure_filename(file.filename)}"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            
            # Compute checksum before saving
            file.seek(0)
            checksum = compute_sha256(file)
            
            # Save file
            file.seek(0)
            file.save(filepath)
            
            # Store URL and checksum
            doc_url = f"/uploads/{filename}"
            document_urls.append(doc_url)
            document_checksums[filename] = checksum
        
        # Create seller application with all KYC fields
        seller = Seller.create(
            user_id=user_id,
            company_name=company_name,
            license_number=license_number,
            license_type=license_type,
            license_expiry=license_expiry,
            gstin=gstin,
            address=address,
            authorized_person=authorized_person,
            authorized_person_contact=authorized_person_contact,
            email=email_company,
            documents=document_urls,
            document_checksums=document_checksums
        )
        
        if not seller:
            return jsonify({"error": "Failed to create seller application"}), 500
        
        # Send notification email
        try:
            user = User.get_by_id(user_id)
            notification_service = get_seller_notification_service()
            notification_service.notify_on_submission(seller, user)
        except Exception as e:
            print(f"Warning: Failed to send notification email: {e}")
        
        return jsonify({
            "message": "Seller application submitted successfully",
            "seller_id": seller.get('id'),
            "docs_stored_count": len(document_urls),
            "data": seller
        }), 201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@seller_bp.route('/status', methods=['GET'])
@login_required
def get_seller_status(current_user, user_id):
    """Get seller application status with full details and timestamps"""
    try:
        seller = Seller.get_by_user_id(user_id)
        if not seller:
            return jsonify({
                "error": "Seller application not found"
            }), 404
        
        # Return full seller details with timestamps and status
        seller_dict = dict(seller)
        
        return jsonify({
            "message": "Seller status retrieved successfully",
            "data": {
                "id": seller_dict.get('id'),
                "user_id": seller_dict.get('user_id'),
                "company_name": seller_dict.get('company_name'),
                "license_number": seller_dict.get('license_number'),
                "license_type": seller_dict.get('license_type'),
                "license_expiry": seller_dict.get('license_expiry'),
                "gstin": seller_dict.get('gstin'),
                "address": seller_dict.get('address'),
                "authorized_person": seller_dict.get('authorized_person'),
                "authorized_person_contact": seller_dict.get('authorized_person_contact'),
                "email": seller_dict.get('email'),
                "company_website": seller_dict.get('company_website'),
                "status": seller_dict.get('status'),
                "documents": seller_dict.get('documents'),
                "submitted_at": seller_dict.get('created_at'),
                "viewed_at": seller_dict.get('viewed_at'),
                "verifying_at": seller_dict.get('verifying_at'),
                "approved_at": seller_dict.get('approved_at'),
                "rejected_at": seller_dict.get('rejected_at'),
                "admin_remarks": seller_dict.get('admin_remarks'),
                "required_changes": seller_dict.get('required_changes'),
            }
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@seller_bp.route('/generate-keys', methods=['POST'])
@seller_required
def generate_keys(current_user, user_id):
    """Generate ECDSA key pair for seller"""
    try:
        seller = Seller.get_by_user_id(user_id)
        if not seller:
            return jsonify({"error": "Seller not found"}), 404
        
        if seller.get('status') != 'approved':
            return jsonify({"error": "Seller must be approved before generating keys"}), 403
        
        # Generate key pair
        keys_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'keys')
        os.makedirs(keys_dir, exist_ok=True)
        
        seller_id = str(seller['id'])
        private_key_path = os.path.join(keys_dir, f'seller_{seller_id}_private_key.pem')
        public_key_path = os.path.join(keys_dir, f'seller_{seller_id}_public_key.pem')
        
        success = generate_key_pair_files(private_key_path, public_key_path)
        
        if not success:
            return jsonify({"error": "Failed to generate keys"}), 500
        
        # Read public key
        with open(public_key_path, 'r') as f:
            public_key_pem = f.read()
        
        # Update seller with public key
        Seller.update_public_key(seller_id, public_key_pem)
        
        return jsonify({
            "message": "Keys generated successfully",
            "data": {
                "seller_id": seller_id,
                "public_key": public_key_pem,
                "private_key_path": private_key_path,
                "warning": "Keep private key secure and never share it"
            }
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@seller_bp.route('/medicine', methods=['POST'])
@seller_required
def create_medicine(current_user, user_id):
    """Create a new medicine"""
    try:
        seller = Seller.get_by_user_id(user_id)
        if not seller or seller.get('status') != 'approved':
            return jsonify({"error": "Seller not approved"}), 403
        
        seller_id = str(seller['id'])
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'batch_no', 'mfg_date', 'expiry_date']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"{field} is required"}), 400
        
        # Handle image upload
        image_url = None
        if 'image' in request.files:
            file = request.files['image']
            if file.filename and allowed_file(file.filename):
                filename = f"{seller_id}_{uuid.uuid4()}_{secure_filename(file.filename)}"
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                image_url = f"/uploads/{filename}"
        
        # Get stock quantity and delivery status with defaults
        stock_quantity = int(data.get('stock_quantity', 0))
        delivery_status = data.get('delivery_status', 'in_stock')
        
        # Validate delivery status
        valid_statuses = ['in_stock', 'pending', 'delivered', 'discontinued']
        if delivery_status not in valid_statuses:
            return jsonify({"error": f"Invalid delivery_status. Must be one of: {', '.join(valid_statuses)}"}), 400
        
        # Create medicine
        medicine = Medicine.create(
            seller_id=seller_id,
            name=data.get('name'),
            batch_no=data.get('batch_no'),
            mfg_date=data.get('mfg_date'),
            expiry_date=data.get('expiry_date'),
            dosage=data.get('dosage'),
            strength=data.get('strength'),
            category=data.get('category'),
            description=data.get('description'),
            image_url=image_url,
            stock_quantity=stock_quantity,
            delivery_status=delivery_status
        )
        
        if not medicine:
            return jsonify({"error": "Failed to create medicine"}), 500
        
        # Add golden image for verification if image provided
        if image_url and 'image' in request.files:
            try:
                ai_service = get_ai_service()
                file.seek(0)  # Reset file pointer
                ai_service.add_golden_image(str(medicine['id']), file)
            except Exception as e:
                print(f"Warning: Failed to add golden image: {e}")
        
        return jsonify({
            "message": "Medicine created successfully",
            "data": medicine
        }), 201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@seller_bp.route('/medicine', methods=['GET'])
@seller_required
def get_medicines(current_user, user_id):
    """Get all medicines for seller"""
    try:
        seller = Seller.get_by_user_id(user_id)
        if not seller:
            return jsonify({"error": "Seller not found"}), 404
        
        seller_id = str(seller['id'])
        medicines = Medicine.get_by_seller(seller_id)
        
        return jsonify({
            "message": "Medicines retrieved successfully",
            "data": medicines
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@seller_bp.route('/medicine/<medicine_id>', methods=['GET'])
@seller_required
def get_medicine(current_user, user_id, medicine_id):
    """Get medicine by ID"""
    try:
        medicine = Medicine.get_by_id(medicine_id)
        if not medicine:
            return jsonify({"error": "Medicine not found"}), 404
        
        # Verify seller owns this medicine
        seller = Seller.get_by_user_id(user_id)
        if str(medicine['seller_id']) != str(seller['id']):
            return jsonify({"error": "Unauthorized"}), 403
        
        return jsonify({
            "message": "Medicine retrieved successfully",
            "data": medicine
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@seller_bp.route('/medicine/<medicine_id>', methods=['PUT'])
@seller_required
def update_medicine(current_user, user_id, medicine_id):
    """Update medicine"""
    try:
        medicine = Medicine.get_by_id(medicine_id)
        if not medicine:
            return jsonify({"error": "Medicine not found"}), 404, {'Content-Type': 'application/json'}

        # Verify seller owns this medicine
        seller = Seller.get_by_user_id(user_id)
        if str(medicine['seller_id']) != str(seller['id']):
            return jsonify({"error": "Unauthorized"}), 403, {'Content-Type': 'application/json'}

        data = request.get_json()

        # Update medicine using the new update method
        updated_medicine = Medicine.update(medicine_id, **data)

        if not updated_medicine:
            return jsonify({"error": "Failed to update medicine"}), 500, {'Content-Type': 'application/json'}

        return jsonify({
            "message": "Medicine updated successfully",
            "medicine": updated_medicine
        }), 200, {'Content-Type': 'application/json'}

    except Exception as e:
        return jsonify({"error": str(e)}), 500, {'Content-Type': 'application/json'}

@seller_bp.route('/issue-qr', methods=['POST'])
@seller_required
def issue_qr(current_user, user_id):
    """Issue signed QR code for medicine with optional batch details"""
    try:
        seller = Seller.get_by_user_id(user_id)
        if not seller or seller.get('status') != 'approved':
            return jsonify({"error": "Seller not approved"}), 403
        
        seller_id = str(seller['id'])
        data = request.get_json()
        medicine_id = data.get('medicine_id')
        batch_details = data.get('batch_details', '')  # Optional batch/box details
        
        if not medicine_id:
            return jsonify({"error": "Medicine ID is required"}), 400
        
        # Verify medicine belongs to seller
        medicine = Medicine.get_by_id(medicine_id)
        if not medicine or str(medicine['seller_id']) != seller_id:
            return jsonify({"error": "Medicine not found or unauthorized"}), 404
        
        # Get seller's private key path
        keys_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'keys')
        private_key_path = os.path.join(keys_dir, f'seller_{seller_id}_private_key.pem')
        
        if not os.path.exists(private_key_path):
            return jsonify({"error": "Private key not found. Please generate keys first."}), 400
        
        # Create QR code service with seller's private key
        qr_service = QRCodeService(seller_private_key_path=private_key_path)
        
        # Prepare QR data with batch details
        qr_payload = {
            "medicine_id": medicine_id,
            "seller_id": seller_id,
            "issued_by": user_id,
            "medicine_name": medicine.get('name'),
            "batch_no": medicine.get('batch_no'),
            "batch_details": batch_details,  # Include additional batch/box details
            "issued_at": datetime.now().isoformat()
        }
        
        # Issue QR code
        qr_code = qr_service.create_signed_qr(
            medicine_id=medicine_id,
            seller_id=seller_id,
            issued_by=user_id,
            additional_data=qr_payload
        )
        
        return jsonify({
            "message": "QR code issued successfully",
            "data": qr_code
        }), 201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@seller_bp.route('/history', methods=['GET'])
@seller_required
def get_issuance_history(current_user, user_id):
    """Get QR code issuance history for seller"""
    try:
        seller = Seller.get_by_user_id(user_id)
        if not seller:
            return jsonify({"error": "Seller not found"}), 404
        
        seller_id = str(seller['id'])
        
        # Get all medicines for seller
        medicines = Medicine.get_by_seller(seller_id)
        medicine_ids = [str(m['id']) for m in medicines]
        
        # Get QR codes for these medicines (simplified - would need proper query)
        # For now, return medicines with QR code count
        result = []
        for medicine in medicines:
            # Count QR codes (simplified)
            result.append({
                "medicine": medicine,
                "qr_count": 0  # Would need to query QR codes
            })
        
        return jsonify({
            "message": "Issuance history retrieved successfully",
            "data": result
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500



