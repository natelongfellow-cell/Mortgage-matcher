from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import json
import os

app = FastAPI()

# Allow UI to call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve the UI folder
app.mount("/ui", StaticFiles(directory="ui"), name="ui")

@app.get("/")
def root():
    return FileResponse("ui/index.html")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/compare")
async def compare(file1: UploadFile = File(...), file2: UploadFile = File(...)):
    # Read uploaded file contents
    content1 = await file1.read()
    content2 = await file2.read()

    # Parse JSON inside each file
    try:
        data1 = json.loads(content1)
    except Exception as e:
        return {"error": f"File1 is not valid JSON: {str(e)}"}

    try:
        data2 = json.loads(content2)
    except Exception as e:
        return {"error": f"File2 is not valid JSON: {str(e)}"}

    # Placeholder comparison logic
    # Replace with your real matching logic later
    return {
        "message": "Files received and parsed successfully",
        "structured_keys": list(data1.keys()),
        "unstructured_keys": list(data2.keys())
    }

