from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import json
from typing import Any, Dict
from matcher import SchemaMatcher

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve UI
app.mount("/ui", StaticFiles(directory="ui"), name="ui")


@app.get("/")
def root():
    return FileResponse("ui/index.html")


@app.get("/health")
def health():
    return {"status": "ok"}


# Lazy-loaded matcher
matcher: SchemaMatcher | None = None


@app.post("/compare")
async def compare(file1: UploadFile = File(...), file2: UploadFile = File(...)) -> Dict[str, Any]:
    global matcher

    # Lazy load the model here instead of at startup
    if matcher is None:
        matcher = SchemaMatcher()

    # Read uploaded file contents
    content1 = await file1.read()
    content2 = await file2.read()

    # Parse JSON
    try:
        data1 = json.loads(content1)
    except Exception as e:
        return {"error": f"File1 is not valid JSON: {str(e)}"}

    try:
        data2 = json.loads(content2)
    except Exception as e:
        return {"error": f"File2 is not valid JSON: {str(e)}"}

    if not isinstance(data1, dict) or not isinstance(data2, dict):
        return {"error": "Both files must contain top-level JSON objects."}

    structured_keys = list(data1.keys())
    unstructured_keys = list(data2.keys())

    matches = matcher.match(structured_keys, unstructured_keys, top_k=3)

    return {
        "message": "Schema matching completed",
        "structured_keys": structured_keys,
        "unstructured_keys": unstructured_keys,
        "matches": matches,
    }
