# 📚 Documentation - Medicine Verification Scanner

Welcome! This folder contains all documentation for the Med-Verify-Scan project.

## 📂 Organization

### 🚀 [Setup](/setup/) - Getting Started

- **[QUICKSTART.md](setup/QUICKSTART.md)** - 5-minute setup guide
- **[INSTALLATION.md](setup/INSTALLATION.md)** - Detailed installation (coming soon)
- **[DEPLOYMENT.md](setup/DEPLOYMENT.md)** - Production deployment (coming soon)

**For New Developers**: Start here! Follow QUICKSTART.md to get the app running locally.

---

### 🎯 [Features](/features/) - What Can You Do?

- **[FEATURES.md](features/FEATURES.md)** - Complete feature guide for all roles

**What to expect:**

- All user features (scanning, search, AI assistant)
- All seller features (KYC, medicine management, QR generation)
- All admin features (approvals, analytics)
- Security features
- Real-world workflow examples

---

### 🔌 [API](/api/) - Integration Guide

- **[ENDPOINTS.md](api/ENDPOINTS.md)** - Complete API reference with examples

**Includes:**

- All REST endpoints with request/response examples
- Authentication flow
- Error handling
- Status codes
- Rate limiting info

---

### 🐛 [Troubleshooting](/troubleshooting/) - Problem Solving

- **[TROUBLESHOOTING.md](troubleshooting/TROUBLESHOOTING.md)** - Common issues and solutions

**Covers:**

- Database connection errors
- CORS issues
- Port conflicts
- Authentication problems
- Debugging checklist

---

## 🗺️ Navigation Guide

**I want to...**

### Get Started

👉 Read: [setup/QUICKSTART.md](setup/QUICKSTART.md)

### Understand the System

👉 Read: [features/FEATURES.md](features/FEATURES.md)

### Build a Feature / Integrate API

👉 Read: [api/ENDPOINTS.md](api/ENDPOINTS.md)

### Fix an Error

👉 Read: [troubleshooting/TROUBLESHOOTING.md](troubleshooting/TROUBLESHOOTING.md)

### See Architecture Overview

👉 Read: Root [`README.md`](../README.md)

---

## 📋 Quick Reference

### Key Concepts

**Roles:**

- 👤 **User**: Scans QR codes, searches medicines, uses AI assistant
- 🏢 **Seller**: Manages medicines, generates QR codes, applies for KYC
- 👨‍💼 **Admin**: Approves sellers/medicines, views analytics

**Workflows:**

1. Seller registers → Admin approves → Seller adds medicine → Admin approves → QR generated
2. User scans QR → System verifies signature → Shows medicine details or warning
3. User searches → Database returns only approved medicines

**Key Features:**

- ECDSA cryptographic signing for QR codes
- JWT authentication
- Role-based access control
- Medicine approval workflow
- Unverified medicine warnings

---

## 🔍 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Browser (React)                           │
│  /admin/dashboard  /seller/dashboard  /user/dashboard       │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/JWT
┌────────────────────────▼────────────────────────────────────┐
│              Backend (Flask)                                 │
│  ┌──────────────┐  ┌─────────────────┐  ┌──────────────┐   │
│  │ Routes       │  │ Services        │  │ Middleware   │   │
│  │ - auth       │  │ - qr_signer     │  │ - auth       │   │
│  │ - admin      │  │ - ai_service    │  │ - security   │   │
│  │ - seller     │  │ - notification  │  │              │   │
│  │ - medicine   │  │ - reminder      │  │              │   │
│  │ - scan       │  │ - ocr           │  │              │   │
│  └──────────────┘  └─────────────────┘  └──────────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │ psycopg2
┌────────────────────────▼────────────────────────────────────┐
│              PostgreSQL Database                             │
│  users | sellers | medicines | qr_codes | scan_logs |      │
│  reminders | notifications | audit_logs | ...               │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Project Status

