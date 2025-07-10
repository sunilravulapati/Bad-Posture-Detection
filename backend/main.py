from fastapi import FastAPI, File, UploadFile, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from posture_logic import analyze_video, analyze_frame
import tempfile
import numpy as np
import cv2
import os

app = FastAPI()

# Allow CORS from any origin (for frontend deployment)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze")
async def analyze(file: UploadFile = File(...), mode: str = Query("frame")):
    print(f"[INFO] Received /analyze request. File: {file.filename}, Mode: {mode}")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp:
        temp.write(await file.read())
        temp_path = temp.name

    try:
        feedback = analyze_video(temp_path, mode)
        print(f"[INFO] Analysis complete. Frames analyzed: {len(feedback)}")
        return JSONResponse(content={"feedback": feedback})
    except Exception as e:
        print(f"[ERROR] Video analysis failed: {e}")
        return JSONResponse(content={"detail": str(e)}, status_code=500)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
            print(f"[INFO] Temporary file removed: {temp_path}")

@app.post("/analyze-frame")
async def analyze_frame_route(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            raise ValueError("Could not decode image. Make sure it's a valid JPEG/PNG.")

        feedback = analyze_frame(img)
        return JSONResponse(content={"feedback": feedback})
    
    except Exception as e:
        print(f"[ERROR] Frame analysis failed: {e}")
        return JSONResponse(content={"detail": str(e)}, status_code=400)
