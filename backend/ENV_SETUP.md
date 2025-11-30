# Environment Variables Setup

Create a `.env` file in the `backend` directory with the following variables:

```env
# Flask Configuration
FLASK_SECRET_KEY=your-secret-key-here-change-in-production
FLASK_ENV=development
FLASK_DEBUG=True

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/med_verify_db

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-key-here-change-in-production
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=86400

# Seller Private Key (for prototype - use HSM/KMS in production)
SELLER_PRIVATE_KEY_PATH=./keys/seller_private_key.pem

# Blockchain Configuration
ETH_RPC_URL=https://polygon-mumbai.g.alchemy.com/v2/YOUR_API_KEY
BLOCKCHAIN_PRIVATE_KEY=your-blockchain-private-key-for-anchoring
BLOCKCHAIN_CONTRACT_ADDRESS=0x0000000000000000000000000000000000000000
BLOCKCHAIN_NETWORK=polygon-mumbai

# Email Configuration (SMTP)
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASS=your-sendgrid-api-key
SMTP_FROM_EMAIL=noreply@medverify.com
# Alternative: SendGrid API Key
SENDGRID_API_KEY=your-sendgrid-api-key

# Push Notifications (Firebase Cloud Messaging)
FCM_SERVER_KEY=your-fcm-server-key
FCM_PROJECT_ID=your-fcm-project-id

# SMS Configuration (Twilio - Optional)
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=+1234567890

# Redis Configuration (for Celery)
REDIS_URL=redis://localhost:6379/0

# Storage Configuration (Supabase or AWS S3)
STORAGE_TYPE=supabase
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key
SUPABASE_BUCKET=med-verify-storage

# AWS S3 Configuration (alternative)
S3_BUCKET=med-verify-storage
S3_ACCESS_KEY=your-s3-access-key
S3_SECRET_KEY=your-s3-secret-key
S3_REGION=us-east-1

# AI Configuration
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-3.5-turbo

# OCR Configuration
TESSERACT_CMD=/usr/bin/tesseract  # Linux/Mac
# TESSERACT_CMD=C:\\Program Files\\Tesseract-OCR\\tesseract.exe  # Windows

# CORS Configuration
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Rate Limiting
RATE_LIMIT_ENABLED=True
RATE_LIMIT_PER_MINUTE=60

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

## Quick Setup

1. Copy this template to `.env` in the backend directory
2. Update the values with your actual credentials
3. For development, you can use dummy values for optional services (SMS, blockchain)
4. Make sure PostgreSQL is running and create the database:
   ```bash
   createdb med_verify_db
   ```
5. Run the database initialization script:
   ```bash
   cd backend
   python database/init_db.py
   ```
