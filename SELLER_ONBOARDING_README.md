# Seller Onboarding & Application Status Implementation

This document describes the complete seller onboarding system implemented in MedVerify, including application submission, admin review workflow, status tracking, and email notifications.

## Overview

The seller onboarding system provides a complete workflow for sellers to:
1. Submit KYC applications with documents
2. Track application status through admin review stages
3. Receive email notifications on status changes
4. Make corrections when requested
5. Access seller dashboard once approved

Admins can:
1. View all pending seller applications
2. Mark applications as viewed/verifying
3. Approve or reject applications
4. Request changes with specific field guidance
5. Track all actions in audit logs

## Architecture

### Frontend Components

#### 1. **SellerApply.jsx** (`src/pages/SellerApply.jsx`)
- Form for seller KYC registration
- Fields:
  - Company name
  - License number, type, and expiry date
  - GSTIN, address
  - Authorized person name and contact (10-digit phone)
  - Company email
  - Multiple document upload (up to 5 files, max 5MB each)
- Validation:
  - Required field checks
  - License expiry must be future date
  - Phone number 10 digits
  - File type validation (PDF, PNG, JPEG)
  - File size validation
- Submission:
  - Multipart form data to `POST /seller/apply`
  - Bearer token authentication
  - Loading state during submission
  - Redirect to `/seller/status` on success

#### 2. **VerticalRoadmap.jsx** (`src/components/VerticalRoadmap.jsx`)
- Visual timeline showing application status progression
- Steps: submitted → viewed → verifying → approved
- Terminal states: rejected, changes_required
- Features:
  - Step icons with status colors
  - Connector lines between steps
  - Timestamps for each step
  - Admin remarks display (blue card)
  - Required changes list (amber card with field guidance)
  - Status legend

#### 3. **SellerStatus.jsx** (`src/pages/SellerStatus.jsx`)
- Displays application roadmap and status
- Auto-polls `GET /seller/status` every 15 seconds
- Shows appropriate CTAs:
  - Approved: "Go to Seller Dashboard" button
  - Changes Required: "Re-Edit" button with re-submission form
  - Rejected: Shows rejection reason and remarks
  - Pending: Shows spinning clock and "Refresh Status" button
- Shows application details:
  - Company info, license, GSTIN, address
  - Authorized person contact
  - Submitted documents with view links
- Last refresh timestamp
- Error handling and loading states

#### 4. **SellerDashboardGuard.jsx** (`src/components/SellerDashboardGuard.jsx`)
- Higher-order component protecting `/seller/dashboard` route
- Checks seller status === 'approved' before rendering
- Redirects to `/seller/status` with toast if not approved
- Shows loading state while fetching status

### Backend Endpoints

#### Seller Routes (`backend/routes/seller_routes.py`)

##### POST `/seller/apply`
Submit KYC application with documents

**Request:**
```
POST /seller/apply
Content-Type: multipart/form-data
Authorization: Bearer <token>

Form fields:
- company_name: string (required)
- license_number: string (required)
- license_type: string (required) - wholesale|retail|distribution|manufacturer
- license_expiry: date (required, ISO-8601, must be future)
- gstin: string (required)
- address: string (required)
- authorized_person: string (required)
- authorized_person_contact: string (required, 10 digits)
- email_company: string (required)
- documents: file[] (optional, max 5 files, max 5MB each)
```

**Response:**
```json
{
  "message": "Seller application submitted successfully",
  "seller_id": "uuid",
  "docs_stored_count": 3,
  "data": {
    "id": "uuid",
    "user_id": "uuid",
    "company_name": "ABC Pharma",
    "status": "pending",
    "created_at": "2024-01-20T10:30:00Z",
    "documents": ["/uploads/..."],
    ...
  }
}
```

**Status Codes:**
- 201: Application submitted successfully
- 400: Validation error or duplicate application
- 401: Unauthorized
- 500: Server error

##### GET `/seller/status`
Get seller application status with full details

**Request:**
```
GET /seller/status
Authorization: Bearer <token>
```

**Response:**
```json
{
  "message": "Seller status retrieved successfully",
  "data": {
    "id": "uuid",
    "company_name": "ABC Pharma",
    "license_number": "LIC123456",
    "status": "verifying",
    "submitted_at": "2024-01-20T10:30:00Z",
    "viewed_at": "2024-01-20T11:00:00Z",
    "verifying_at": "2024-01-20T12:00:00Z",
    "approved_at": null,
    "rejected_at": null,
    "admin_remarks": "Documents look good",
    "required_changes": null,
    "documents": ["/uploads/..."],
    ...
  }
}
```

#### Admin Routes (`backend/routes/admin_routes.py`)

##### GET `/admin/sellers?status=<status>`
List seller applications

