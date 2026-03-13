from better_automation.auth import Auth, User
from better_automation.sqlmodel import SQLModelAdapter
from sqlmodel import create_engine
from core.config import settings

# Create database engine
engine = create_engine(str(settings.NEON_DATABASE_URL).replace("postgresql://", "postgresql+psycopg2://"))

# Create adapter
adapter = SQLModelAdapter(engine, User)

# Initialize Better Auth
auth = Auth(
    secret=settings.BETTER_AUTH_SECRET,
    database_url=str(settings.NEON_DATABASE_URL),
    # Add other configuration options as needed
)

# Export the auth instance
better_auth = auth