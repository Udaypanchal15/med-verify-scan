"""
QR Code Service - High-level service for QR code operations (No Blockchain Version)
Only: Signing, Database storage, Medicine/Seller validation
"""
import json
from datetime import datetime
from typing import Dict, Any, Optional
from services.qr_signer import QRCodeSigner, verify_qr_signature
from database.models import Medicine, QRCode, Seller

class QRCodeService:
    """Service for QR code creation and verification (blockchain removed)"""
    
    def __init__(self, seller_private_key_path: Optional[str] = None):
        self.signer = QRCodeSigner(seller_private_key_path) if seller_private_key_path else None
    
    def create_signed_qr(self, medicine_id: str, seller_id: str, issued_by: str) -> Dict[str, Any]:
        """
        Create a signed QR for a medicine (No blockchain anchoring)
        """
        medicine = Medicine.get_by_id(medicine_id)
        if not medicine:
            raise ValueError(f"Medicine not found: {medicine_id}")
        
        seller = Seller.get_by_id(seller_id)
        if not seller:
            raise ValueError(f"Seller not found: {seller_id}")
        
        if seller.get('status') != 'approved':
            raise ValueError(f"Seller not approved: {seller_id}")
        
        # Create payload
        payload_data = {
            "medicine_id": str(medicine['id']),
            "batch_no": medicine['batch_no'],
            "mfg_date": str(medicine['mfg_date']),
            "expiry_date": str(medicine['expiry_date']),
            "seller_id": str(seller['id']),
            "medicine_name": medicine['name'],
            "dosage": medicine.get('dosage'),
            "strength": medicine.get('strength'),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Sign payload
        if self.signer:
            signature = self.signer.sign_payload(payload_data)
        else:
            signature = "UNSIGNED_DEMO_MODE"  # For demo/testing only
        
        # Store in DB
        qr_code = QRCode.create(
            medicine_id=medicine_id,
            payload_json=payload_data,
            signature=signature,
            blockchain_tx=None,   # <== REMOVED BLOCKCHAIN
            issued_by=issued_by
        )

        return {
            "qr_id": str(qr_code['id']),
            "payload": payload_data,
            "signature": signature,
            "public_key": seller.get('public_key'),
            "blockchain_tx": None,      # <== REMOVED
            "blockchain_explorer_url": None,
            "issued_at": qr_code['issued_at'].isoformat() if qr_code.get('issued_at') else None
        }
    
    def verify_qr_code(self, qr_data: Dict[str, Any], public_key_pem: str) -> Dict[str, Any]:
        """
        Verify signature and verify record exists in DB (No blockchain)
        """
        result = {
            "verified": False,
            "signature_valid": False,
            "in_database": False,
            "expired": False,
            "details": {}
        }
        
        signature = qr_data.get('signature')
        payload = {k: v for k, v in qr_data.items() if k != 'signature'}
        
        if not signature:
            result["details"]["error"] = "Signature missing"
            return result
        
        # Verify signature
        try:
            result["signature_valid"] = verify_qr_signature(payload, signature, public_key_pem)
        except Exception as e:
            result["details"]["error"] = f"Signature verification failed: {str(e)}"
            return result
        
        # If invalid signature → counterfeit
        if not result["signature_valid"]:
            result["details"]["status"] = "counterfeit"
            return result
        
        # Lookup medicine
        medicine_id = payload.get("medicine_id")
        medicine = Medicine.get_by_id(medicine_id) if medicine_id else None
        
        if medicine:
            result["in_database"] = True
            result["details"]["medicine_name"] = medicine["name"]
            
            expiry_date = medicine["expiry_date"]
            if expiry_date and datetime.now().date() > expiry_date:
                result["expired"] = True
                result["details"]["status"] = "expired"
                return result
        
        if result["signature_valid"] and result["in_database"] and not result["expired"]:
            result["verified"] = True
            result["details"]["status"] = "verified"
        else:
            result["details"]["status"] = "not_found_or_invalid"
        
        return result
    
    def get_qr_code_by_id(self, qr_id: str) -> Optional[Dict[str, Any]]:
        return QRCode.get_by_id(qr_id)
    
    def revoke_qr_code(self, qr_id: str, reason: str = None) -> bool:
        try:
            QRCode.revoke(qr_id, reason)
            return True
        except Exception as e:
            print(f"Error revoking QR code: {e}")
            return False
