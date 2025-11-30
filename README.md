# Med Verify Scan

A comprehensive medicine verification and anti-counterfeiting system combining blockchain technology, QR code scanning, and AI-powered authentication.

## 🎯 Overview

Med Verify Scan is an enterprise-grade solution designed to:
- **Verify Medicine Authenticity** - Detect counterfeit medicines through QR code verification
- **Track Medicine Supply Chain** - Monitor medications from manufacturer to patient
- **Prevent Fraud** - Use blockchain anchoring and cryptographic signatures
- **Empower Users** - Enable consumers, healthcare providers, and regulatory authorities to verify medicines

## 🌟 Key Features

### For Consumers
- **Quick QR Scan** - Scan medicine packaging to verify authenticity instantly
- **Batch Information** - View manufacturing and expiry details
- **Medicine Directory** - Search and browse verified medicines
- **Safety Alerts** - Get notified about recalled or counterfeit batches

### For Healthcare Providers
- **Bulk Verification** - Verify multiple medicines at once
- **Reports & Analytics** - Track authentic vs. suspicious medicines
- **Patient Alerts** - Flag counterfeit medicines for patient safety
- **Audit Trails** - Complete supply chain documentation

### For Medicine Sellers/Distributors
- **Seller Dashboard** - Manage profile and medicines
- **Batch Registration** - Upload medicine batches with verification details
- **Performance Metrics** - Track reputation and customer trust
- **Admin Approval System** - Streamlined onboarding process

### For Administrators
- **User Management** - Approve and manage sellers
- **Medicine Verification** - Review and approve batches
- **Reporting Tools** - Generate comprehensive system reports
- **Fraud Detection** - Monitor suspicious patterns

## 📋 System Architecture

### Frontend
- **Framework**: React + Vite
- **Language**: JavaScript/JSX
- **Styling**: Tailwind CSS + PostCSS
- **Key Components**: Scanning interface, dashboard, user management

### Backend
- **Framework**: Flask (Python)
- **Database**: MySQL
- **Authentication**: JWT tokens with secure middleware
- **Blockchain**: Solidity smart contracts (anchoring)

### Database Schema
- `users` - User profiles (consumers, sellers, admins)
- `medicines` - Medicine master data
- `batches` - Medicine batch information
- `scans` - Medicine scan records and verification history
- `sellers` - Seller profiles and verification status
- `seller_medicines` - Medicine inventory management

## 🚀 Quick Start

### Prerequisites
- Node.js 16+ and npm/bun
- Python 3.8+
- MySQL 8.0+
- Git

### Installation

#### 1. Clone the Repository
```bash
git clone <repository-url>
cd med-verify-scan-main
```

#### 2. Frontend Setup
```bash
npm install
# or
bun install
```

#### 3. Backend Setup
```bash
cd backend
pip install -r requirements.txt
```

#### 4. Database Setup
```bash
# Create MySQL database
mysql -u root -p < database/schema.sql

# Run migrations
python database/migrate.py
```

#### 5. Configuration
Create `.env` file in the backend directory:
```
FLASK_ENV=development
DATABASE_URL=mysql+pymysql://user:password@localhost/med_verify
SECRET_KEY=your-secret-key
JWT_SECRET=your-jwt-secret
```

### Running the Application

#### Start Frontend
```bash
npm run dev
# Application available at http://localhost:5173
```

#### Start Backend
```bash
cd backend
python app.py
# API available at http://localhost:5000
```

