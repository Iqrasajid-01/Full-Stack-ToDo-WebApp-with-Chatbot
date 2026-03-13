from fastapi import FastAPI
import uvicorn

app = FastAPI(title="Test Server")

@app.get("/")
def read_root():
    return {"message": "Server is running!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8002, log_level="info")