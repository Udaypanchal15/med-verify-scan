"""
ECDSA QR Code Signing Service
Handles key generation, payload signing, and signature verification
"""
import json
import hashlib
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from typing import Dict, Any, Optional, Tuple
import os

class QRCodeSigner:
    """ECDSA-based QR code signing service"""
    
    def __init__(self, private_key_path: Optional[str] = None):
        """
        Initialize the signer with a private key
        If private_key_path is provided, load the key from file
        Otherwise, generate a new key pair
        """
        self.private_key = None
        self.public_key = None
        self.private_key_path = private_key_path
        
        if private_key_path and os.path.exists(private_key_path):
            self.load_private_key(private_key_path)
        else:
            self.generate_key_pair()
            if private_key_path:
                self.save_private_key(private_key_path)
    
    def generate_key_pair(self) -> Tuple[bytes, bytes]:
        """
        Generate a new ECDSA key pair using P-256 curve
        Returns (private_key_pem, public_key_pem)
        """
        # Generate private key using P-256 curve (secp256r1)
        private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
        public_key = private_key.public_key()
        
        # Serialize private key
        private_key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        # Serialize public key
        public_key_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        self.private_key = private_key
        self.public_key = public_key
        
        return private_key_pem, public_key_pem
    
    def load_private_key(self, key_path: str) -> bool:
        """Load private key from PEM file"""
        try:
            with open(key_path, 'rb') as f:
                private_key_pem = f.read()
            
            self.private_key = serialization.load_pem_private_key(
                private_key_pem,
                password=None,
                backend=default_backend()
            )
            self.public_key = self.private_key.public_key()
            return True
        except Exception as e:
            print(f"Error loading private key: {e}")
            return False
    
    def save_private_key(self, key_path: str) -> bool:
        """Save private key to PEM file"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(key_path) if os.path.dirname(key_path) else '.', exist_ok=True)
            
            private_key_pem = self.private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            
            with open(key_path, 'wb') as f:
                f.write(private_key_pem)
            
            # Set restrictive permissions (Unix-like systems)
            if os.name != 'nt':  # Not Windows
                os.chmod(key_path, 0o600)
            
            return True
        except Exception as e:
            print(f"Error saving private key: {e}")
            return False
    
    def get_public_key_pem(self) -> str:
        """Get public key in PEM format as string"""
        if not self.public_key:
            raise ValueError("Public key not available")
        
        public_key_pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return public_key_pem.decode('utf-8')
    
    def canonical_json(self, data: Dict[str, Any]) -> str:
        """
        Convert dictionary to canonical JSON string
        - Keys are sorted alphabetically
        - No whitespace
        - Consistent encoding
        """
        return json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
    
    def hash_payload(self, payload: str) -> bytes:
        """Hash payload using SHA-256"""
        return hashlib.sha256(payload.encode('utf-8')).digest()
    
    def sign_payload(self, payload_data: Dict[str, Any]) -> str:
        """
        Sign a QR code payload
        Returns base64-encoded signature
        """
        if not self.private_key:
            raise ValueError("Private key not available")
        
        # Create canonical JSON
        canonical_json_str = self.canonical_json(payload_data)
        
        # Hash the payload
        payload_hash = self.hash_payload(canonical_json_str)
        
        # Sign the hash
        signature = self.private_key.sign(
            payload_hash,
            ec.ECDSA(hashes.SHA256())
        )
        
        # Encode signature as base64
        signature_b64 = base64.b64encode(signature).decode('utf-8')
        
        return signature_b64
    
    def verify_signature(self, payload_data: Dict[str, Any], signature: str, public_key_pem: str) -> bool:
        """
        Verify a QR code signature
        Returns True if signature is valid, False otherwise
        """
        try:
            # Load public key
            public_key = serialization.load_pem_public_key(
                public_key_pem.encode('utf-8'),
                backend=default_backend()
            )
            
            # Create canonical JSON
            canonical_json_str = self.canonical_json(payload_data)
            
            # Hash the payload
            payload_hash = self.hash_payload(canonical_json_str)
            
            # Decode signature
            signature_bytes = base64.b64decode(signature)
            
            # Verify signature
            public_key.verify(
                signature_bytes,
                payload_hash,
                ec.ECDSA(hashes.SHA256())
            )
            
            return True
        except Exception as e:
            print(f"Signature verification failed: {e}")
            return False
    
    def create_qr_payload(self, medicine_id: str, batch_no: str, mfg_date: str, 
                         expiry_date: str, seller_id: str, **kwargs) -> Dict[str, Any]:
        """
        Create a QR code payload dictionary
        """
        payload = {
            "medicine_id": medicine_id,
            "batch_no": batch_no,
            "mfg_date": mfg_date,
            "expiry_date": expiry_date,
            "seller_id": seller_id,
            **kwargs
        }
        return payload
    
    def sign_qr_code(self, medicine_id: str, batch_no: str, mfg_date: str,
                    expiry_date: str, seller_id: str, **kwargs) -> Dict[str, Any]:
        """
        Create and sign a QR code payload
        Returns payload with signature
        """
        # Create payload
        payload = self.create_qr_payload(
            medicine_id=medicine_id,
            batch_no=batch_no,
            mfg_date=mfg_date,
            expiry_date=expiry_date,
            seller_id=seller_id,
            **kwargs
        )
        
        # Sign payload
        signature = self.sign_payload(payload)
        
        # Add signature to payload
        payload['signature'] = signature
        
        return payload

def load_public_key_from_pem(public_key_pem: str):
    """Load public key from PEM string"""
    return serialization.load_pem_public_key(
        public_key_pem.encode('utf-8'),
        backend=default_backend()
    )

def verify_qr_signature(payload_data: Dict[str, Any], signature: str, public_key_pem: str) -> bool:
    """
    Standalone function to verify QR code signature
    """
    signer = QRCodeSigner()
    return signer.verify_signature(payload_data, signature, public_key_pem)

def generate_key_pair_files(private_key_path: str, public_key_path: str) -> bool:
    """
    Generate and save key pair to files
    Returns True if successful
    """
    try:
        signer = QRCodeSigner()
        private_key_pem, public_key_pem = signer.generate_key_pair()
        
        # Save private key
        os.makedirs(os.path.dirname(private_key_path) if os.path.dirname(private_key_path) else '.', exist_ok=True)
        with open(private_key_path, 'wb') as f:
            f.write(private_key_pem)
        if os.name != 'nt':
            os.chmod(private_key_path, 0o600)
        
        # Save public key
        os.makedirs(os.path.dirname(public_key_path) if os.path.dirname(public_key_path) else '.', exist_ok=True)
        with open(public_key_path, 'wb') as f:
            f.write(public_key_pem)
        
        return True
    except Exception as e:
        print(f"Error generating key pair: {e}")
        return False



