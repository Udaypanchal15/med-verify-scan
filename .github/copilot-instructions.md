# Copilot Instructions - Medicine Verification Scanner

## 🎯 Project Overview

**Med-Verify-Scan** is a full-stack medicine authentication and reminder system combining QR codes, ECDSA cryptography, AI services, and blockchain anchoring. It's a university-level educational project with three user roles (user, seller, admin) managing medicine verification workflows.

### Tech Stack

- **Frontend**: React 18 + Vite + Tailwind CSS + Shadcn UI
- **Backend**: Flask + PostgreSQL + JWT
- **Security**: ECDSA signing (P-256 curve), JWT auth with role-based access
- **AI**: OCR (pytesseract), Image Verification (TensorFlow/MobileNet), LLM (OpenAI)
- **Optional**: Blockchain (Ethereum/Polygon), Notifications (Email/FCM/SMS)

---

## 🏗️ Architecture & Data Flow

### Key User Workflows

**Seller Workflow**: Register → KYC Approval → Generate Keys → Create Medicines → Issue QR Codes

**User Workflow**: Register → Scan QR Codes → Verify Authenticity → Create Reminders

**Admin Workflow**: Approve Sellers → Approve Medicines → Monitor System

### Critical Service Boundaries

- **Authentication Layer** (`backend/middleware/auth.py`): Decorators `@role_required()`, `@admin_required()`, `@seller_required()` inject `current_user` and `user_id` into route handlers
- **QR Signing** (`backend/services/qr_signer.py`): ECDSA with canonical JSON serialization for deterministic signatures
- **Reminders** (`backend/services/reminder_service.py`, `reminder_worker.py`): APScheduler-based background worker processes recurring reminders with user timezone support
- **Notification Router** (`backend/services/notification_service.py`): Abstracts Email/FCM/SMS behind single interface

### Database Schema (10 tables in PostgreSQL)

- `users`: Email/password + role + timezone
- `sellers`: KYC status tracking, public_key storage
- `medicines`: Product metadata + approval_status
- `qr_issuances`: Medicine-QR linkage with seller signature
- `scans`: User verification history + AI confidence scores
- `reminders`: Recurring medicine reminders with recurrence rules
- `device_tokens`: Push notification device registration
- Supporting: `admin_logs`, `key_revocations`, `seller_documents`

---

## 🔑 Key Design Patterns & Conventions

### 1. Role-Based Access Control (RBAC)

```python
# Auth middleware wraps routes with role checking
@role_required('seller', 'admin')
def protected_route(current_user, user_id):
    # current_user is injected Dict with id, email, role, timezone
    # user_id extracted from JWT identity
    pass
```

### 2. Model Layer Pattern

Database operations use static methods in `database/models.py` classes:

```python
# Models return Dict or List[Dict], never database objects
user = User.get_by_id(user_id)  # Returns Dict or None
medicines = Medicine.get_by_seller(seller_id)  # Returns List[Dict]
```

### 3. ECDSA QR Signing (Security-Critical)

- **Canonical JSON**: Keys sorted alphabetically, no whitespace (ensures reproducible hashes)
- **P-256 Curve**: secp256r1 via cryptography library
- **Verification**: Public key embedded in QR payload, signature base64-encoded

```python
# From qr_signer.py
signature = signer.sign_payload({"medicine_id": "123"})
is_valid = signer.verify_signature(payload, signature, public_key_pem)
```

### 4. Reminder Recurrence Logic

Uses `dateutil.rrule` with timezone-aware datetime handling:

- Supports DAILY, WEEKLY, MONTHLY, YEARLY patterns
- Worker queries due reminders every 60 seconds (configurable in `start_reminder_worker()`)
- Device tokens associated with users for push notifications

### 5. AI Service Abstraction

Single entry point `backend/services/ai_service.py` wraps:

- **OCR**: `ocr_service.py` (pytesseract) → extracts text from medicine images
- **Image Verification**: `image_verification.py` (TensorFlow MobileNet) → 0-1 confidence
- **LLM**: `llm_service.py` (OpenAI) → validity checks via API

---

## 📂 File Structure & Key Files

```
backend/
├── app.py                 # Flask app config, blueprints registration, JWT setup
├── database/
│   ├── models.py          # Model classes with static CRUD methods
│   ├── __init__.py        # Connection pooling, query execution
│   └── schema.sql         # Table definitions (10 tables)
├── routes/                # API endpoints grouped by resource
│   ├── auth_routes.py     # Register, login, refresh, logout
│   ├── seller_routes.py   # KYC, medicine CRUD, QR issuance
│   ├── medicine_routes.py # Search, approval workflows
│   ├── scan_routes.py     # QR verification endpoint (core feature)
│   ├── reminder_routes.py # Reminder CRUD + device token registration
│   └── admin_routes.py    # Seller/medicine approvals, logs
├── services/              # Business logic
│   ├── auth.py            # Password hashing (bcrypt), JWT generation
│   ├── qr_signer.py       # ECDSA signing (critical security)
│   ├── qr_service.py      # QR code generation (qrcode library)
│   ├── ai_service.py      # Unified AI interface
│   ├── notification_service.py  # Email/FCM/SMS abstraction
│   ├── reminder_service.py      # Recurrence rule parsing
│   └── reminder_worker.py       # Background scheduler
├── middleware/
│   ├── auth.py            # @role_required() decorators
│   └── security.py        # Additional security headers
├── contracts/
│   └── HashAnchor.sol     # Smart contract (mostly disabled in current build)
└── tests/
    └── test_qr_signer.py  # Unit tests for signing/verification

src/                        # React frontend
├── components/
│   ├── QRScanner.jsx      # Scans QR, displays verification results
│   ├── MedicineDatabase.jsx
│   ├── AIMedicineAssistant.jsx
│   └── Navigation.jsx
├── pages/
│   ├── Login.jsx
│   └── Register.jsx
└── lib/
    └── auth.js            # Frontend JWT storage, API client setup
```

