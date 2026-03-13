#!/usr/bin/env python3
"""
Simple script to run the backend server
"""
from main import app
import uvicorn
from db.init import create_db_and_tables

if __name__ == "__main__":
    print("Setting up database...")
    create_db_and_tables()
    print("Database setup complete.")

    print("Starting server on http://localhost:8000...")
    uvicorn.run(app, host="localhost", port=8000, log_level="info")