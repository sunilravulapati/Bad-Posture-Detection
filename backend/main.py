from fastapi import FastAPI, File, UploadFile, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from posture_logic import analyze_video, analyze_frame
import tempfile
import numpy as np
import cv2
import os # Import os for path handling

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze")
async def analyze(file: UploadFile = File(...), mode: str = Query("frame")):
    print(f"Received video analysis request for file: {file.filename}, mode: {mode}")
    with tempfile.NamedTemporaryFile(delete=False) as temp:
        temp.write(await file.read())
        temp_path = temp.name
    print(f"Video saved temporarily to: {temp_path}")

    try:
        feedback = analyze_video(temp_path, mode)
        print(f"Video analysis feedback: {feedback}")
        return JSONResponse(content={"feedback": feedback})
    except Exception as e:
        print(f"Error during video analysis: {e}")
        return JSONResponse(content={"detail": str(e)}, status_code=500)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path) # Clean up the temporary file
            print(f"Temporary video file {temp_path} removed.")


@app.post("/analyze-frame")
async def analyze_frame_route(frame: UploadFile = File(...)):
    print(f"Received frame analysis request for file: {frame.filename}, content type: {frame.content_type}")
    contents = await frame.read()
    print(f"Received {len(contents)} bytes for the frame.")

    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        print("ERROR: cv2.imdecode failed to decode the image.")
        return JSONResponse(content={"result": {"posture": "error", "reason": "Could not decode image"}}, status_code=400)

    print(f"Image decoded successfully. Shape: {img.shape}, Type: {img.dtype}")

    try:
        result = analyze_frame(img)
        print(f"Frame analysis result: {result}")
        return JSONResponse(content={"result": result})
    except Exception as e:
        print(f"Error during frame analysis: {e}")
        return JSONResponse(content={"detail": str(e)}, status_code=500)

