from fastapi import FastAPI, Request, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import base64
from io import BytesIO
from PIL import Image
import numpy as np
import cv2
import tempfile
from posture_logic import analyze_image, analyze_video, summarize_video

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze-frame")
async def analyze_frame(request: Request):
    body = await request.json()
    image_data = body.get("image_data")

    if not image_data:
        return JSONResponse(content={"error": "No image data provided"}, status_code=400)

    try:
        header, encoded = image_data.split(",", 1)
        img_bytes = base64.b64decode(encoded)
        img = Image.open(BytesIO(img_bytes)).convert("RGB")
        img_np = np.array(img)
        image_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
        feedback = analyze_image(image_bgr)
        return {"feedback": feedback}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/analyze")
async def analyze(file: UploadFile = File(...), mode: str = Query("frame")):
    with tempfile.NamedTemporaryFile(delete=False) as temp:
        temp.write(await file.read())
        temp_path = temp.name

    if mode == "summary":
        feedback = summarize_video(temp_path)
    else:
        feedback = analyze_video(temp_path)
    
    return JSONResponse(content={"feedback": feedback})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
