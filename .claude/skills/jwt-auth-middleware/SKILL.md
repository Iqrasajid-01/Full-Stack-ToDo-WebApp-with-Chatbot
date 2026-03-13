---
name: jwt-auth-middleware
description: Implement secure JWT-based authentication middleware for protecting backend API routes.
---

# JWT Authentication Middleware

## Instructions

1. **Token validation**
   - Extract JWT token from request headers
   - Verify token signature and integrity
   - Reject invalid or expired tokens

2. **User identification**
   - Decode user identity from validated token
   - Attach authenticated user context to requests
   - Prevent user impersonation

3. **Route protection**
   - Enforce authentication on protected API routes
   - Return proper authorization errors
   - Ensure consistent behavior across endpoints

## Best Practices
- Require JWT on all non-public routes
- Use a shared secret via environment variables
- Avoid leaking authentication details in errors
- Keep middleware logic centralized
- Fail fast on unauthorized access

Use this skill when securing backend APIs with JWT authentication.
