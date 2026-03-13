---
name: centralized-api-client
description: Create a centralized API client for consistent, secure, and reusable backend communication across the application.
---

# Centralized API Client

## Instructions

1. **Client setup**
   - Create a single API client instance
   - Configure base URL and default headers
   - Handle environment-based endpoints

2. **Request handling**
   - Attach auth tokens automatically
   - Standardize request and response formats
   - Support GET, POST, PUT, DELETE methods

3. **Error handling**
   - Catch and normalize API errors
   - Handle unauthorized and expired sessions
   - Provide meaningful error messages to the app

4. **Reusability**
   - Expose reusable service functions
   - Keep API logic separate from UI components
   - Ensure type safety where possible

## Best Practices
- Centralize token injection logic
- Avoid duplicate API calls
- Implement request timeouts
- Log errors for debugging
- Keep API client framework-agnostic

Use this skill to simplify and standardize API communication across frontend and backend services.
