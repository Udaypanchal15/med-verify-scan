# Medicine Verification Scanner - Quick Start Guide

## 📋 Table of Contents

- [System Overview](#system-overview)
- [Setup & Installation](#setup--installation)
- [Running the Project](#running-the-project)
- [First Steps](#first-steps)

---

## System Overview

**Med-Verify-Scan** is a full-stack medicine authentication system with three distinct user roles:

### 🧑‍⚕️ **User Role**

- Search verified medicines in the database
- Scan QR codes to verify medicine authenticity
- Check medicine details and expiry information
- Chat with AI medicine assistant
- Get warnings for unverified medicines

### 🏢 **Seller Role**

- Apply for KYC verification
- Manage medicine inventory
- Generate ECDSA signing keys
- Issue QR codes for medicines
- Track medicine approval status

### 👨‍💼 **Admin Role**

- Approve/reject seller applications
- Approve/reject medicines submitted by sellers
- View system analytics and audit logs
- Monitor all QR codes and scans
- Manage revoked keys

---

## Setup & Installation

### Prerequisites

- Python 3.9+ (Backend)
- Node.js 16+ (Frontend)
- PostgreSQL 12+
- Git

### Step 1: Clone & Navigate

```bash
git clone <repository-url>
cd med-verify-scan-main
```

### Step 2: Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Database Setup

```bash
# Create PostgreSQL database
createdb med_verify_db

# Initialize schema
psql med_verify_db < database/schema.sql

# OR run initialization script
python database/init_db.py
```

### Step 4: Environment Configuration

Create `backend/.env` file:

```env
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/med_verify_db

# Security
FLASK_SECRET_KEY=your-random-secret-key-here
JWT_SECRET_KEY=your-random-jwt-secret-here
FLASK_ENV=development

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Optional: AI Services
OPENAI_API_KEY=sk-your-api-key

# Optional: Blockchain
ETH_RPC_URL=https://sepolia.infura.io/v3/your-infura-key

# Optional: Notifications
SENDGRID_API_KEY=SG-your-sendgrid-key
```

### Step 5: Frontend Setup

```bash
# From project root
npm install  # or bun install if using bun

# Create .env.local for frontend
echo "VITE_API_URL=http://localhost:5000" > .env.local
```

---

## Running the Project

### Terminal 1: Start Backend

```bash
cd backend
.\venv\Scripts\activate  # Windows

# Run Flask server
python app.py
```

Backend starts on: **http://localhost:5000**

### Terminal 2: Start Frontend

```bash
# From project root
npm run dev  # or bun run dev
```

Frontend starts on: **http://localhost:5173**

---

## First Steps

### 1. Create Admin Account

```bash
cd backend
python scripts/create_admin.py
```

### 2. Login as Admin

```
Email: admin@example.com
Password: (follow script prompt)
URL: http://localhost:5173/login → /admin/dashboard
```

### 3. Test Seller Registration & Approval

1. Go to **http://localhost:5173/register**
2. Create new account with role: **Seller**
3. Fill KYC form (company name, license number)
4. Login as admin and approve the seller
5. Seller can now add medicines

### 4. Test Medicine Approval & QR Generation

1. Login as approved seller
2. Go to **Seller Dashboard** → **Add Medicine**
3. Fill medicine details (name, batch, dates, etc.)
4. Login as admin and approve the medicine
5. Seller can now generate QR codes

### 5. Test User Verification

1. Create regular user account
2. Login and visit main page
3. Try QR scanner to scan generated QR codes
4. Search for medicines in **User Dashboard**

---

## Troubleshooting

### Database Connection Error

```
Error: Could not connect to database
Solution: Check DATABASE_URL in .env and ensure PostgreSQL is running
```

### Port Already in Use

```
Backend: Change port in app.py line: app.run(port=5001)
Frontend: npm run dev -- --port 5174
```

### CORS Error

```
Error: Cross-Origin Request Blocked
Solution: Add frontend URL to CORS_ORIGINS in .env
```

See `/docs/troubleshooting/` for more help.

---

## Next Steps

- Explore `/docs/api/` for complete API documentation
- Read `/docs/features/` to understand available features
- Check `/docs/setup/` for advanced configuration
