from flask import Blueprint, request, jsonify
from services.medicine_info import ai_describe_medicine
from database.models import Medicine
from database import execute_query

medicine_bp = Blueprint('medicine_bp', __name__, url_prefix='/medicine')

@medicine_bp.route('', methods=['GET'])
def get_medicine_info():
    med_name = request.args.get('name')
    if not med_name:
        return jsonify({"error": "Medicine name is required"}), 400

    info = ai_describe_medicine(med_name)
    return jsonify({"medicine": med_name, "info": info})

@medicine_bp.route('/all', methods=['GET'])
def get_all_medicines():
    """Get all approved medicines from all sellers"""
    try:
        medicines = Medicine.get_all_approved()
        return jsonify({
            "message": "All medicines retrieved successfully",
            "data": medicines,
            "count": len(medicines)
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@medicine_bp.route('/search', methods=['GET'])
def search_approved_medicines():
    """Search for approved medicines"""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({"error": "Search query is required"}), 400
        
        # Search approved medicines by name, category, or description
        search_query = """
            SELECT m.*, s.company_name 
            FROM medicines m 
            JOIN sellers s ON m.seller_id = s.id 
            WHERE m.approval_status = 'approved' 
            AND (
                LOWER(m.name) LIKE LOWER(%s) 
                OR LOWER(m.category) LIKE LOWER(%s) 
                OR LOWER(m.description) LIKE LOWER(%s)
            )
            ORDER BY m.created_at DESC
            LIMIT 50
        """
        search_term = f"%{query}%"
        results = execute_query(search_query, (search_term, search_term, search_term), fetch_all=True)
        medicines = [dict(r) for r in results] if results else []
        
        return jsonify({
            "message": "Search completed",
            "data": medicines,
            "count": len(medicines)
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@medicine_bp.route('/approved', methods=['GET'])
def get_approved_medicines():
    """Get all approved medicines"""
    try:
        medicines = Medicine.get_all_approved()
        return jsonify({
            "message": "Approved medicines retrieved successfully",
            "data": medicines,
            "count": len(medicines)
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
