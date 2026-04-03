# api.py

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import json
from matcher import compare_json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/compare")
async def compare(structured: UploadFile = File(...), unstructured: UploadFile = File(...)):
    try:
        structured_data = json.loads((await structured.read()).decode("utf-8"))
        unstructured_data = json.loads((await unstructured.read()).decode("utf-8"))
    except Exception as e:
        return {"error": f"Invalid JSON uploaded: {str(e)}"}

    result = compare_json(structured_data, unstructured_data)
    return result

@app.get("/")
def root():
    return {"status": "Mortgage Matcher API running"}
