from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from matcher import compare_documents

app = FastAPI()

# -----------------------------
# CORS
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Serve UI
# -----------------------------
app.mount("/ui", StaticFiles(directory="ui"), name="ui")

@app.get("/")
def root():
    return FileResponse(os.path.join("ui", "index.html"))

# -----------------------------
# Health Check
# -----------------------------
@app.get("/health")
def health():
    return {"status": "ok"}

# -----------------------------
# Compare Endpoint
# -----------------------------
@app.post("/compare")
async def compare(doc1: UploadFile = File(...), doc2: UploadFile = File(...)):
    try:
        text1 = (await doc1.read()).decode("utf-8", errors="ignore")
        text2 = (await doc2.read()).decode("utf-8", errors="ignore")

        result = compare_documents(text1, text2)
        return {"result": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
