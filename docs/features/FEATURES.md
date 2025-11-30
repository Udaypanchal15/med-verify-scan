# Features Guide - Medicine Verification Scanner

## 📚 Complete Feature List

### 🧑‍⚕️ User Features

#### 1. **QR Code Scanning**

- Scan physical QR codes using device camera
- Upload image with QR code
- Manually enter QR data
- Real-time verification results

**Access**: Home page → "Medicine Verification Scanner" section

**What it shows:**

- ✅ Verified medicines (authentic, approved by admin)
- ⚠️ Expired medicines (authentic but past expiry date)
- ❌ Counterfeit/Unknown (not in system or signature verification failed)
- 🚫 Unverified medicines (not approved by admin yet)

**Unverified Medicine Warning**:
When you scan a medicine that exists in database but isn't approved:

- Yellow warning banner appears
- Shows "Use at your own risk"
- Provides recommendations to verify directly with manufacturer

---

#### 2. **Medicine Search Database**

- Search by medicine name
- Search by batch number
- Filter by seller/company
- View complete medicine information

**Access**: Navigation → "My Dashboard" (for users) → Search tab

**Results show:**

- Medicine name and dosage
- Manufacturing and expiry dates
- Batch number
- Seller/Company information
- Verification status (✓ Verified)

---

#### 3. **AI Medicine Assistant**

- Ask questions about medicines
- Get health information
- AI-powered responses
- Multi-turn conversation

**Access**: Home page → "AI Medicine Assistant" section

**Features:**

- Natural language questions
- Context-aware responses
- Safe health guidance
- Disclaimer about consulting professionals

---

### 🏢 Seller Features

#### 1. **KYC Application**

- Register as seller
- Submit company details
- Upload licensing documents
- Track approval status

**Access**: Register → Select "Seller" role → Fill KYC form

**Status Tracking:**

- 🟡 **Pending**: Waiting for admin approval
- 🟢 **Approved**: Can now manage medicines and generate QR codes
- 🔴 **Rejected**: Review reason and reapply

---

#### 2. **ECDSA Key Generation**

- Generate cryptographic key pair
- Securely store private key
- Display public key for reference
- One-time generation per seller

**Access**: Seller Dashboard → "Generate ECDSA Keys"

**What it does:**

- Creates P-256 elliptic curve cryptography keys
- Private key stored securely on backend
- Public key used for QR code signing
- Required before issuing QR codes

---

#### 3. **Medicine Management**

- Add new medicines to inventory
- Enter medicine details (name, dosage, strength, batch, dates)
- Upload medicine images (optional)
- Edit medicine information
- Track approval status

**Access**: Seller Dashboard → "Your Medicines"

**Status Workflow:**

1. Seller adds medicine
2. Medicine appears as "🟡 Pending" (awaiting admin approval)
3. Admin reviews and approves
4. Medicine shows as "🟢 Approved"
5. Seller can now generate QR codes

---

#### 4. **QR Code Generation**

- Generate QR code for each medicine unit
- Embed medicine metadata in QR
- Sign QR with ECDSA signature
- Download QR code image
- Multiple QR codes per medicine

**Access**: Seller Dashboard → Click "Generate QR Code" on approved medicine

**QR Contains:**

- Medicine ID
- Batch number
- Manufacturing date
- Expiry date
- Seller ID
- ECDSA Signature (for verification)

---

### 👨‍💼 Admin Features

#### 1. **Seller Management**

View and manage all seller applications

**Access**: Admin Dashboard → "Sellers" tab

**Available Actions:**

- 📋 View pending applications
- ✅ Approve seller (allows medicine uploads)
- ❌ Reject seller (with optional reason)
- 🚫 Revoke seller (deactivates all QR codes)
- View seller company details and license

---

#### 2. **Medicine Verification**

Review and approve medicines before they're visible to users

**Access**: Admin Dashboard → "Medicines" tab

**Medicine Approval Workflow:**

