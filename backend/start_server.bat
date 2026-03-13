@echo off
cd /d D:\Q4-Hackathon2\H2-Phase-II\backend
echo Starting backend server on port 8000...
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
pause