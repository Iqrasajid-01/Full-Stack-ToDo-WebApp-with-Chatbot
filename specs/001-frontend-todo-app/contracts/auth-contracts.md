# API Contracts: Authentication

## POST /api/auth/signup

**Description**: Register a new user account

**Request**:
```json
{
  "email": "user@example.com",
  "password": "securePassword123",
  "name": "John Doe"
}
```

**Response (Success)**:
```json
{
  "status": "success",
  "data": {
    "user": {
      "id": "uuid-string",
      "email": "user@example.com",
      "name": "John Doe"
    },
    "token": "jwt-token-string"
  }
}
```

**Response (Validation Error)**:
```json
{
  "status": "error",
  "errors": [
    {
      "field": "email",
      "message": "Email is already taken"
    }
  ]
}
```

**Response (Failure)**:
```json
{
  "status": "error",
  "message": "Registration failed"
}
```

## POST /api/auth/signin

**Description**: Authenticate user and return JWT token

**Request**:
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Response (Success)**:
```json
{
  "status": "success",
  "data": {
    "user": {
      "id": "uuid-string",
      "email": "user@example.com",
      "name": "John Doe"
    },
    "token": "jwt-token-string"
  }
}
```

**Response (Failure)**:
```json
{
  "status": "error",
  "message": "Invalid credentials"
}
```

## POST /api/auth/signout

**Description**: Invalidate current user session

**Headers**:
```
Authorization: Bearer {jwt-token}
```

**Response (Success)**:
```json
{
  "status": "success",
  "message": "Successfully signed out"
}
```

## GET /api/auth/me

**Description**: Retrieve current authenticated user details

**Headers**:
```
Authorization: Bearer {jwt-token}
```

**Response (Success)**:
```json
{
  "status": "success",
  "data": {
    "id": "uuid-string",
    "email": "user@example.com",
    "name": "John Doe",
    "createdAt": "2026-02-06T10:00:00Z"
  }
}
```

**Response (Unauthorized)**:
```json
{
  "status": "error",
  "message": "Unauthorized"
}
```