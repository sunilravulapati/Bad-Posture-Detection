from ultralytics import YOLO

# Load the model
model = YOLO("yolov8n-pose.pt")  # Lightweight pose model

# Analyze the video and save the output (no window will pop up)
model.predict(
    source="C:/Users/sunilravulapati/Downloads/sit2.mp4",
    save=True,
    save_txt=False,  # optional: saves bounding box data if True
    conf=0.5,         # confidence threshold
    stream=False,     # disable streaming (batch processing)
    show=False        # don't show frames
)
