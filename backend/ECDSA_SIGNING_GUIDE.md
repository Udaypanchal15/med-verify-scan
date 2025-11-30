# ECDSA QR Code Signing Guide

## Overview

The ECDSA signing module provides cryptographic signing and verification for QR code payloads. This ensures the authenticity and integrity of medicine QR codes.

## Features

- **ECDSA Key Generation**: Generate P-256 (secp256r1) key pairs
- **Canonical JSON**: Consistent JSON serialization for signing
- **Payload Signing**: Sign QR code payloads with private key
- **Signature Verification**: Verify signatures with public key
- **Key Management**: Save/load keys from files

## Usage

### 1. Generate Key Pair

#### Using the Script
```bash
python backend/scripts/generate_keys.py --output-dir ./keys --seller-id seller123
```

This will create:
- `keys/seller_seller123_private_key.pem` (keep secure!)
- `keys/seller_seller123_public_key.pem` (store in database)

#### Programmatically
```python
from services.qr_signer import QRCodeSigner

# Generate new key pair
signer = QRCodeSigner()
private_key_pem, public_key_pem = signer.generate_key_pair()

# Save keys
signer.save_private_key('./keys/private_key.pem')
public_key_str = signer.get_public_key_pem()
```

### 2. Sign QR Code Payload

```python
from services.qr_signer import QRCodeSigner

# Initialize signer with private key
signer = QRCodeSigner(private_key_path='./keys/private_key.pem')

# Create and sign QR code
qr_data = signer.sign_qr_code(
    medicine_id="med-123",
    batch_no="BATCH001",
    mfg_date="2024-01-01",
    expiry_date="2026-01-01",
    seller_id="seller-123"
)

# qr_data contains:
# {
#     "medicine_id": "med-123",
#     "batch_no": "BATCH001",
#     "mfg_date": "2024-01-01",
#     "expiry_date": "2026-01-01",
#     "seller_id": "seller-123",
#     "signature": "base64_encoded_signature"
# }
```

### 3. Verify QR Code Signature

```python
from services.qr_signer import verify_qr_signature

# QR data from scanned code
qr_data = {
    "medicine_id": "med-123",
    "batch_no": "BATCH001",
    "mfg_date": "2024-01-01",
    "expiry_date": "2026-01-01",
    "seller_id": "seller-123",
    "signature": "base64_encoded_signature"
}

# Public key from database (seller's public key)
public_key_pem = "-----BEGIN PUBLIC KEY-----\n..."

# Extract payload and signature
signature = qr_data.pop("signature")
payload = qr_data

# Verify signature
is_valid = verify_qr_signature(payload, signature, public_key_pem)

if is_valid:
    print("✅ Signature is valid")
else:
    print("❌ Signature is invalid")
```

### 4. Using QR Code Service

```python
from services.qr_service import QRCodeService

# Initialize service (for signing, requires private key path)
qr_service = QRCodeService(seller_private_key_path='./keys/private_key.pem')

# Create signed QR code
qr_code = qr_service.create_signed_qr(
    medicine_id="med-123",
    seller_id="seller-123",
    issued_by="user-123",
    blockchain_tx="0x..."  # Optional
)

# Verify QR code
verification_result = qr_service.verify_qr_code(
    qr_data=qr_data,
    public_key_pem=public_key_pem
)

# verification_result contains:
# {
#     "verified": True/False,
#     "signature_valid": True/False,
#     "in_database": True/False,
#     "revoked": True/False,
#     "expired": True/False,
#     "details": {...}
# }
```

## Canonical JSON

The signing process uses **canonical JSON** to ensure consistent serialization:

- Keys are sorted alphabetically
- No whitespace between elements
- Consistent encoding (UTF-8)

Example:
```python
# These produce the same canonical JSON:
{"b": 2, "a": 1}  # Input 1
{"a": 1, "b": 2}  # Input 2

# Both become: '{"a":1,"b":2}'
```

## Security Considerations

### Private Key Storage

**⚠️ IMPORTANT**: Private keys must be kept secure!

1. **Development/Prototype**:
   - Store private keys in files with restrictive permissions (600)
   - Never commit private keys to version control
   - Use environment variables for key paths

2. **Production**:
   - Use Hardware Security Modules (HSM) or Key Management Services (KMS)
   - Never store private keys in application code or databases
   - Use secure key storage solutions (AWS KMS, Azure Key Vault, etc.)

### Public Key Storage

- Store public keys in the database (sellers table)
- Public keys can be shared openly (they're used for verification)
- Ensure public keys are associated with approved sellers

### Signature Verification

- Always verify signatures server-side
- Never trust client-side verification alone
- Check signature validity before processing QR data
- Verify seller status (approved/revoked) before trusting signatures

## Key Pair Management

### For Sellers

1. Generate key pair when seller is approved
2. Store private key securely (HSM/KMS in production)
3. Store public key in database (sellers table)
4. Use private key only for signing QR codes
5. Never share private key

### For System

1. Verify signatures using seller's public key
2. Check seller status before verification
3. Revoke keys if seller is compromised
4. Log all signing and verification events

## Testing

Run unit tests:
```bash
cd backend
python -m pytest tests/test_qr_signer.py -v
```

## API Integration

### Signing (Seller Endpoint)

```python
# POST /seller/issue_qr
{
    "medicine_id": "med-123",
    "seller_id": "seller-123"
}

# Response includes signed QR code with signature
```

### Verification (Scan Endpoint)

```python
# POST /scan
{
    "qr_data": {
        "medicine_id": "med-123",
        "batch_no": "BATCH001",
        ...
        "signature": "base64_signature"
    }
}

# Response includes verification result
```

## Troubleshooting

### Signature Verification Fails

1. Check that payload matches exactly (canonical JSON)
2. Verify public key is correct for the seller
3. Ensure signature is base64 encoded correctly
4. Check that seller is approved and key is not revoked

### Key Loading Fails

1. Verify key file path is correct
2. Check file permissions (600 for private keys)
3. Ensure key format is PEM
4. Verify key is not corrupted

### Canonical JSON Mismatch

1. Ensure keys are sorted alphabetically
2. Remove all whitespace
3. Use consistent encoding (UTF-8)
4. Check for hidden characters or BOM

## Example Workflow

1. **Seller Registration**:
   - Seller applies for approval
   - Admin approves seller
   - System generates key pair for seller
   - Public key stored in database
   - Private key stored securely

2. **QR Code Issuance**:
   - Seller creates medicine record
   - Seller issues QR code for medicine
   - System signs payload with seller's private key
   - Signed QR code stored in database
   - QR code returned to seller

3. **QR Code Verification**:
   - User scans QR code
   - System extracts payload and signature
   - System retrieves seller's public key
   - System verifies signature
   - System checks database for QR code
   - System returns verification result

## References

- [ECDSA Wikipedia](https://en.wikipedia.org/wiki/Elliptic_Curve_Digital_Signature_Algorithm)
- [P-256 Curve](https://tools.ietf.org/html/rfc5480)
- [Cryptography Library](https://cryptography.io/)