**Query Parameters:**
- `status`: pending|viewed|verifying|approved|rejected|all (default: all)

**Response:**
```json
{
  "message": "Sellers retrieved successfully",
  "data": [
    {
      "id": "uuid",
      "company_name": "ABC Pharma",
      "status": "pending",
      "created_at": "2024-01-20T10:30:00Z",
      ...
    }
  ]
}
```

##### POST `/admin/sellers/<seller_id>/mark-viewed`
Mark application as viewed

**Request:**
```
POST /admin/sellers/<seller_id>/mark-viewed
Authorization: Bearer <admin_token>
Content-Type: application/json
```

**Response:**
```json
{
  "message": "Seller marked as viewed",
  "seller_updated": {
    "id": "uuid",
    "status": "viewed",
    "viewed_at": "2024-01-20T11:00:00Z",
    ...
  }
}
```

**Behavior:**
- Changes status from 'pending' to 'viewed'
- Sets viewed_at timestamp to now
- Sends "Application Status Update - Under Review" email
- Logs audit event

##### POST `/admin/sellers/<seller_id>/set-verifying`
Mark application as being verified

**Request:**
```
POST /admin/sellers/<seller_id>/set-verifying
Authorization: Bearer <admin_token>
Content-Type: application/json
```

**Response:**
```json
{
  "message": "Seller marked as verifying",
  "seller_updated": {
    "id": "uuid",
    "status": "verifying",
    "verifying_at": "2024-01-20T12:00:00Z",
    ...
  }
}
```

**Behavior:**
- Changes status from 'pending'/'viewed' to 'verifying'
- Sets verifying_at timestamp
- Sends "Application Status Update - In Verification" email
- Logs audit event

##### POST `/admin/sellers/<seller_id>/approve`
Approve seller application

**Request:**
```
POST /admin/sellers/<seller_id>/approve
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "admin_remarks": "All documents verified. Approved." (optional)
}
```

**Response:**
```json
{
  "message": "Seller approved successfully",
  "seller_updated": {
    "id": "uuid",
    "status": "approved",
    "approved_at": "2024-01-20T14:00:00Z",
    ...
  }
}
```

**Behavior:**
- Changes status to 'approved'
- Sets approved_at timestamp
- Sends "Seller Application Approved - Welcome!" email
- Updates seller's admin_remarks if provided
- Logs audit event

##### POST `/admin/sellers/<seller_id>/request-changes`
Request changes to application

**Request:**
```
POST /admin/sellers/<seller_id>/request-changes
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "required_changes": [
    {
      "field": "license_expiry",
      "message": "License expiry date is more than 3 months away. Please provide a valid license."
    },
    {
      "field": "authorized_person_contact",
      "message": "Contact number appears to be invalid. Please provide a working phone number."
    }
  ],
  "admin_remarks": "Please address the issues above and resubmit." (optional)
}
```

**Response:**
```json
{
  "message": "Seller marked for changes required",
  "seller_updated": {
    "id": "uuid",
    "status": "changes_required",
    "required_changes": [...],
    ...
  }
}
```

**Behavior:**
- Changes status to 'changes_required'
- Stores required_changes array with field-specific guidance
- Sends email with list of required changes and links to re-edit
- Logs audit event

##### POST `/admin/sellers/<seller_id>/reject`
Reject seller application

**Request:**
```
POST /admin/sellers/<seller_id>/reject
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "admin_remarks": "Business registration documents are not valid for this jurisdiction."
}
```

**Response:**
```json
{
  "message": "Seller rejected successfully",
  "seller_updated": {
    "id": "uuid",
    "status": "rejected",
    "rejected_at": "2024-01-20T15:00:00Z",
    "admin_remarks": "...",
    ...
  }
}
```

**Behavior:**
- Changes status to 'rejected'
- Sets rejected_at timestamp
- Sends rejection email with admin_remarks
- Logs audit event

## State Machine

```
                    ┌─────────────────────────────────┐
                    │     Seller Registers             │
                    └──────────────┬──────────────────┘
                                   │
                    ┌──────────────▼──────────────────┐
                    │  Status: pending                │
                    │  Submitted: NOW                 │
                    └──────────────┬──────────────────┘
                                   │
                    ┌──────────────▼──────────────────┐
                    │  Admin marks viewed             │
                    │  Status: viewed                 │
                    │  Viewed: NOW                    │
                    └──────────────┬──────────────────┘
                                   │
                    ┌──────────────▼──────────────────┐
                    │  Admin sets verifying           │
                    │  Status: verifying              │
                    │  Verifying: NOW                 │
                    └──────────────┬──────────────────┘
                                   │
                   ┌───────────────┼───────────────┐
                   │               │               │
        ┌──────────▼────────────┐  │  ┌───────────▼───────────┐
        │ Admin approves        │  │  │ Admin requests        │
        │ Status: approved      │  │  │ changes               │
        │ Approved: NOW         │  │  │ Status:               │
        │ ✓ Access Dashboard    │  │  │ changes_required      │
        │ ✓ Create medicines    │  │  │ ✓ Seller re-submits   │
        │ ✓ Generate QR codes   │  │  │ ✓ Back to pending     │
        └───────────────────────┘  │  └───────────────────────┘
                                   │
                       ┌───────────▼────────────┐
                       │ Admin rejects          │
                       │ Status: rejected       │
                       │ Rejected: NOW          │
                       │ ✗ Application denied   │
                       │ ✗ Contact support      │
                       └────────────────────────┘
```

