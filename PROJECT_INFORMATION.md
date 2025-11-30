# QR Code Tracker and Alerting Using AI - Project Information

## 📖 Project Overview

**Project Name**: QR Code Tracker and Alerting Using AI  
**Version**: 1.0.0  
**Type**: University Mini-Project  
**Domain**: Medicine Verification & Healthcare

## 🎯 Project Objectives

1. **Medicine Authenticity Verification**: Verify medicine authenticity using QR codes, ECDSA signatures, and blockchain
2. **AI-Powered Verification**: Use OCR and image verification to enhance security
3. **Reminder System**: Provide medicine dosage and expiry reminders
4. **Multi-role System**: Support users, sellers, and admins
5. **Blockchain Integration**: Anchor QR code issuances on blockchain for auditability

## 🏗️ System Architecture

### Technology Stack

#### Frontend
- **React 18** - UI framework
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Shadcn UI** - Component library
- **html5-qrcode** - QR code scanning
- **React Router** - Routing

#### Backend
- **Flask** - Web framework
- **PostgreSQL** - Database
- **Redis** - Caching (optional)
- **JWT** - Authentication
- **Web3.py** - Blockchain integration
- **TensorFlow** - AI/ML models
- **OpenCV** - Image processing
- **pytesseract** - OCR

#### Blockchain
- **Ethereum/Polygon** - Blockchain network
- **Solidity** - Smart contracts
- **Web3.py** - Blockchain interaction

#### AI Services
- **OCR** - Text extraction from images
- **Image Verification** - Packaging verification using CNNs
- **LLM** - Medicine information summarization

## 🔐 Security Features

1. **ECDSA Signing**: Cryptographic signing of QR codes
2. **JWT Authentication**: Secure token-based authentication
3. **Role-Based Access Control**: User, seller, admin roles
4. **Key Revocation**: Ability to revoke compromised keys
5. **Blockchain Anchoring**: Immutable record of issuances
6. **Input Validation**: Server-side validation of all inputs
7. **Rate Limiting**: Protection against abuse
8. **Security Headers**: XSS, CSRF protection
9. **Password Hashing**: bcrypt for password security
10. **Audit Logging**: Comprehensive audit trails

## 📊 Database Schema

### Core Tables

1. **users** - User accounts
2. **sellers** - Pharmaceutical companies
3. **medicines** - Medicine records
4. **qr_codes** - QR code issuances
5. **revoked_keys** - Revoked seller keys
6. **scan_logs** - QR code scan history
7. **reminders** - Medicine reminders
8. **notification_logs** - Notification delivery logs
9. **audit_logs** - Admin action logs
10. **device_tokens** - Push notification tokens

## 🔄 Workflows

### Seller Registration Flow

1. User registers with role "seller"
2. Seller applies for KYC with company details
3. Admin reviews and approves/rejects
4. Approved seller generates ECDSA key pair
5. Seller can create medicines and issue QR codes

### QR Code Issuance Flow

1. Seller creates medicine record
2. Seller issues QR code for medicine
3. System signs QR code with seller's private key
4. QR code is anchored on blockchain
5. QR code is stored in database
6. QR code returned to seller

### QR Code Verification Flow

1. User scans QR code
2. System extracts payload and signature
3. System verifies signature with seller's public key
4. System checks if key is revoked
5. System verifies QR code in database
6. System checks blockchain anchoring
7. System performs OCR and image verification (if image provided)
8. System returns verification result with AI summary

### Reminder Flow

1. User creates reminder with recurrence rule
2. Reminder stored in database
3. Reminder worker checks for due reminders
4. Notifications sent via email/push/SMS
5. Next run time calculated for recurring reminders
6. Reminder deactivated when complete

## 🎨 Frontend Features

### User Interface
- **Homepage** - Landing page with features
- **QR Scanner** - Scan QR codes using webcam or file upload
- **Medicine Database** - Search and view medicines
- **AI Assistant** - Get AI-powered medicine information
- **Reminders** - Create and manage reminders
- **Scan History** - View past scans
- **Profile** - User profile and settings

### Seller Dashboard
- **KYC Application** - Apply for seller status
- **Medicine Management** - CRUD operations for medicines
- **QR Issuance** - Issue signed QR codes
- **Issuance History** - View issued QR codes
- **Analytics** - View seller statistics