1. Seller submits medicine
2. Admin sees it in "Pending" status
3. Admin reviews details
4. Admin clicks "Approve" or "Reject"
5. Approved medicines shown to users as verified
6. Users see "Use at own risk" for pending medicines

**Approval Prevents:**

- Counterfeit medicines showing as verified
- Unvetted products reaching users
- Fraudulent sellers distributing fake medicines

---

#### 3. **System Analytics**

View dashboard with system-wide statistics

**Access**: Admin Dashboard → "Analytics" tab

**Metrics Displayed:**

- Total sellers (active, approved)
- Total medicines (approved, pending)
- Total QR codes issued
- Revoked QR codes (detected counterfeits)
- Scan results breakdown:
  - ✅ Verified scans
  - ⚠️ Expired medicines
  - ❌ Counterfeit detected
  - 🚫 Unverified/unknown
  - ❌ Errors

---

#### 4. **Audit Logs**

Track all admin actions for security and compliance

**Access**: Admin Dashboard → "Audit Logs" (can add tab)

**Tracks:**

- Seller approvals/rejections
- Medicine approvals/rejections
- Key revocations
- Admin account activities
- Timestamps and responsible admin

---

### 🔐 Security Features (All Roles)

#### 1. **ECDSA Digital Signatures**

- QR codes cryptographically signed
- Prevents tampering and counterfeiting
- Seller's public key embedded in QR
- Verification fails if signature invalid or key revoked

#### 2. **JWT Authentication**

- Secure token-based authentication
- Automatic token refresh
- Role-based access control
- Session management

#### 3. **Role-Based Access Control (RBAC)**

- Users can only access their role's features
- Admins cannot be assigned except by script
- Sellers cannot approve their own medicines
- Protected routes prevent unauthorized access

#### 4. **Input Validation**

- Email format validation
- Password complexity requirements
- File upload validation (size, type)
- SQL injection prevention

---

## Workflow Examples

### Example 1: New Seller Selling Medicine

```
1. Seller registers with role "Seller"
   ↓
2. Fills KYC form (company name, license)
   ↓
3. Admin approves seller
   ↓
4. Seller generates ECDSA keys
   ↓
5. Seller adds medicine (name, batch, dates, etc.)
   ↓
6. Admin reviews and approves medicine
   ↓
7. Seller generates QR code for medicine unit
   ↓
8. User scans QR → Sees "✅ Verified"
```

### Example 2: User Verifying Unknown Medicine

```
1. User has medicine without QR
   ↓
2. Tries scanning with app (fails)
   ↓
3. Searches medicine in database (not found)
   ↓
4. System shows warning: "Not verified by our platform"
   ↓
5. User recommendations:
   - Contact manufacturer directly
   - Check physical packaging
   - Consult healthcare professional
   - Report to authorities if suspicious
```

### Example 3: Counterfeit Detection

```
1. User scans QR code
   ↓
2. Signature verification fails (tampering detected)
   OR public key is revoked
   ↓
3. System shows: "❌ Counterfeit Detected"
   ↓
4. Recommendation: Do not use, report to authorities
```

---

## Feature Status

| Feature                  | Status      | Notes                              |
| ------------------------ | ----------- | ---------------------------------- |
| User Registration/Login  | ✅ Complete | JWT-based auth                     |
| QR Code Scanning         | ✅ Complete | Camera & manual input              |
| Medicine Database Search | ✅ Complete | Text search                        |
| AI Assistant             | ✅ Complete | OpenAI integration                 |
| Seller KYC               | ✅ Complete | Document upload                    |
| Medicine Management      | ✅ Complete | CRUD operations                    |
| QR Generation            | ✅ Complete | ECDSA signing                      |
| Admin Dashboard          | ✅ Complete | Approvals & analytics              |
| Blockchain               | 🟡 Partial  | Contracts written, routes disabled |
| Notifications            | 🟡 Partial  | Backend ready, UI pending          |
| Reminders                | 🟡 Partial  | Backend ready, UI pending          |

---

See `/docs/api/` for detailed endpoint documentation.
