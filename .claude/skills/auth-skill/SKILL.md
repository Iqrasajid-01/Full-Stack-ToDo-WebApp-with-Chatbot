---
name: auth-skill
description: Implement secure user authentication including signup, signin, password hashing, JWT tokens, and Better Auth integration.
---

# Authentication Skill

## Instructions

1. **User authentication flows**
   - Implement user signup and signin
   - Validate user credentials securely
   - Handle authentication errors gracefully

2. **Password security**
   - Hash passwords before storage
   - Never store or log plain-text passwords
   - Follow industry-standard hashing practices

3. **JWT token handling**
   - Issue JWT tokens on successful authentication
   - Include user identity claims in tokens
   - Enforce token expiry and validation

4. **Better Auth integration**
   - Integrate Better Auth on the frontend
   - Enable JWT-based authentication
   - Ensure tokens are attached to API requests

## Best Practices
- Enforce authentication on all protected routes
- Ensure user isolation across all operations
- Use environment variables for secrets
- Fail securely on authentication errors
- Keep authentication logic centralized

Use this skill whenever implementing or validating authentication functionality.
