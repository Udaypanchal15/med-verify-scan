"""
Unit tests for QR code signing and verification
"""
import unittest
import json
from services.qr_signer import QRCodeSigner, verify_qr_signature, generate_key_pair_files
import tempfile
import os

class TestQRCodeSigner(unittest.TestCase):
    """Test cases for QR code signing"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.signer = QRCodeSigner()
        self.test_payload = {
            "medicine_id": "test-medicine-123",
            "batch_no": "BATCH001",
            "mfg_date": "2024-01-01",
            "expiry_date": "2026-01-01",
            "seller_id": "seller-123"
        }
    
    def test_key_generation(self):
        """Test key pair generation"""
        private_key_pem, public_key_pem = self.signer.generate_key_pair()
        
        self.assertIsNotNone(private_key_pem)
        self.assertIsNotNone(public_key_pem)
        self.assertIn(b'BEGIN PRIVATE KEY', private_key_pem)
        self.assertIn(b'BEGIN PUBLIC KEY', public_key_pem)
    
    def test_canonical_json(self):
        """Test canonical JSON serialization"""
        payload1 = {"b": 2, "a": 1, "c": 3}
        payload2 = {"c": 3, "a": 1, "b": 2}
        
        json1 = self.signer.canonical_json(payload1)
        json2 = self.signer.canonical_json(payload2)
        
        # Should produce the same output regardless of key order
        self.assertEqual(json1, json2)
        self.assertEqual(json1, '{"a":1,"b":2,"c":3}')
    
    def test_sign_and_verify(self):
        """Test signing and verification"""
        # Sign payload
        signature = self.signer.sign_payload(self.test_payload)
        
        self.assertIsNotNone(signature)
        self.assertIsInstance(signature, str)
        
        # Get public key
        public_key_pem = self.signer.get_public_key_pem()
        
        # Verify signature
        is_valid = self.signer.verify_signature(self.test_payload, signature, public_key_pem)
        self.assertTrue(is_valid)
    
    def test_signature_verification_fails_on_tampering(self):
        """Test that signature verification fails when payload is tampered"""
        # Sign original payload
        signature = self.signer.sign_payload(self.test_payload)
        public_key_pem = self.signer.get_public_key_pem()
        
        # Tamper with payload
        tampered_payload = self.test_payload.copy()
        tampered_payload["batch_no"] = "TAMPERED"
        
        # Verify should fail
        is_valid = self.signer.verify_signature(tampered_payload, signature, public_key_pem)
        self.assertFalse(is_valid)
    
    def test_signature_verification_fails_on_wrong_key(self):
        """Test that signature verification fails with wrong public key"""
        # Sign with one key
        signature = self.signer.sign_payload(self.test_payload)
        
        # Create another signer with different key
        other_signer = QRCodeSigner()
        other_public_key_pem = other_signer.get_public_key_pem()
        
        # Verification should fail with wrong key
        is_valid = self.signer.verify_signature(self.test_payload, signature, other_public_key_pem)
        self.assertFalse(is_valid)
    
    def test_key_save_and_load(self):
        """Test saving and loading keys"""
        with tempfile.TemporaryDirectory() as temp_dir:
            key_path = os.path.join(temp_dir, "test_key.pem")
            
            # Generate and save key
            self.signer.save_private_key(key_path)
            self.assertTrue(os.path.exists(key_path))
            
            # Create new signer and load key
            loaded_signer = QRCodeSigner(key_path)
            
            # Both signers should produce the same public key
            original_public_key = self.signer.get_public_key_pem()
            loaded_public_key = loaded_signer.get_public_key_pem()
            
            self.assertEqual(original_public_key, loaded_public_key)
    
    def test_create_qr_payload(self):
        """Test QR payload creation"""
        payload = self.signer.create_qr_payload(
            medicine_id="med-123",
            batch_no="BATCH001",
            mfg_date="2024-01-01",
            expiry_date="2026-01-01",
            seller_id="seller-123"
        )
        
        self.assertEqual(payload["medicine_id"], "med-123")
        self.assertEqual(payload["batch_no"], "BATCH001")
        self.assertEqual(payload["mfg_date"], "2024-01-01")
        self.assertEqual(payload["expiry_date"], "2026-01-01")
        self.assertEqual(payload["seller_id"], "seller-123")
    
    def test_sign_qr_code(self):
        """Test complete QR code signing"""
        qr_data = self.signer.sign_qr_code(
            medicine_id="med-123",
            batch_no="BATCH001",
            mfg_date="2024-01-01",
            expiry_date="2026-01-01",
            seller_id="seller-123"
        )
        
        self.assertIn("signature", qr_data)
        self.assertIn("medicine_id", qr_data)
        self.assertIsNotNone(qr_data["signature"])
        
        # Verify signature
        signature = qr_data.pop("signature")
        public_key_pem = self.signer.get_public_key_pem()
        is_valid = verify_qr_signature(qr_data, signature, public_key_pem)
        self.assertTrue(is_valid)
    
    def test_standalone_verify_function(self):
        """Test standalone verify function"""
        signature = self.signer.sign_payload(self.test_payload)
        public_key_pem = self.signer.get_public_key_pem()
        
        is_valid = verify_qr_signature(self.test_payload, signature, public_key_pem)
        self.assertTrue(is_valid)

class TestKeyPairGeneration(unittest.TestCase):
    """Test key pair file generation"""
    
    def test_generate_key_pair_files(self):
        """Test generating key pair files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            private_key_path = os.path.join(temp_dir, "private_key.pem")
            public_key_path = os.path.join(temp_dir, "public_key.pem")
            
            success = generate_key_pair_files(private_key_path, public_key_path)
            
            self.assertTrue(success)
            self.assertTrue(os.path.exists(private_key_path))
            self.assertTrue(os.path.exists(public_key_path))
            
            # Verify files contain keys
            with open(private_key_path, 'rb') as f:
                private_key = f.read()
                self.assertIn(b'BEGIN PRIVATE KEY', private_key)
            
            with open(public_key_path, 'rb') as f:
                public_key = f.read()
                self.assertIn(b'BEGIN PUBLIC KEY', public_key)

if __name__ == '__main__':
    unittest.main()



