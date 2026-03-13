from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.config import settings
from typing import Generator
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse


# Create the database engine
# Using psycopg2 driver for PostgreSQL with proper connection parameters for Neon
original_url = str(settings.NEON_DATABASE_URL)

# Parse the URL to modify query parameters
parsed = urlparse(original_url)
query_params = parse_qs(parsed.query)

# Add or update SSL parameters for Neon
query_params['sslmode'] = ['require']

# Reconstruct the URL with updated parameters
new_query = urlencode(query_params, doseq=True)
connection_string = urlunparse((
    parsed.scheme.replace('postgresql', 'postgresql+psycopg2'),
    parsed.netloc,
    parsed.path,
    parsed.params,
    new_query,
    parsed.fragment
))

# Create engine with connection pooling and proper parameters
engine = create_engine(
    connection_string,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=300,    # Recycle connections every 5 minutes
    echo=False           # Set to True for debugging SQL queries
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_session() -> Generator:
    """
    Get a database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()