---

## 🚀 Development Workflows

### Backend Development

```powershell
# Setup
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

# Environment
Copy backend/.env.example to backend/.env and configure:
- DATABASE_URL (PostgreSQL connection string)
- FLASK_SECRET_KEY, JWT_SECRET_KEY
- Optional: OPENAI_API_KEY, SENDGRID_API_KEY, ETH_RPC_URL

# Database initialization
python -c "from database import init_db; from app import app; init_db(app)"

# Run server
python app.py  # Runs on http://localhost:5000

# Tests
python -m pytest tests/ -v
```

### Frontend Development

```powershell
# Setup
npm install  # or bun install (project uses bun)

# Dev server (Vite on http://localhost:5173)
npm run dev

# Build
npm run build
```

### Key Environment Variables

```
# Database
DATABASE_URL=postgresql://user:pass@localhost/med_verify_db

# Security
FLASK_SECRET_KEY=<random-secret>
JWT_SECRET_KEY=<random-secret>

# AI (optional but enables advanced features)
OPENAI_API_KEY=sk-...

# Notifications (optional)
SENDGRID_API_KEY=SG...
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
```

---

## 🔐 Critical Security Patterns

1. **ECDSA Signing**: Always use canonical JSON before signing (see `qr_signer.py:canonical_json()`)
2. **Key Revocation**: Check `key_revocations` table before verifying old signatures
3. **Role Validation**: Decorators verify role AND check `users.is_active` flag
4. **Input Validation**: Email regex + password complexity in `auth_routes.py`
5. **Token Expiry**: Access tokens 1h, refresh tokens 24h (configurable in `app.py`)

---

## 🧪 Testing Strategy

- **Unit Tests**: `backend/tests/test_qr_signer.py` covers signing, verification, key generation
- **Manual Testing**: Use provided curl examples in `API_DOCUMENTATION.md`
- **Test Accounts**: Use admin creation script → `python backend/scripts/create_admin.py`

---

## ⚠️ Known Limitations & Workarounds

1. **Blockchain Disabled**: Contract files exist but routes disabled (feature incomplete)
2. **Limited Frontend**: Basic components only; production UI needs expansion
3. **No Production Hardening**: Private keys stored as files (use HSM in production)
4. **APScheduler Limitation**: Reminders only fire if Flask process running continuously
5. **AI Services Optional**: All AI endpoints gracefully degrade if services unavailable

---

## 📚 Documentation Reference

- **API Details**: `backend/API_DOCUMENTATION.md` (all 30+ endpoints documented)
- **Setup**: `PROJECT_SETUP_GUIDE.md`, `HOW_TO_START.md`
- **Features**: `PROJECT_INFORMATION.md`, `ALL_YOU_NEED_TO_KNOW.md`
- **Blockchain**: `backend/BLOCKCHAIN_GUIDE.md` (reference, not active)
- **ECDSA Details**: `backend/ECDSA_SIGNING_GUIDE.md`

---

## 🎯 Common Coding Tasks

### Adding a New API Endpoint

1. Create route function in `backend/routes/<resource>_routes.py`
2. Use appropriate decorator: `@role_required('seller')`
3. Inject `current_user`, `user_id` from decorator
4. Return JSON with `{"message": "...", "data": {...}}` format
5. Update `API_DOCUMENTATION.md` with request/response examples

### Modifying Database Schema

1. Update table definitions in `backend/database/schema.sql`
2. Re-run `init_db()` (warning: drops existing tables in dev)
3. Add corresponding Model class method in `backend/database/models.py`
4. Test with `test_qr_signer.py` pattern or manual queries

### Adding AI Service Integration

1. Create service file `backend/services/my_service.py`
2. Implement as class with static methods
3. Handle exceptions gracefully (don't fail core features)
4. Register in `ai_service.py` as aggregated method
5. Document in `AI_SERVICES_GUIDE.md`

---

## 🔍 Debugging Tips

- **JWT Issues**: Check token expiry with `jwt.io`, verify claims match user roles
- **Database Errors**: Enable logging in `app.py`, check PostgreSQL connection string
- **QR Verification Fails**: Compare canonical JSON serialization and ensure public_key matches issuer
- **Reminders Not Firing**: Check APScheduler running, verify user timezone setting, inspect `reminder_worker.py` logs
- **CORS Errors**: Update `CORS_ORIGINS` env var in `app.py` to include frontend URL

---

## 📊 Project Statistics

- **Backend Routes**: ~30 endpoints across 6 blueprints
- **Database Tables**: 10 (users, sellers, medicines, scans, reminders, etc.)
- **Services**: 10+ including AI, notifications, reminders
- **Frontend Components**: 5+ (QRScanner, Database, Assistant, Navigation)
- **Test Coverage**: Core QR signing well-tested; UI/integration tests needed