## 📖 API Documentation

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/profile` - Get current user profile

### Medicine Verification
- `POST /api/scan/verify` - Verify medicine by QR code
- `GET /api/medicines` - Get medicine list
- `GET /api/medicines/:id` - Get medicine details
- `GET /api/batches/:batchId` - Get batch information

### Seller Management
- `POST /api/seller/register` - Register as seller
- `GET /api/seller/profile` - Get seller profile
- `POST /api/seller/medicines` - Add medicine to inventory
- `GET /api/seller/medicines` - Get seller's medicines

### Admin Operations
- `GET /api/admin/users` - List all users
- `POST /api/admin/approve-seller/:id` - Approve seller
- `GET /api/admin/medicines/pending` - Pending medicine approvals
- `POST /api/admin/medicines/verify/:id` - Verify medicine batch

See [API_DOCUMENTATION.md](./backend/API_DOCUMENTATION.md) for complete API reference.

## 📚 Documentation

- **[Setup Guide](./COMPLETE_SETUP_GUIDE.md)** - Complete installation instructions
- **[API Documentation](./backend/API_DOCUMENTATION.md)** - Full API reference
- **[Database Schema](./backend/database/schema.sql)** - Database structure
- **[Blockchain Guide](./backend/BLOCKCHAIN_GUIDE.md)** - Smart contract details
- **[Seller Onboarding](./SELLER_ONBOARDING_README.md)** - Seller workflow guide
- **[Troubleshooting](./docs/troubleshooting/)** - Common issues and solutions

## 🔐 Security Features

- **JWT Authentication** - Secure token-based authentication
- **Password Hashing** - Bcrypt with salt for password security
- **HTTPS/TLS** - Encrypted data transmission
- **SQL Injection Prevention** - Parameterized queries
- **CORS Protection** - Cross-origin request validation
- **Rate Limiting** - API rate limiting to prevent abuse
- **Blockchain Anchoring** - Immutable record anchoring

## 🧪 Testing

### Run Tests
```bash
# Frontend tests
npm run test

# Backend tests
cd backend
pytest

# Coverage report
pytest --cov=routes tests/
```

### Manual Testing Credentials
Test seller account (created via migrations):
- Email: `test.seller@medicine.com`
- Password: `TestSeller@123`

Test admin account:
- Email: `admin@medicine.com`
- Password: `Admin@123`

## 📁 Project Structure

```
med-verify-scan-main/
├── src/                    # Frontend React components
│   ├── components/        # Reusable UI components
│   ├── pages/            # Page components
│   ├── hooks/            # Custom React hooks
│   └── lib/              # Utility functions
├── backend/              # Flask backend
│   ├── routes/          # API endpoints
│   ├── database/        # Database models & migrations
│   ├── middleware/      # Authentication & security
│   ├── services/        # Business logic
│   ├── scripts/         # Utility scripts
│   └── contracts/       # Smart contracts (Solidity)
├── docs/                # Documentation
└── public/              # Static assets
```

## 🛠️ Development Workflow

### Making Changes
1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes and test thoroughly
3. Commit with clear messages: `git commit -m "Add: description"`
4. Push to remote: `git push origin feature/your-feature`
5. Create a Pull Request on GitHub

### Code Standards
- Follow PEP 8 for Python code
- Use ESLint for JavaScript/React
- Add comments for complex logic
- Write tests for new features
- Keep commits atomic and meaningful

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:
1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request with description

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check [Troubleshooting Documentation](./docs/troubleshooting/)
- Review existing issues and discussions

## 🔄 Changelog

### Version 1.0.0 (Latest)
- ✅ Complete medicine verification system
- ✅ Blockchain anchoring for immutability
- ✅ Admin approval workflow
- ✅ Seller dashboard
- ✅ QR code scanning
- ✅ Supply chain tracking
- ✅ AI-powered authentication

### Recent Fixes
- Fixed email case sensitivity in database
- Improved seller profile validation
- Enhanced security middleware
- Optimized database queries

## 🎓 Learning Resources

- [React Documentation](https://react.dev)
- [Flask Documentation](https://flask.palletsprojects.com)
- [MySQL Documentation](https://dev.mysql.com/doc)
- [Blockchain Basics](./backend/BLOCKCHAIN_GUIDE.md)
- [Smart Contracts Guide](./backend/ECDSA_SIGNING_GUIDE.md)

---

**Built with ❤️ for medicine safety and authenticity verification**

Last Updated: 2024
