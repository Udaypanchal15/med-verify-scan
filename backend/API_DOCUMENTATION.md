# API Documentation

## Authentication Endpoints

### POST /auth/register
Register a new user.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "role": "user",
  "timezone": "UTC"
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
      "timezone": "UTC",
      "created_at": "2024-01-01T00:00:00Z"
    },
    "access_token": "jwt_token",
    "refresh_token": "refresh_token"
  }
}
```

**Errors:**
- 400: Invalid input
- 409: User already exists
- 403: Cannot self-assign admin role

---

### POST /auth/login
Login user and get JWT tokens.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
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
      "role": "user",
      "timezone": "UTC",
      "last_login": "2024-01-01T00:00:00Z"
    },
    "access_token": "jwt_token",
    "refresh_token": "refresh_token"
  }
}
```

**Errors:**
- 400: Missing email or password
- 401: Invalid credentials

---

### POST /auth/refresh
Refresh access token using refresh token.

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

**Errors:**
- 401: Invalid or expired refresh token

---

### GET /auth/me
Get current user information.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "message": "User information retrieved successfully",
  "data": {
    "id": "uuid",
    "email": "user@example.com",
    "role": "user",
    "timezone": "UTC",
    "created_at": "2024-01-01T00:00:00Z",
    "last_login": "2024-01-01T00:00:00Z"
  }
}
```

**Errors:**
- 401: Not authenticated

---

### POST /auth/logout
Logout user (client-side token removal).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "message": "Logged out successfully. Please remove tokens on client side."
}
```

---

## Authentication Headers

All protected endpoints require the following header:
```
Authorization: Bearer <access_token>
```

## Password Requirements

- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit

## Role-Based Access

- **user**: Regular users (can scan, create reminders)
- **seller**: Pharmaceutical companies (can register, issue QR codes)
- **admin**: Administrators (can approve sellers, revoke keys, view analytics)

## Token Expiration

- **Access Token**: 1 hour (3600 seconds)
- **Refresh Token**: 24 hours (86400 seconds)

## Error Responses

All errors follow this format:
```json
{
  "error": "Error type",
  "message": "Detailed error message"
}
```

Common HTTP status codes:
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 409: Conflict
- 500: Internal Server Error



