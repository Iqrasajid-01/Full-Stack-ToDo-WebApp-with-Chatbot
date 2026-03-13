import uvicorn
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from main import app
    print("Successfully imported app")
    
    # Try to initialize the database
    from db.init import create_db_and_tables
    print("Attempting to create database tables...")
    create_db_and_tables()
    print("Database tables created successfully")
    
    # Run the server
    print("Starting server on http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
    
except Exception as e:
    print(f"Error starting server: {e}")
    import traceback
    traceback.print_exc()