"""
Seller routes for KYC, medicine management, and QR code issuance
"""
from flask import Blueprint, request, jsonify, send_file
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
from io import BytesIO
import base64

# Try importing QR code libraries
try:
    import qrcode
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False
    print("[WARNING] qrcode library not installed. QR code image generation will be disabled.")

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("[WARNING] reportlab library not installed. PDF generation will be disabled.")

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

@seller_bp.route('/generate-keys', methods=['POST', 'OPTIONS'])
@seller_required
def generate_keys(current_user, user_id):
    """Generate ECDSA key pair for seller"""
    try:
        seller = Seller.get_by_user_id(user_id)
        if not seller:
            return jsonify({"error": "Seller not found"}), 404, {'Content-Type': 'application/json'}

        if seller.get('status') != 'approved':
            return jsonify({"error": "Seller must be approved before generating keys"}), 403, {'Content-Type': 'application/json'}
        
        # Generate key pair
        keys_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'keys')
        os.makedirs(keys_dir, exist_ok=True)
        
        seller_id = str(seller['id'])
        private_key_path = os.path.join(keys_dir, f'seller_{seller_id}_private_key.pem')
        public_key_path = os.path.join(keys_dir, f'seller_{seller_id}_public_key.pem')
        
        success = generate_key_pair_files(private_key_path, public_key_path)

        if not success:
            return jsonify({"error": "Failed to generate keys"}), 500, {'Content-Type': 'application/json'}

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
        }), 200, {'Content-Type': 'application/json'}

    except Exception as e:
        return jsonify({"error": str(e)}), 500, {'Content-Type': 'application/json'}

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

@seller_bp.route('/medicine/<medicine_id>', methods=['PUT', 'OPTIONS'])
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

