from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Any, Dict, Optional
import os

app = FastAPI(
    title="Mortgage Matcher",
    version="1.0.0",
)

# Mount the existing UI folder
app.mount("/ui", StaticFiles(directory="ui"), name="ui")


# Serve the UI as the root page
@app.get("/", include_in_schema=False)
def root() -> FileResponse:
    index_path = os.path.join("ui", "index.html")
    if not os.path.exists(index_path):
        # Helpful error if UI folder is missing in the container
        raise HTTPException(status_code=500, detail="UI index.html not found")
    return FileResponse(index_path)


# Health check endpoint
@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


# ---- Request/response models for /compare ----

class CompareRequest(BaseModel):
    doc_type: str
    structured: Dict[str, Any]
    unstructured: Dict[str, Any]


class CompareResponse(BaseModel):
    status: str
    message: str
    score: float
    details: Optional[Dict[str, Any]] = None


# Placeholder compare endpoint
@app.post("/compare", response_model=CompareResponse)
def compare_docs(payload: CompareRequest) -> CompareResponse:
    """
    Placeholder implementation.

    The UI sends:
      {
        "doc_type": "paystub" | "w2",
        "structured": { ... },
        "unstructured": { ... }
      }

    This endpoint currently returns a stub response so you can
    validate end-to-end wiring from UI → API → UI.
    Replace the internals later with your real matcher logic.
    """

    # Basic sanity check on doc_type
    if payload.doc_type not in {"paystub", "w2"}:
        raise HTTPException(status_code=400, detail="Unsupported doc_type")

    # Stubbed comparison result
    result = CompareResponse(
        status="success",
        message=f"Placeholder comparison for {payload.doc_type}",
        score=0.0,
        details={
            "note": "Replace this with real field-level comparison logic.",
            "structured_keys": list(payload.structured.keys()),
            "unstructured_keys": list(payload.unstructured.keys()),
        },
    )

    return result


# Optional: simple 404 handler for clarity
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )
