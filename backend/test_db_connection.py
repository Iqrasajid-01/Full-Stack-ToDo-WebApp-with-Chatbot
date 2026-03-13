import asyncio
from sqlalchemy import create_engine, text
from core.config import settings
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

def test_db_connection():
    try:
        # Create the database engine
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

        print(f"Connecting to: {connection_string[:50]}...")  # Print first 50 chars
        
        # Create engine
        engine = create_engine(connection_string)
        
        # Test the connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("Database connection successful!")
            print("Result:", result.fetchone())
            
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_db_connection()