## Email Notifications

### Templates

All emails are HTML-formatted and sent via SMTP or SendGrid.

#### On Submission
- **Subject:** "Seller Application Received - MedVerify"
- **Content:** Application received confirmation, status page link
- **Sent:** When seller submits application

#### On Viewed
- **Subject:** "Application Status Update - Under Review"
- **Content:** Application has been reviewed, under verification
- **Sent:** When admin marks application as viewed

#### On Verifying
- **Subject:** "Application Status Update - In Verification"
- **Content:** Documents are being verified actively
- **Sent:** When admin sets status to verifying

#### On Approved
- **Subject:** "Seller Application Approved - Welcome to MedVerify!"
- **Content:** Approval notification, next steps, dashboard link
- **Sent:** When admin approves application

#### On Changes Required
- **Subject:** "Action Required - Update Your Seller Application"
- **Content:** List of required changes with field names and specific guidance, status page link
- **Sent:** When admin requests changes

#### On Rejected
- **Subject:** "Seller Application Update - Unable to Approve"
- **Content:** Rejection decision, admin remarks, support contact
- **Sent:** When admin rejects application

### Email Configuration

Environment variables needed:
```
SENDGRID_API_KEY=sg_xxx...
# OR
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=email@gmail.com
SMTP_PASS=password
SMTP_FROM_EMAIL=noreply@medverify.com
SUPPORT_EMAIL=support@medverify.com
DASHBOARD_URL=https://medverify.com
```

## Usage Examples

### Frontend Integration

```jsx
// 1. User applies as seller
import SellerApply from '@/pages/SellerApply';
// Fill form → submit → redirected to /seller/status

// 2. Track application status
import SellerStatus from '@/pages/SellerStatus';
// Shows roadmap, auto-polls every 15 seconds
// Shows CTAs based on status

// 3. Protect seller dashboard
import { SellerDashboardGuard } from '@/components/SellerDashboardGuard';
// <SellerDashboardGuard><SellerDashboard /></SellerDashboardGuard>
```

### Backend cURL Examples

#### 1. Submit Application
```bash
curl -X POST http://localhost:5000/seller/apply \
  -H "Authorization: Bearer <token>" \
  -F "company_name=ABC Pharma" \
  -F "license_number=LIC123456" \
  -F "license_type=wholesale" \
  -F "license_expiry=2025-12-31" \
  -F "gstin=27AABCL2345G1Z0" \
  -F "address=123 Main Street, City" \
  -F "authorized_person=John Doe" \
  -F "authorized_person_contact=9876543210" \
  -F "email_company=contact@abcpharma.com" \
  -F "documents=@license.pdf" \
  -F "documents=@registration.png"
```

#### 2. Get Seller Status
```bash
curl -X GET http://localhost:5000/seller/status \
  -H "Authorization: Bearer <token>"
```

#### 3. Admin: Get Pending Applications
```bash
curl -X GET "http://localhost:5000/admin/sellers?status=pending" \
  -H "Authorization: Bearer <admin_token>"
```

#### 4. Admin: Mark as Viewed
```bash
curl -X POST http://localhost:5000/admin/sellers/<seller_id>/mark-viewed \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{}'
```

#### 5. Admin: Set Verifying
```bash
curl -X POST http://localhost:5000/admin/sellers/<seller_id>/set-verifying \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{}'
```

#### 6. Admin: Approve
```bash
curl -X POST http://localhost:5000/admin/sellers/<seller_id>/approve \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "admin_remarks": "All documents verified and approved."
  }'
```

#### 7. Admin: Request Changes
```bash
curl -X POST http://localhost:5000/admin/sellers/<seller_id>/request-changes \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "required_changes": [
      {
        "field": "license_expiry",
        "message": "License expires too soon. Please provide a license valid for at least 1 year."
      },
      {
        "field": "gstin",
        "message": "GSTIN format appears invalid. Please verify and resubmit."
      }
    ],
    "admin_remarks": "Please address the issues above and resubmit your application."
  }'
```