| Component         | Status             | Notes                               |
| ----------------- | ------------------ | ----------------------------------- |
| Backend API       | ✅ Complete        | All 30+ endpoints working           |
| Frontend UI       | ✅ Mostly Complete | Admin, Seller, User dashboards done |
| Authentication    | ✅ Complete        | JWT, roles, protections             |
| QR Verification   | ✅ Complete        | ECDSA signing working               |
| Medicine Approval | ✅ Complete        | Admin workflow done                 |
| AI Integration    | ✅ Complete        | OpenAI integration ready            |
| Database          | ✅ Complete        | 10 tables, proper schema            |
| Documentation     | ✅ Complete        | You're reading it!                  |
| Blockchain        | 🟡 Partial         | Contracts ready, routes disabled    |
| Notifications     | 🟡 Partial         | Backend ready, UI pending           |

---

## 🎓 Learning Path

**New to the project?** Follow this order:

1. ✅ Read [setup/QUICKSTART.md](setup/QUICKSTART.md) - Get it running
2. ✅ Read [features/FEATURES.md](features/FEATURES.md) - Understand capabilities
3. ✅ Try each role:
   - Register as User → Scan QR codes
   - Register as Seller → Add medicines
   - Create Admin → Approve things
4. ✅ Read [api/ENDPOINTS.md](api/ENDPOINTS.md) - How to integrate
5. ✅ Read [troubleshooting/TROUBLESHOOTING.md](troubleshooting/TROUBLESHOOTING.md) - When stuck

---

## 💡 Pro Tips

### For Developers

- Check `/backend/app.py` for Flask configuration
- Read `/backend/database/models.py` for database structure
- Use `/backend/routes/` to understand API patterns
- Enable logging: `FLASK_ENV=development`

### For Testing

- Use Postman/curl for API testing
- Create test admin with: `python backend/scripts/create_admin.py`
- Test user flow: Register → Login → Perform action
- Check database directly: `psql med_verify_db`

### For Production

- See [setup/DEPLOYMENT.md](setup/DEPLOYMENT.md) (coming soon)
- Never commit `.env` files
- Use strong secrets for FLASK_SECRET_KEY, JWT_SECRET_KEY
- Enable HTTPS in production
- Set up database backups

---

## ❓ FAQ

**Q: How do I run the project?**
A: See [setup/QUICKSTART.md](setup/QUICKSTART.md)

**Q: What's a medicine approval status?**
A: See [features/FEATURES.md](features/FEATURES.md) → Medicine Approval section

**Q: How does QR scanning work?**
A: See [api/ENDPOINTS.md](api/ENDPOINTS.md) → POST /scan endpoint

**Q: Why is my QR showing as counterfeit?**
A: See [troubleshooting/TROUBLESHOOTING.md](troubleshooting/TROUBLESHOOTING.md) → "QR Code Verification Shows Counterfeit"

**Q: Can I use the system without OpenAI API key?**
A: Yes, AI features are optional. System degrades gracefully.

**Q: How do I deploy to production?**
A: See [setup/DEPLOYMENT.md](setup/DEPLOYMENT.md) (coming soon)

---

## 📞 Support

**If documentation doesn't help:**

1. Check [troubleshooting/TROUBLESHOOTING.md](troubleshooting/TROUBLESHOOTING.md)
2. Review error logs: `/backend/logs/app.log`
3. Check browser console: F12 → Console tab
4. Verify your steps match a feature description
5. Restart both backend and frontend services

---

## 📝 Document Maintenance

Last Updated: January 2025

- Setup docs: Updated for current versions
- API docs: Synced with backend code
- Features: Reflects current implementation
- Troubleshooting: Contains known issues and solutions

---

**Happy building! 🚀**

For questions, check the appropriate doc or review the source code:

- Backend: `/backend/`
- Frontend: `/src/`
- Database: `/backend/database/`
