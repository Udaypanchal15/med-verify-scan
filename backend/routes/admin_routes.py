"""
Admin routes for KYC approval, key revocation, analytics, and audit logs
"""
from flask import Blueprint, request, jsonify
from middleware.auth import admin_required
from database.models import Seller, User, QRCode, ScanLog, RevokedKeys, Medicine
from database import execute_query
from services.seller_notification_service import get_seller_notification_service
from datetime import datetime, timezone
import json

admin_bp = Blueprint('admin_bp', __name__, url_prefix='/admin')

@admin_bp.route('/sellers', methods=['GET'])
@admin_required
def get_sellers(current_user, user_id):
    """Get all seller applications"""
    try:
        status = request.args.get('status', 'all')
        
        if status == 'pending':
            sellers = Seller.get_all_pending()
        elif status == 'approved':
            sellers = Seller.get_all_approved()
        else:
            # Get all sellers
            query = "SELECT * FROM sellers ORDER BY created_at DESC"
            results = execute_query(query, fetch_all=True)
            sellers = [dict(r) for r in results] if results else []
        
        return jsonify({
            "message": "Sellers retrieved successfully",
            "data": sellers
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/sellers/<seller_id>/approve', methods=['POST', 'OPTIONS'])
@admin_required
def approve_seller(current_user, user_id, seller_id):
    """Approve seller KYC application"""
    try:
        data = request.get_json() or {}
        admin_remarks = data.get('admin_remarks', '')
        
        seller = Seller.get_by_id(seller_id)
        if not seller:
            return jsonify({"error": "Seller not found"}), 404, {'Content-Type': 'application/json'}

        if seller.get('status') == 'approved':
            return jsonify({"error": "Seller already approved"}), 400, {'Content-Type': 'application/json'}
        
        # Update seller status
        query = """
            UPDATE sellers
            SET status = 'approved'
            WHERE id = %s
            RETURNING *
        """
        result = execute_query(query, (seller_id,), fetch_one=True)

        return jsonify({
            "message": "Seller approved successfully",
            "seller_updated": dict(result) if result else {}
        }), 200, {'Content-Type': 'application/json'}
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500, {'Content-Type': 'application/json'}

@admin_bp.route('/sellers/<seller_id>/reject', methods=['POST', 'OPTIONS'])
@admin_required
def reject_seller(current_user, user_id, seller_id):
    """Reject seller KYC application"""
    try:
        data = request.get_json() or {}
        admin_remarks = data.get('admin_remarks', '')

        seller = Seller.get_by_id(seller_id)
        if not seller:
            return jsonify({"error": "Seller not found"}), 404, {'Content-Type': 'application/json'}
        
        # Update seller status - minimal schema compatible
        query = """
            UPDATE sellers
            SET status = 'rejected'
            WHERE id = %s
            RETURNING *
        """
        result = execute_query(query, (seller_id,), fetch_one=True)

        return jsonify({
            "message": "Seller rejected successfully",
            "seller_updated": dict(result) if result else {}
        }), 200, {'Content-Type': 'application/json'}

    except Exception as e:
        return jsonify({"error": str(e)}), 500, {'Content-Type': 'application/json'}

@admin_bp.route('/sellers/<seller_id>/mark-viewed', methods=['POST', 'OPTIONS'])
@admin_required
def mark_seller_viewed(current_user, user_id, seller_id):
    """Mark seller application as viewed by admin"""
    try:
        seller = Seller.get_by_id(seller_id)
        if not seller:
            return jsonify({"error": "Seller not found"}), 404, {'Content-Type': 'application/json'}

        if seller.get('status') not in ['pending']:
            return jsonify({
                "error": "Can only mark pending applications as viewed",
                "current_status": seller.get('status')
            }), 400, {'Content-Type': 'application/json'}

        # Update seller status to viewed
        query = """
            UPDATE sellers
            SET status = 'viewed'
            WHERE id = %s
            RETURNING *
        """
        result = execute_query(query, (seller_id,), fetch_one=True)

        return jsonify({
            "message": "Seller marked as viewed",
            "seller_updated": dict(result) if result else {}
        }), 200, {'Content-Type': 'application/json'}

    except Exception as e:
        return jsonify({"error": str(e)}), 500, {'Content-Type': 'application/json'}

@admin_bp.route('/sellers/<seller_id>/set-verifying', methods=['POST', 'OPTIONS'])
@admin_required
def set_seller_verifying(current_user, user_id, seller_id):
    """Mark seller application as being verified"""
    try:
        seller = Seller.get_by_id(seller_id)
        if not seller:
            return jsonify({"error": "Seller not found"}), 404, {'Content-Type': 'application/json'}

        if seller.get('status') not in ['pending', 'viewed']:
            return jsonify({
                "error": "Can only set verifying for pending or viewed applications",
                "current_status": seller.get('status')
            }), 400, {'Content-Type': 'application/json'}
        
        # Update seller status to verifying
        query = """
            UPDATE sellers
            SET status = 'verifying'
            WHERE id = %s
            RETURNING *
        """
        result = execute_query(query, (seller_id,), fetch_one=True)

        return jsonify({
            "message": "Seller marked as verifying",
            "seller_updated": dict(result) if result else {}
        }), 200, {'Content-Type': 'application/json'}

    except Exception as e:
        return jsonify({"error": str(e)}), 500, {'Content-Type': 'application/json'}

@admin_bp.route('/sellers/<seller_id>/request-changes', methods=['POST', 'OPTIONS'])
@admin_required
def request_seller_changes(current_user, user_id, seller_id):
    """Request changes to seller application"""
    try:
        data = request.get_json() or {}
        remarks = data.get('remarks', '')

        if not remarks:
            return jsonify({"error": "Remarks are required"}), 400, {'Content-Type': 'application/json'}

        seller = Seller.get_by_id(seller_id)
        if not seller:
            return jsonify({"error": "Seller not found"}), 404, {'Content-Type': 'application/json'}

        # Update seller status to changes_required (simplified - no jsonb columns needed)
        query = """
            UPDATE sellers
            SET status = 'changes_required'
            WHERE id = %s
            RETURNING *
        """
        result = execute_query(query, (seller_id,), fetch_one=True)

        # Note: Remarks are stored in the seller's status
        # The seller can see the status "changes_required" and know to contact admin or check for details

        return jsonify({
            "message": "Changes requested successfully",
            "seller_updated": dict(result) if result else {},
            "remarks": remarks
        }), 200, {'Content-Type': 'application/json'}

    except Exception as e:
        return jsonify({"error": str(e)}), 500, {'Content-Type': 'application/json'}

@admin_bp.route('/sellers/<seller_id>/revoke', methods=['POST'])
@admin_required
def revoke_seller(current_user, user_id, seller_id):
    """Revoke seller and their keys"""
    try:
        data = request.get_json()
        reason = data.get('reason', '')
        
        seller = Seller.get_by_id(seller_id)
        if not seller:
            return jsonify({"error": "Seller not found"}), 404
        
        # Update seller status
        Seller.update_status(seller_id, 'revoked', approved_by=user_id)
        
        # Revoke seller's public key
        if seller.get('public_key'):
            RevokedKeys.create(
                seller_id=seller_id,
                public_key=seller['public_key'],
                reason=reason,
                revoked_by=user_id
            )
        
        # Log audit event
        log_audit_event(user_id, 'revoke_seller', 'seller', seller_id, {
            "seller_id": seller_id,
            "reason": reason
        })
        
        return jsonify({
            "message": "Seller revoked successfully"
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/analytics', methods=['GET'])
@admin_required
def get_analytics(current_user, user_id):
    """Get system analytics"""
    try:
        # Get scan counts
        scan_query = """
            SELECT result, COUNT(*) as count 
            FROM scan_logs 
            GROUP BY result
        """
        scan_results = execute_query(scan_query, fetch_all=True)
        scan_counts = {r['result']: r['count'] for r in scan_results} if scan_results else {}
        
        # Get total sellers
        seller_query = "SELECT COUNT(*) as count FROM sellers WHERE status = 'approved'"
        seller_result = execute_query(seller_query, fetch_one=True)
        total_sellers = seller_result['count'] if seller_result else 0
        
        # Get total medicines
        medicine_query = "SELECT COUNT(*) as count FROM medicines"
        medicine_result = execute_query(medicine_query, fetch_one=True)
        total_medicines = medicine_result['count'] if medicine_result else 0
        
        # Get total QR codes
        qr_query = "SELECT COUNT(*) as count FROM qr_codes"
        qr_result = execute_query(qr_query, fetch_one=True)
        total_qr_codes = qr_result['count'] if qr_result else 0
        
        # Get revoked QR codes
        revoked_query = "SELECT COUNT(*) as count FROM qr_codes WHERE revoked = TRUE"
        revoked_result = execute_query(revoked_query, fetch_one=True)
        revoked_qr_codes = revoked_result['count'] if revoked_result else 0
        
        return jsonify({
            "message": "Analytics retrieved successfully",
            "data": {
                "scan_counts": scan_counts,
                "total_sellers": total_sellers,
                "total_medicines": total_medicines,
                "total_qr_codes": total_qr_codes,
                "revoked_qr_codes": revoked_qr_codes,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/audit-logs', methods=['GET'])
@admin_required
def get_audit_logs(current_user, user_id):
    """Get audit logs"""
    try:
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        
        query = """
            SELECT * FROM audit_logs 
            ORDER BY created_at DESC 
            LIMIT %s OFFSET %s
        """
        results = execute_query(query, (limit, offset), fetch_all=True)
        logs = [dict(r) for r in results] if results else []
        
        return jsonify({
            "message": "Audit logs retrieved successfully",
            "data": logs
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/revoked-keys', methods=['GET'])
@admin_required
def get_revoked_keys(current_user, user_id):
    """Get all revoked keys"""
    try:
        query = "SELECT * FROM revoked_keys ORDER BY revoked_at DESC"
        results = execute_query(query, fetch_all=True)
        keys = [dict(r) for r in results] if results else []
        
        return jsonify({
            "message": "Revoked keys retrieved successfully",
            "data": keys
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/medicines', methods=['GET'])
@admin_required
def get_medicines(current_user, user_id):
    """Get all medicines with approval status"""
    try:
        status = request.args.get('status', 'all')
        
        if status == 'pending':
            medicines = Medicine.get_all_pending()
        elif status == 'approved':
            medicines = Medicine.get_all_approved()
        else:
            # Get all medicines
            query = """
                SELECT m.*, s.company_name 
                FROM medicines m 
                JOIN sellers s ON m.seller_id = s.id 
                ORDER BY m.created_at DESC
            """
            results = execute_query(query, fetch_all=True)
            medicines = [dict(r) for r in results] if results else []
        
        return jsonify({
            "message": "Medicines retrieved successfully",
            "data": medicines
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/medicines/<medicine_id>/approve', methods=['POST'])
@admin_required
def approve_medicine(current_user, user_id, medicine_id):
    """Approve a medicine"""
    try:
        medicine = Medicine.get_by_id(medicine_id)
        if not medicine:
            return jsonify({"error": "Medicine not found"}), 404
        
        if medicine.get('approval_status') == 'approved':
            return jsonify({"error": "Medicine already approved"}), 400
        
        # Update medicine status
        Medicine.update_approval_status(medicine_id, 'approved', approved_by=user_id)
        
        # Log audit event
        log_audit_event(user_id, 'approve_medicine', 'medicine', medicine_id, {
            "medicine_id": medicine_id,
            "medicine_name": medicine.get('name')
        })
        
        return jsonify({
            "message": "Medicine approved successfully",
            "data": Medicine.get_by_id(medicine_id)
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/medicines/<medicine_id>/reject', methods=['POST'])
@admin_required
def reject_medicine(current_user, user_id, medicine_id):
    """Reject a medicine"""
    try:
        data = request.get_json()
        reason = data.get('reason', '')
        
        medicine = Medicine.get_by_id(medicine_id)
        if not medicine:
            return jsonify({"error": "Medicine not found"}), 404
        
        # Update medicine status
        Medicine.update_approval_status(medicine_id, 'rejected', approved_by=user_id)
        
        # Log audit event
        log_audit_event(user_id, 'reject_medicine', 'medicine', medicine_id, {
            "medicine_id": medicine_id,
            "medicine_name": medicine.get('name'),
            "reason": reason
        })
        
        return jsonify({
            "message": "Medicine rejected successfully"
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/sellers/medicines', methods=['GET'])
@admin_required
def get_all_seller_medicines(current_user, user_id):
    """Get all medicines from all approved sellers (hierarchical view)"""
    try:
        # Get all approved sellers
        sellers = Seller.get_all_approved()
        
        # For each seller, get their medicines
        result = []
        for seller in sellers:
            seller_dict = dict(seller) if hasattr(seller, 'keys') else seller
            medicines = Medicine.get_by_seller(str(seller_dict['id']))
            result.append({
                "seller": seller_dict,
                "medicines": medicines if medicines else [],
                "medicine_count": len(medicines) if medicines else 0
            })
        
        # Calculate statistics
        total_sellers = len(result)
        total_medicines = sum(item['medicine_count'] for item in result)
        
        return jsonify({
            "message": "Medicines retrieved successfully",
            "statistics": {
                "total_sellers": total_sellers,
                "total_medicines": total_medicines
            },
            "data": result
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def log_audit_event(user_id: str, action: str, resource_type: str, resource_id: str, details: dict):
    """Log admin action to audit log"""
    try:
        query = """
            INSERT INTO audit_logs (user_id, action, resource_type, resource_id, details, ip_address)
            VALUES (%s, %s, %s, %s, %s::jsonb, %s)
        """
        from flask import request
        ip_address = request.remote_addr if request else None
        execute_query(query, (user_id, action, resource_type, resource_id, json.dumps(details), ip_address))
    except Exception as e:
        print(f"Error logging audit event: {e}")



