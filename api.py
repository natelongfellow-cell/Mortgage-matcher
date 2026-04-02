from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from matcher.compare import compare_json_files

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/compare")
async def compare(file1: UploadFile = File(...), file2: UploadFile = File(...)):
    data1 = await file1.read()
    data2 = await file2.read()
    return compare_json_files(data1, data2)

@app.get("/")
def root():
    return {"status": "ok", "message": "Mortgage Matcher API running"}
