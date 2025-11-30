"""
Script to generate ECDSA key pair for sellers
Usage: python scripts/generate_keys.py [output_dir]
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.qr_signer import generate_key_pair_files
import argparse

def main():
    parser = argparse.ArgumentParser(description='Generate ECDSA key pair for QR code signing')
    parser.add_argument('--output-dir', '-o', default='./keys', help='Output directory for keys')
    parser.add_argument('--seller-id', '-s', help='Seller ID (for naming keys)')
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Generate key file names
    if args.seller_id:
        private_key_path = os.path.join(args.output_dir, f'seller_{args.seller_id}_private_key.pem')
        public_key_path = os.path.join(args.output_dir, f'seller_{args.seller_id}_public_key.pem')
    else:
        private_key_path = os.path.join(args.output_dir, 'private_key.pem')
        public_key_path = os.path.join(args.output_dir, 'public_key.pem')
    
    print("=" * 50)
    print("Generating ECDSA Key Pair")
    print("=" * 50)
    print(f"Output directory: {args.output_dir}")
    print(f"Private key: {private_key_path}")
    print(f"Public key: {public_key_path}")
    print()
    
    # Generate keys
    success = generate_key_pair_files(private_key_path, public_key_path)
    
    if success:
        print("✅ Key pair generated successfully!")
        print()
        print("⚠️  IMPORTANT SECURITY NOTES:")
        print("1. Keep the private key secure and never share it")
        print("2. Set restrictive permissions on the private key file")
        print("3. In production, use HSM/KMS for key storage")
        print("4. Store the public key in the database for verification")
        print()
        print("To use the keys:")
        print(f"  Private key path: {private_key_path}")
        print(f"  Public key (for database): {public_key_path}")
    else:
        print("❌ Failed to generate key pair")
        sys.exit(1)

if __name__ == '__main__':
    main()