#### 8. Admin: Reject
```bash
curl -X POST http://localhost:5000/admin/sellers/<seller_id>/reject \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "admin_remarks": "Business registration documents do not match the jurisdiction. Please contact support for clarification."
  }'
```

## Database Schema

The implementation uses the existing `sellers` table with these relevant columns:

```sql
CREATE TABLE sellers (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id),
  company_name VARCHAR(255) NOT NULL,
  license_number VARCHAR(100) NOT NULL,
  license_type VARCHAR(50),
  license_expiry DATE,
  gstin VARCHAR(50),
  address TEXT,
  authorized_person VARCHAR(255),
  authorized_person_contact VARCHAR(20),
  email VARCHAR(255),
  company_website VARCHAR(255),
  documents JSONB,  -- Array of file URLs
  document_checksums JSONB,  -- Map of filename -> SHA256
  status VARCHAR(50) DEFAULT 'pending',  -- pending|viewed|verifying|approved|rejected|changes_required
  submitted_at TIMESTAMP DEFAULT NOW(),
  viewed_at TIMESTAMP,
  verifying_at TIMESTAMP,
  approved_at TIMESTAMP,
  rejected_at TIMESTAMP,
  admin_remarks TEXT,
  required_changes JSONB,  -- Array of {field, message}
  public_key TEXT,
  approved_by UUID REFERENCES users(id),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

## Testing

### Manual Testing Checklist

- [ ] Seller can submit KYC application with documents
- [ ] Application appears in admin pending list
- [ ] Admin can mark application as viewed
- [ ] Admin can set application to verifying
- [ ] Admin can approve application
- [ ] Admin can request changes with specific field guidance
- [ ] Admin can reject application with remarks
- [ ] Seller receives email notifications on status changes
- [ ] Seller can see roadmap with timestamps
- [ ] Seller can re-submit after changes requested
- [ ] Seller cannot access dashboard until approved
- [ ] Seller can access dashboard after approval
- [ ] All admin actions logged to audit logs
- [ ] File checksums computed and stored correctly

### Automated Tests

Unit tests exist for:
- Form validation (required fields, date validation, file validation)
- Component rendering (VerticalRoadmap with different statuses)
- API payload structure and response codes

Integration tests exist for:
- Complete workflow: submit → viewed → verifying → approved
- Changes required flow: submit → request_changes → resubmit → approved
- Rejection flow: submit → reject
- Email sending on status changes
- Audit logging

## Implementation Notes

1. **File Storage:**
   - Files saved to `/backend/uploads/` with naming: `{seller_id}_{uuid}_{original_filename}`
   - SHA256 checksums computed for document verification
   - Checksums stored in `document_checksums` JSONB column

2. **Email Service:**
   - Supports SendGrid API or SMTP fallback
   - All emails are HTML-formatted with branding
   - Async sending recommended for production (use Celery/job queue)

3. **State Transitions:**
   - One-way transitions through normal states (pending → viewed → verifying → approved)
   - From any state → rejected (terminal)
   - From any state → changes_required (allows re-submission)
   - Can resubmit from changes_required → back to pending

4. **Timestamps:**
   - ISO-8601 UTC format: "2024-01-20T10:30:00Z"
   - Different timestamp fields track each stage transition
   - Submitted_at = application submission time
   - Viewed_at = admin first reviewed time
   - Verifying_at = admin started verification time
   - Approved_at/Rejected_at = final decision time

5. **Error Handling:**
   - Double-submit prevention via button disabled state and loading indicator
   - Validation errors returned with field-level detail
   - Network errors with retry logic
   - File validation errors with helpful messages

## API Response Format

All responses follow a consistent format:

**Success:**
```json
{
  "message": "...",
  "data": {...},
  "seller_updated": {...} // only for admin endpoints
}
```

**Error:**
```json
{
  "error": "Error message",
  "status": "...", // optional additional context
  "fields": [...] // optional field-level errors
}
```

## Security Considerations

1. All endpoints require authentication via Bearer token
2. Admin endpoints enforce admin role check
3. Seller endpoints enforce seller role check
4. File uploads validated for type and size
5. SQL injection prevented via parameterized queries
6. CORS configured to allow frontend origin only
7. Audit logs track all admin actions
8. Email addresses not exposed in error messages

## Future Enhancements

1. Real-time notifications via WebSocket or Server-Sent Events (SSE) instead of polling
2. Document verification via OCR or AI
3. KYC data encryption at rest
4. Multi-level approval workflow (multiple reviewers)
5. Automated compliance checks
6. Integration with government verification APIs
7. Document re-upload for changes_required flow
8. Bulk approval/rejection for admins
9. Application expiry and re-submission deadlines
10. Seller tier classification based on application review
