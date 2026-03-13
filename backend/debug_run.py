#!/usr/bin/env python3
"""
Debug script to run the backend server and troubleshoot connection issues
"""
import subprocess
import sys
import time
import requests
import threading
from main import app
import uvicorn
from db.init import create_db_and_tables

def run_server():
    """Run the server in a separate thread"""
    print("Starting server on http://localhost:8000...")
    uvicorn.run(app, host="localhost", port=8000, log_level="info")

def test_server():
    """Test the server after a delay"""
    time.sleep(3)  # Wait for server to start
    
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✓ Server is running and responding!")
            print(f"Health check response: {response.json()}")
        else:
            print(f"✗ Server responded with status code: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to server. Is it running?")
    except Exception as e:
        print(f"✗ Error testing server: {e}")

if __name__ == "__main__":
    print("Setting up database...")
    create_db_and_tables()
    print("Database setup complete.")
    
    print("\nStarting server and test in separate threads...")
    
    # Start server in a thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Run test
    test_server()
    
    print("\nKeeping main thread alive. Press Ctrl+C to exit.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        sys.exit(0)