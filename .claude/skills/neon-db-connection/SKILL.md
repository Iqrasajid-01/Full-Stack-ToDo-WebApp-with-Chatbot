---
name: neon-db-connection
description: Configure and manage a secure connection to Neon Serverless PostgreSQL for persistent data storage.
---

# Neon Database Connection

## Instructions

1. **Database configuration**
   - Set up Neon Serverless PostgreSQL connection
   - Use environment variables for database credentials
   - Ensure compatibility with serverless execution

2. **Connection management**
   - Initialize database connections safely
   - Support connection reuse where applicable
   - Handle connection failures gracefully

3. **ORM integration**
   - Integrate database connection with SQLModel
   - Ensure models are correctly bound to the database
   - Prepare database layer for multi-user data access

## Best Practices
- Never hardcode database credentials
- Use connection pooling appropriate for serverless
- Validate connection on application startup
- Log database errors without exposing sensitive data
- Design for scalability and reliability

Use this skill whenever setting up or validating database connectivity.
