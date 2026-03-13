---
name: betterauth-jwt-setup
description: Configure and integrate BetterAuth for JWT-based authentication flows in modern web applications.
---

# BetterAuth JWT Setup

## Instructions

1. **Configuration**
   - Install and initialize BetterAuth
   - Define JWT secret and token expiry
   - Configure auth providers and strategies

2. **Token management**
   - Issue JWT tokens on successful authentication
   - Refresh tokens securely when required
   - Invalidate tokens on logout

3. **Integration**
   - Connect BetterAuth with backend auth logic
   - Ensure compatibility with existing JWT middleware
   - Standardize auth responses across services

## Best Practices
- Store secrets in environment variables
- Use short-lived access tokens
- Rotate secrets periodically
- Log auth events without exposing sensitive data
- Keep auth configuration centralized

Use this skill when setting up BetterAuth with JWT for secure authentication systems.
