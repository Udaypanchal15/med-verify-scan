# Complete Setup & Testing Guide

## Test Credentials

### For Test Seller Account

**Email**: test@test.com  
**Password**: Test1234

To set up this account:
1. Run the SQL script: `CREATE_TEST_SELLER_PROFILE.sql`
2. This will:
   - Create approved seller profile
   - Add 3 sample medicines with different stock levels
   - Set delivery status tracking

### For New Seller (seller1234@gmail.com)

**Email**: seller1234@gmail.com  
**Password**: Test1234

**Process**:
1. Register with this email as "seller" role
2. Login - will be redirected to company registration
3. Fill company details:
   - Company Name: e.g., "My Pharma Ltd"
   - License Number: e.g., "LIC-2024-001"
   - License Type: e.g., "Manufacturing License"
   - License Expiry: Future date
   - GSTIN: e.g., "29ABCDE1234F1Z5"
   - Address: e.g., "123 Main Street"
   - Authorized Person: e.g., "John Doe"
   - Contact: e.g., "9876543210"
   - Company Email: e.g., "info@mypharmacy.com"
4. Upload documents (PDF/PNG/JPEG, max 5MB each, max 5 files)
5. Submit - redirected to status page

---

## Features Overview

### Main Page (Index.jsx)
- **Showcase only** - No functional features
- Display platform capabilities
- CTA buttons for different roles
- Feature cards with descriptions

### Seller Dashboard

#### 1. Seller Profile Section
- Company name, license number
- Status badge (approved/pending/rejected)
- Business profile information
- KYC application status tracking

#### 2. Add Medicine Form
- Fields: name, batch_no, strength, dosage, category, stock_quantity, delivery_status, mfg_date, expiry_date
- Quick add from dashboard tab
- Optional medical usage and manufacturer info

#### 3. Medicine Management (Full Database)
Navigate via:
- Navigation bar: "Medicines" link
- Dashboard: "Go to Medicine Database" button
- URL: `/seller/medicines`

**Features**:
- Add new medicines with stock tracking
- Search by name/batch number
- Filter by delivery status (in_stock, pending, delivered, discontinued)
- Statistics: total, in stock, pending, delivered
- Color-coded stock levels:
  - Red: 0 units (out of stock)
  - Amber: 1-9 units (low stock)
  - Green: 10+ units (sufficient)
- QR code generation for medicines
- Expandable add form

### Admin Dashboard

#### Medicine Management
Navigate via:
- Navigation bar: "Medicines" link
- URL: `/admin/medicines`

**Features**:
- View all sellers and their medicines
- Expandable seller cards
- Search sellers by name/license
- Statistics: approved sellers, total sellers, total medicines
- Hierarchical view:
  - Click seller to expand
  - See all their medicines
  - Medicine details with stock levels
- Seller status badges with color coding

---

## API Endpoints

### Seller Endpoints
- `POST /seller/apply` - Submit KYC application
- `GET /seller/status` - Get seller approval status
- `POST /seller/medicine` - Create new medicine
- `GET /seller/medicine` - Get seller's medicines
- `GET /seller/medicine/<id>` - Get specific medicine
- `POST /seller/issue-qr` - Generate QR code

### Admin Endpoints
- `GET /admin/sellers` - Get all sellers
- `GET /admin/sellers/medicines` - Get all medicines hierarchical
- `POST /admin/sellers/<id>/approve` - Approve seller
- `POST /admin/medicines/<id>/approve` - Approve medicine
- `POST /admin/medicines/<id>/reject` - Reject medicine

---

## Testing Workflow

### Test 1: Approved Seller (test@test.com)
1. Login with test@test.com / Test1234
2. Directed to seller dashboard
3. See medicines that were added via SQL script
4. Can add new medicines from dashboard
5. Visit "Medicines" link to see full database
6. Try generating QR codes

### Test 2: New Seller Registration (seller1234@gmail.com)
1. Register new seller account
2. Redirected to company registration form
3. ✅ FIX APPLIED: Now submits without "invalid token" error
4. Token issue was:
   - Using wrong storage key (localStorage.getItem('token') instead of 'access_token')
   - Now uses getAccessToken() from auth library
   - Correctly sends Authorization header without Content-Type
5. After approval by admin, seller can access full features

### Test 3: Admin View
1. Login as admin (or use /admin/dashboard)
2. Click "Medicines" in navigation
3. See all approved sellers
4. Click seller to expand and view their medicines
5. Search and filter sellers
6. View statistics

---

## Database Schema Fields

### Sellers Table
```
id (UUID)
user_id (UUID) - FK users
company_name (VARCHAR)
license_number (VARCHAR UNIQUE)
license_type (VARCHAR)
license_expiry (DATE)
gstin (VARCHAR)
address (TEXT)
authorized_person (VARCHAR)
authorized_person_contact (VARCHAR)
email (VARCHAR) ← Now populated during registration
status (VARCHAR) - pending/approved/rejected/revoked
public_key (TEXT)
approved_at (TIMESTAMP)
approved_by (UUID) - FK users
created_at (TIMESTAMP)
updated_at (TIMESTAMP)
```

### Medicines Table
```
id (UUID)
seller_id (UUID) - FK sellers
name (VARCHAR)
batch_no (VARCHAR)
mfg_date (DATE)
expiry_date (DATE)
dosage (VARCHAR)
strength (VARCHAR)
category (VARCHAR)
description (TEXT)
image_url (TEXT)
approval_status (VARCHAR) - pending/approved/rejected
stock_quantity (INTEGER) ← NEW FIELD
delivery_status (VARCHAR) ← NEW FIELD: in_stock/pending/delivered/discontinued
created_at (TIMESTAMP)
updated_at (TIMESTAMP)
```

---

## Common Issues & Fixes

### Issue: "Invalid token" on seller registration
**Cause**: Token not being read from correct localStorage key  
**Fix**: ✅ Applied - Uses getAccessToken() from auth library

### Issue: Files not uploading
**Cause**: Wrong file types or size  
**Solution**: Only PDF, PNG, JPEG allowed (max 5MB each, max 5 files)

### Issue: Seller can't see medicines
**Cause**: Seller not approved  
**Solution**: Admin must approve seller first via /admin/sellers

### Issue: No delivery_status in form
**Cause**: Field not in form state  
**Fix**: ✅ Applied - Added delivery_status to medicine form

---

## Quick Commands

### View Test Seller
```bash
# Login shell
cd backend
psql

# Query
SELECT email, status FROM sellers 
WHERE user_id = (SELECT id FROM users WHERE email = 'test@test.com');

# Should show: test@test.com | approved
```

### Check Medicines
```sql
SELECT name, batch_no, stock_quantity, delivery_status 
FROM medicines 
WHERE seller_id = (
  SELECT s.id FROM sellers s 
  WHERE s.user_id = (SELECT id FROM users WHERE email = 'test@test.com')
);
```

### Run Test SQL
```bash
psql -U postgres -d medverify -f CREATE_TEST_SELLER_PROFILE.sql
```

---

## Status

✅ **All Features Implemented**
- Medicine database (seller & admin)
- Stock tracking with color coding
- Delivery status management
- Token issue fixed for seller registration
- Delivery status form field added
- Test data setup script ready

🎯 **Next Steps**
1. Run SQL script to set up test seller
2. Test seller login and medicine management
3. Test new seller registration (should work now without token error)
4. Verify admin can see all medicines
5. Test QR code generation