### Admin Dashboard
- **Seller Management** - Approve/reject sellers
- **Key Management** - Revoke seller keys
- **Analytics** - System-wide analytics
- **Audit Logs** - View audit trail
- **System Settings** - Configure system

## 🔌 API Endpoints Summary

### Authentication (5 endpoints)
- Register, login, refresh, me, logout

### Seller (7 endpoints)
- Apply KYC, status, generate keys, medicine CRUD, issue QR, history

### Admin (6 endpoints)
- Get sellers, approve, reject, revoke, analytics, audit logs

### Scan (4 endpoints)
- Scan QR, scan image, history, search

### Reminders (5 endpoints)
- Create, get, update, delete, register device token

### Blockchain (2 endpoints)
- Info, verify

### Medicine (1 endpoint)
- Get medicine info

## 🧪 Testing

### Unit Tests
- ECDSA signing/verification
- QR code generation
- Authentication
- Database models

### Integration Tests
- API endpoints
- Database operations
- Blockchain integration
- AI services

### Manual Testing
- User flows
- Seller flows
- Admin flows
- Error scenarios

## 📈 Performance Considerations

1. **Database Indexing**: Indexed on frequently queried fields
2. **Connection Pooling**: Database connection pooling
3. **Caching**: Redis for caching (optional)
4. **Rate Limiting**: Prevent abuse
5. **Async Processing**: Background workers for reminders
6. **Image Optimization**: Compress images before storage
7. **Batch Operations**: Batch blockchain transactions

## 🔮 Future Enhancements

1. **Mobile App** - React Native mobile app
2. **Advanced AI** - More sophisticated image verification
3. **Multi-language Support** - Internationalization
4. **Advanced Analytics** - Machine learning for fraud detection
5. **Integration** - Integration with pharmacy systems
6. **API Rate Limiting** - More sophisticated rate limiting
7. **WebSocket** - Real-time notifications
8. **GraphQL** - GraphQL API alternative

## 📚 Documentation Files

- `PROJECT_SETUP_GUIDE.md` - Detailed setup instructions
- `START_PROJECT.md` - Quick start guide
- `backend/API_DOCUMENTATION.md` - API documentation
- `backend/BLOCKCHAIN_GUIDE.md` - Blockchain setup guide
- `backend/AI_SERVICES_GUIDE.md` - AI services guide
- `backend/ECDSA_SIGNING_GUIDE.md` - ECDSA signing guide
- `backend/ENV_SETUP.md` - Environment variables guide

## 🛠️ Development Tools

- **VS Code** - Recommended IDE
- **Postman** - API testing
- **pgAdmin** - Database management
- **Metamask** - Blockchain wallet
- **Remix IDE** - Smart contract development

## 📝 Code Standards

- **Python**: PEP 8 style guide
- **JavaScript**: ESLint configuration
- **Git**: Conventional commits
- **Documentation**: Docstrings for all functions
- **Testing**: pytest for backend, Jest for frontend

## 🔒 Security Best Practices

1. **Never commit secrets** to version control
2. **Use environment variables** for configuration
3. **Validate all inputs** on server-side
4. **Use HTTPS** in production
5. **Implement rate limiting**
6. **Regular security audits**
7. **Keep dependencies updated**
8. **Use strong passwords**
9. **Implement proper error handling**
10. **Log security events**

## 📊 Project Statistics

- **Backend Routes**: ~30 endpoints
- **Database Tables**: 10 tables
- **Services**: 10+ services
- **Frontend Components**: 20+ components
- **Test Coverage**: Unit tests for critical paths
- **Documentation**: 7+ documentation files

## 🎓 Educational Value

This project demonstrates:
- Full-stack development
- Blockchain integration
- AI/ML integration
- Security best practices
- Database design
- API design
- Authentication and authorization
- Real-time systems
- System architecture

## 🙏 Acknowledgments

- Flask community
- React community
- PostgreSQL community
- Ethereum community
- OpenAI for LLM services
- All open-source contributors

## 📄 License

This project is for educational purposes only.

---

**Project Status**: ✅ Complete (Steps 1-12)  
**Last Updated**: January 2025  
**Maintainer**: Development Team



