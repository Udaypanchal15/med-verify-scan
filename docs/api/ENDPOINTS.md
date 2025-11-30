# API Documentation - Medicine Verification Scanner

## Base URL

```
http://localhost:5000
```

## Authentication

All protected endpoints require JWT token in Authorization header:

```
Authorization: Bearer <access_token>
```

---

## Authentication Endpoints

### POST /auth/register

Register a new user

**Request:**

```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "role": "user" // "user", "seller", or "admin"
}
```

**Response (201):**

```json
{
  "message": "User registered successfully",
  "data": {
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "role": "user",
      "created_at": "2024-01-01T00:00:00Z"
    },
    "access_token": "jwt_token",
    "refresh_token": "refresh_token"
  }
}
```

---

### POST /auth/login

Login and get tokens

**Request:**

```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response (200):**

```json
{
  "message": "Login successful",
  "data": {
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "role": "user"
    },
    "access_token": "jwt_token",
    "refresh_token": "refresh_token"
  }
}
```

---

### POST /auth/refresh

Refresh access token

**Headers:**

```
Authorization: Bearer <refresh_token>
```

**Response (200):**

```json
{
  "message": "Token refreshed successfully",
  "data": {
    "access_token": "new_jwt_token"
  }
}
```

---

## Medicine Endpoints

### GET /medicines

Get all approved medicines

**Query Parameters:**

- `q` (optional): Search query
- `category` (optional): Filter by category
- `limit` (optional): Results per page (default: 50)
- `offset` (optional): Pagination offset (default: 0)

**Response (200):**

```json
{
  "message": "Medicines retrieved",
  "data": [
    {
      "id": "medicine-uuid",
      "name": "Paracetamol 500mg",
      "batch_no": "BATCH001",
      "mfg_date": "2024-01-15",
      "expiry_date": "2026-01-15",
      "dosage": "500mg",
      "strength": "500mg",
      "category": "Painkiller",
      "description": "Pain relief medicine",
      "approval_status": "approved",
      "seller_id": "seller-uuid",
      "company_name": "PharmaCorp Ltd."
    }
  ]
}
```

---

### GET /medicines/search

Search medicines by name or batch

**Query Parameters:**

- `q` (required): Search query
- `approved_only` (optional): true/false (default: true)

**Response (200):**

```json
{
  "message": "Search results",
  "data": [
    {
      "id": "medicine-uuid",
      "name": "Ibuprofen 200mg",
      "batch_no": "MC24002",
      "approval_status": "approved"
    }
  ]
}
```

---

## Seller Endpoints (Protected: seller_required)

### POST /seller/apply

Apply for seller KYC

**Request:**

```json
{
  "company_name": "PharmaCorp Ltd.",
  "license_number": "LIC12345"
}
```

**Response (201):**

```json
{
  "message": "Seller application submitted",
  "data": {
    "id": "seller-uuid",
    "company_name": "PharmaCorp Ltd.",
    "status": "pending",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

---

### GET /seller/status

Get seller KYC status

**Response (200):**

```json
{
  "message": "Seller status retrieved",
  "data": {
    "id": "seller-uuid",
    "company_name": "PharmaCorp Ltd.",
    "status": "approved",
    "public_key": "-----BEGIN PUBLIC KEY-----\n...",
    "approved_at": "2024-01-02T00:00:00Z"
  }
}
```

---

### POST /seller/generate-keys

Generate ECDSA key pair (One-time operation)

**Response (200):**

```json
{
  "message": "Keys generated successfully",
  "data": {
    "public_key": "-----BEGIN PUBLIC KEY-----\n...",
    "private_key_saved": true
  }
}
```

---

### POST /seller/medicine

Add new medicine

**Request:**

```json
{
  "name": "Paracetamol 500mg",
  "batch_no": "BATCH001",
  "mfg_date": "2024-01-15",
  "expiry_date": "2026-01-15",
  "dosage": "500mg",
  "strength": "500mg",
  "category": "Painkiller",
  "description": "Pain relief medicine"
}
```

**Response (201):**

```json
{
  "message": "Medicine created successfully",
  "data": {
    "id": "medicine-uuid",
    "name": "Paracetamol 500mg",
    "batch_no": "BATCH001",
    "approval_status": "pending",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

---

### GET /seller/medicine

Get seller's medicines

**Query Parameters:**

- `status` (optional): "all", "pending", "approved", "rejected"

**Response (200):**

```json
{
  "message": "Medicines retrieved",
  "data": [
    {
      "id": "medicine-uuid",
      "name": "Paracetamol 500mg",
      "approval_status": "pending",
      "seller_id": "seller-uuid"
    }
  ]
}
```

---

### POST /seller/issue-qr

Generate QR code for a medicine

**Request:**

```json
{
  "medicine_id": "medicine-uuid"
}
```

**Response (201):**

```json
{
  "message": "QR code generated",
  "data": {
    "qr_id": "qr-uuid",
    "medicine_id": "medicine-uuid",
    "signature": "base64-encoded-signature",
    "qr_image_url": "data:image/png;base64,..."
  }
}
```

---

## Scanning Endpoint (Protected: login_required)

### POST /scan

Scan and verify a QR code

**Request:**

```json
{
  "qr_data": {
    "medicine_id": "medicine-uuid",
    "batch_no": "BATCH001",
    "seller_id": "seller-uuid",
    "signature": "base64-encoded-signature"
  }
}
```

**Response (200) - Verified Medicine:**

```json
{
  "message": "QR scanned",
  "data": {
    "verified": true,
    "result": "verified",
    "medicine": {
      "id": "medicine-uuid",
      "name": "Paracetamol 500mg",
      "batch_no": "BATCH001",
      "expiry_date": "2026-01-15",
      "approval_status": "approved"
    },
    "seller": {
      "id": "seller-uuid",
      "company_name": "PharmaCorp Ltd.",
      "status": "approved"
    },
    "ai_summary": "Paracetamol is a common pain reliever..."
  }
}
```

**Response (200) - Unverified Medicine:**

```json
{
  "error": "Medicine not verified by this platform. Use at your own risk.",
  "warning": true,
  "data": {
    "verified": false,
    "result": "unverified",
    "medicine": {
      "id": "medicine-uuid",
      "name": "Unknown Medicine",
      "approval_status": "pending"
    },
    "message": "This medicine has not been verified by our platform."
  }
}
```

**Response (200) - Counterfeit Detected:**

```json
{
  "message": "QR scanned",
  "data": {
    "verified": false,
    "result": "counterfeit",
    "medicine": null,
    "seller": null,
    "ai_summary": null
  }
}
```

---

## Admin Endpoints (Protected: admin_required)

### GET /admin/sellers

Get all sellers

**Query Parameters:**

- `status` (optional): "all", "pending", "approved", "rejected"

**Response (200):**

```json
{
  "message": "Sellers retrieved",
  "data": [
    {
      "id": "seller-uuid",
      "company_name": "PharmaCorp Ltd.",
      "status": "pending",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

---

### POST /admin/sellers/{seller_id}/approve

Approve seller application

**Response (200):**

```json
{
  "message": "Seller approved successfully",
  "data": {
    "id": "seller-uuid",
    "company_name": "PharmaCorp Ltd.",
    "status": "approved",
    "approved_at": "2024-01-02T00:00:00Z"
  }
}
```

---

### POST /admin/sellers/{seller_id}/reject

Reject seller application

**Request:**

```json
{
  "reason": "License number invalid"
}
```

**Response (200):**

```json
{
  "message": "Seller rejected successfully"
}
```

---

### GET /admin/medicines

Get all medicines for approval

**Query Parameters:**

- `status` (optional): "all", "pending", "approved", "rejected"

**Response (200):**

```json
{
  "message": "Medicines retrieved",
  "data": [
    {
      "id": "medicine-uuid",
      "name": "Paracetamol 500mg",
      "approval_status": "pending",
      "seller_id": "seller-uuid",
      "company_name": "PharmaCorp Ltd.",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

---

### POST /admin/medicines/{medicine_id}/approve

Approve medicine

**Response (200):**

```json
{
  "message": "Medicine approved successfully",
  "data": {
    "id": "medicine-uuid",
    "name": "Paracetamol 500mg",
    "approval_status": "approved",
    "approved_at": "2024-01-02T00:00:00Z"
  }
}
```

---

### POST /admin/medicines/{medicine_id}/reject

Reject medicine

**Request:**

```json
{
  "reason": "Batch number invalid"
}
```

**Response (200):**

```json
{
  "message": "Medicine rejected successfully"
}
```

---

### GET /admin/analytics

Get system analytics and statistics

**Response (200):**

```json
{
  "message": "Analytics retrieved",
  "data": {
    "total_sellers": 15,
    "total_medicines": 42,
    "total_qr_codes": 156,
    "revoked_qr_codes": 2,
    "scan_counts": {
      "verified": 234,
      "expired": 5,
      "counterfeit": 3,
      "error": 1
    }
  }
}
```

---

## Error Responses

### 400 Bad Request

```json
{
  "error": "Invalid input",
  "message": "Email is required"
}
```

### 401 Unauthorized

```json
{
  "error": "Authorization required",
  "message": "Please provide a valid token"
}
```

### 403 Forbidden

```json
{
  "error": "Insufficient permissions",
  "message": "Required role: admin"
}
```

### 404 Not Found

```json
{
  "error": "Resource not found",
  "message": "Medicine with id ... not found"
}
```

### 409 Conflict

```json
{
  "error": "Resource already exists",
  "message": "User already registered"
}
```

### 500 Internal Server Error

```json
{
  "error": "Internal server error",
  "message": "An unexpected error occurred"
}
```

---

## Rate Limiting

Currently no rate limiting. In production, implement:

- 100 requests per minute per IP
- 10 requests per minute per user for sensitive endpoints
- Exponential backoff for failed auth attempts

---

## Pagination

For endpoints that return multiple results:

**Query Parameters:**

- `limit`: Number of results (default: 50, max: 1000)
- `offset`: Start position (default: 0)

**Example:**

```
GET /medicines?limit=20&offset=40
```

---

## Security Headers

All responses include:

```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
```

---

## Status Codes

| Code | Meaning        |
| ---- | -------------- |
| 200  | OK             |
| 201  | Created        |
| 400  | Bad Request    |
| 401  | Unauthorized   |
| 403  | Forbidden      |
| 404  | Not Found      |
| 409  | Conflict       |
| 500  | Internal Error |
