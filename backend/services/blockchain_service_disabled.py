# """
# Blockchain Service Integration with QR Code Service
# High-level service for blockchain operations related to QR codes
# """
# import os
# from typing import Optional, Dict, Any
# from backend.services.blockchain_disabled import BlockchainService, create_qr_hash, anchor_qr_code

# class QRBlockchainService:
#     """Service for QR code blockchain operations"""
    
#     def __init__(self):
#         """Initialize blockchain service"""
#         rpc_url = os.getenv('ETH_RPC_URL')
#         private_key = os.getenv('BLOCKCHAIN_PRIVATE_KEY')
#         contract_address = os.getenv('BLOCKCHAIN_CONTRACT_ADDRESS')
#         network = os.getenv('BLOCKCHAIN_NETWORK', 'polygon-mumbai')
        
#         self.blockchain = None
#         if rpc_url:
#             try:
#                 self.blockchain = BlockchainService(
#                     rpc_url=rpc_url,
#                     private_key=private_key,
#                     contract_address=contract_address,
#                     network=network
#                 )
#             except Exception as e:
#                 print(f"Warning: Blockchain service not available: {e}")
#                 self.blockchain = None
    
#     def is_available(self) -> bool:
#         """Check if blockchain service is available"""
#         if not self.blockchain:
#             return False
#         return self.blockchain.is_connected()
    
#     def anchor_qr_code_issuance(self, payload: Dict[str, Any], signature: str) -> Optional[Dict[str, Any]]:
#         """
#         Anchor QR code issuance on blockchain
#         Returns transaction details or None
#         """
#         if not self.is_available():
#             return None
        
#         try:
#             result = anchor_qr_code(self.blockchain, payload, signature)
#             return result
#         except Exception as e:
#             print(f"Error anchoring QR code: {e}")
#             return None
    
#     def verify_qr_code_anchored(self, payload: Dict[str, Any], signature: str,
#                                tx_hash: Optional[str] = None) -> bool:
#         """
#         Verify if QR code is anchored on blockchain
#         Returns True if anchored, False otherwise
#         """
#         if not self.is_available():
#             return False
        
#         try:
#             # Create hash
#             hash_value = create_qr_hash(payload, signature)
            
#             # Verify hash
#             if tx_hash:
#                 return self.blockchain.verify_hash_anchored(hash_value, tx_hash)
#             else:
#                 # Without tx_hash, we can't verify (would need to scan)
#                 return False
#         except Exception as e:
#             print(f"Error verifying QR code: {e}")
#             return False
    
#     def get_transaction_url(self, tx_hash: str) -> Optional[str]:
#         """Get blockchain explorer URL for transaction"""
#         if not self.blockchain:
#             return None
#         return self.blockchain.get_transaction_url(tx_hash)
    
#     def get_network_info(self) -> Dict[str, Any]:
#         """Get blockchain network information"""
#         if not self.is_available():
#             return {
#                 "available": False,
#                 "message": "Blockchain service not available"
#             }
        
#         return {
#             "available": True,
#             "connected": self.blockchain.is_connected(),
#             "chain_id": self.blockchain.get_chain_id(),
#             "network": self.blockchain.network,
#             "account": self.blockchain.get_account_address(),
#             "balance": self.blockchain.get_balance()
#         }