@seller_bp.route('/issue-qr', methods=['POST', 'OPTIONS'])
@seller_required
def issue_qr(current_user, user_id):
    """Issue QR code for medicine with optional batch details"""
    try:
        print(f"[QR Generation] Starting for user_id: {user_id}")

        seller = Seller.get_by_user_id(user_id)
        if not seller or seller.get('status') != 'approved':
            return jsonify({"error": "Seller not approved"}), 403, {'Content-Type': 'application/json'}

        seller_id = str(seller['id'])
        print(f"[QR Generation] Seller ID: {seller_id}")

        data = request.get_json()
        medicine_id = data.get('medicine_id')
        batch_details = data.get('batch_details', '')

        print(f"[QR Generation] Medicine ID: {medicine_id}")

        if not medicine_id:
            return jsonify({"error": "Medicine ID is required"}), 400, {'Content-Type': 'application/json'}

        # Verify medicine belongs to seller
        medicine = Medicine.get_by_id(medicine_id)
        print(f"[QR Generation] Medicine found: {medicine.get('name') if medicine else 'None'}")

        if not medicine or str(medicine['seller_id']) != seller_id:
            return jsonify({"error": "Medicine not found or unauthorized"}), 404, {'Content-Type': 'application/json'}

        # Create payload for QR code
        payload = {
            "medicine_id": medicine_id,
            "seller_id": seller_id,
            "medicine_name": medicine.get('name'),
            "batch_no": medicine.get('batch_no'),
            "batch_details": batch_details,
            "mfg_date": str(medicine.get('mfg_date')) if medicine.get('mfg_date') else None,
            "expiry_date": str(medicine.get('expiry_date')) if medicine.get('expiry_date') else None,
            "issued_at": datetime.now(timezone.utc).isoformat()
        }

        print(f"[QR Generation] Payload created: {json.dumps(payload, default=str)}")

        # Create QR code without signature (simplified version)
        print(f"[QR Generation] Calling QRCode.create()...")
        qr_code_db = QRCode.create(
            medicine_id=medicine_id,
            payload_json=payload,
            signature="",  # No signature for simplified version
            blockchain_tx=None,
            issued_by=user_id
        )

        print(f"[QR Generation] QR Code created in DB: {qr_code_db}")

        # Generate QR code image
        if not QRCODE_AVAILABLE:
            print("[QR Generation] qrcode library not available, returning without image")
            return jsonify({
                "message": "QR code generated successfully (install 'qrcode' library for image generation)",
                "data": {
                    "qr_id": str(qr_code_db['id']),
                    "payload": payload,
                    "medicine_name": medicine.get('name'),
                    "batch_no": medicine.get('batch_no')
                }
            }), 201, {'Content-Type': 'application/json'}

        try:
            print(f"[QR Generation] qrcode module available, generating image...")

            # Create QR code data string
            qr_data = json.dumps(payload)
            print(f"[QR Generation] QR data prepared: {len(qr_data)} bytes")

            # Generate QR code image
            print(f"[QR Generation] Creating QR code object...")
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            print(f"[QR Generation] QR object created, adding data...")
            qr.add_data(qr_data)
            qr.make(fit=True)
            print(f"[QR Generation] QR data processed, creating image...")

            # Create image
            img = qr.make_image(fill_color="black", back_color="white")
            print(f"[QR Generation] Image created, converting to base64...")

            # Convert to base64
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()

            print(f"[QR Generation] QR image generated successfully ({len(img_str)} bytes base64)")

            return jsonify({
                "message": "QR code generated successfully",
                "data": {
                    "qr_id": str(qr_code_db['id']),
                    "qr_image": f"data:image/png;base64,{img_str}",
                    "payload": payload,
                    "medicine_name": medicine.get('name'),
                    "batch_no": medicine.get('batch_no'),
                    "expiry_date": str(medicine.get('expiry_date')) if medicine.get('expiry_date') else None
                }
            }), 201, {'Content-Type': 'application/json'}

        except Exception as qr_error:
            print(f"[QR Generation] Error during image generation: {type(qr_error).__name__}: {str(qr_error)}")
            import traceback
            traceback.print_exc()
            # Still return QR code data without image on error
            return jsonify({
                "message": "QR code generated (image generation failed)",
                "data": {
                    "qr_id": str(qr_code_db['id']),
                    "payload": payload,
                    "medicine_name": medicine.get('name'),
                    "batch_no": medicine.get('batch_no'),
                    "image_error": str(qr_error)
                }
            }), 201, {'Content-Type': 'application/json'}

    except Exception as e:
        print(f"[QR Generation ERROR] {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500, {'Content-Type': 'application/json'}

@seller_bp.route('/qr/<qr_id>/download', methods=['GET'])
@seller_required
def download_qr_code(current_user, user_id, qr_id):
    """Download QR code as PNG image"""
    try:
        if not QRCODE_AVAILABLE:
            return jsonify({"error": "qrcode library not installed"}), 500
        
        # Get QR code from database
        qr_code = QRCode.get_by_id(qr_id)
        if not qr_code:
            return jsonify({"error": "QR code not found"}), 404
        
        # Verify seller owns this QR code
        seller = Seller.get_by_user_id(user_id)
        medicine = Medicine.get_by_id(qr_code.get('medicine_id'))
        
        if str(medicine['seller_id']) != str(seller['id']):
            return jsonify({"error": "Unauthorized"}), 403
        
        # Get payload
        payload = qr_code.get('payload_json')
        if isinstance(payload, str):
            payload = json.loads(payload)
        
        # Generate QR code image
        qr_data = json.dumps(payload)
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to bytes
        img_io = BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        
        # Return as downloadable file
        medicine_name = medicine.get('name', 'medicine').replace(' ', '_')
        batch_no = medicine.get('batch_no', 'batch').replace(' ', '_')
        filename = f"QR_{medicine_name}_{batch_no}_{qr_id[:8]}.png"
        
        return send_file(
            img_io,
            mimetype='image/png',
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@seller_bp.route('/qr/<qr_id>/download-pdf', methods=['GET'])
@seller_required
def download_qr_pdf(current_user, user_id, qr_id):
    """Download QR code as PDF (for printing)"""
    try:
        if not QRCODE_AVAILABLE:
            return jsonify({"error": "qrcode library not installed"}), 500
        
        if not PDF_AVAILABLE:
            return jsonify({"error": "PDF generation requires reportlab library"}), 500
        
        # Get QR code from database
        qr_code = QRCode.get_by_id(qr_id)
        if not qr_code:
            return jsonify({"error": "QR code not found"}), 404
        
        # Verify seller owns this QR code
        seller = Seller.get_by_user_id(user_id)
        medicine = Medicine.get_by_id(qr_code.get('medicine_id'))
        
        if str(medicine['seller_id']) != str(seller['id']):
            return jsonify({"error": "Unauthorized"}), 403
        
        # Get payload
        payload = qr_code.get('payload_json')
        if isinstance(payload, str):
            payload = json.loads(payload)
        
        # Generate QR code image
        qr_data = json.dumps(payload)
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to bytes
        qr_img_io = BytesIO()
        img.save(qr_img_io, 'PNG')
        qr_img_io.seek(0)
        
        # Create PDF
        pdf_io = BytesIO()
        c = canvas.Canvas(pdf_io, pagesize=letter)
        width, height = letter
        
        # Add title
        c.setFont("Helvetica-Bold", 16)
        c.drawString(1*inch, height - 1*inch, "Medicine QR Code")
        
        # Add medicine details
        c.setFont("Helvetica", 10)
        y_position = height - 1.5*inch
        c.drawString(1*inch, y_position, f"Medicine: {medicine.get('name')}")
        y_position -= 0.3*inch
        c.drawString(1*inch, y_position, f"Batch No: {medicine.get('batch_no')}")
        y_position -= 0.3*inch
        c.drawString(1*inch, y_position, f"Company: {seller.get('company_name')}")
        y_position -= 0.3*inch
        c.drawString(1*inch, y_position, f"Expiry Date: {medicine.get('expiry_date')}")
        
        # Add QR code image to PDF (centered)
        qr_size = 3*inch
        x_position = (width - qr_size) / 2
        y_position -= 0.8*inch
        
        # Save QR image temporarily for PDF
        temp_img = BytesIO()
        img.save(temp_img, 'PNG')
        temp_img.seek(0)
        
        c.drawImage(temp_img, x_position, y_position - qr_size, width=qr_size, height=qr_size)
        
        # Add footer
        c.setFont("Helvetica", 8)
        c.drawString(1*inch, 0.5*inch, f"Generated on: {datetime.now(timezone.utc).isoformat()}")
        c.drawString(1*inch, 0.3*inch, f"QR ID: {qr_id}")
        
        c.save()
        pdf_io.seek(0)
        
        # Return as downloadable file
        medicine_name = medicine.get('name', 'medicine').replace(' ', '_')
        batch_no = medicine.get('batch_no', 'batch').replace(' ', '_')
        filename = f"QR_{medicine_name}_{batch_no}_{qr_id[:8]}.pdf"
        
        return send_file(
            pdf_io,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    
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



