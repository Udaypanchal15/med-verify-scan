# """
# Blockchain routes for QR code anchoring and verification
# """
# from flask import Blueprint, jsonify
# from middleware.auth import login_required, admin_required
# from backend.services.blockchain_service_disabled import QRBlockchainService

# blockchain_bp = Blueprint('blockchain_bp', __name__, url_prefix='/blockchain')

# @blockchain_bp.route('/info', methods=['GET'])
# @login_required
# def get_blockchain_info(current_user, user_id):
#     """Get blockchain network information"""
#     try:
#         blockchain_service = QRBlockchainService()
#         info = blockchain_service.get_network_info()
#         return jsonify({
#             "message": "Blockchain information retrieved successfully",
#             "data": info
#         }), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# @blockchain_bp.route('/verify', methods=['POST'])
# @login_required
# def verify_hash(current_user, user_id):
#     """Verify if a hash is anchored on blockchain"""
#     try:
#         from flask import request
#         data = request.get_json()
        
#         hash_value = data.get('hash')
#         tx_hash = data.get('tx_hash')
        
#         if not hash_value:
#             return jsonify({"error": "Hash is required"}), 400
        
#         blockchain_service = QRBlockchainService()
#         if not blockchain_service.is_available():
#             return jsonify({
#                 "error": "Blockchain service not available"
#             }), 503
        
#         # Verify hash
#         is_anchored = blockchain_service.blockchain.verify_hash_anchored(hash_value, tx_hash)
        
#         return jsonify({
#             "message": "Hash verification completed",
#             "data": {
#                 "hash": hash_value,
#                 "anchored": is_anchored,
#                 "tx_hash": tx_hash
#             }
#         }), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

