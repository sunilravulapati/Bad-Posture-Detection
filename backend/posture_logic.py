from ultralytics import YOLO
import numpy as np
import cv2
import os # Import os for path handling

# Ensure the model path is correct. If yolov8n-pose.pt is not in the same directory
# as posture_logic.py, provide the full path or adjust accordingly.
# For example: model_path = "/path/to/your/yolov8n-pose.pt"
model_path = "yolov8n-pose.pt"

try:
    model = YOLO(model_path)
    print(f"YOLO model loaded successfully from {model_path}")
except Exception as e:
    print(f"ERROR: Could not load YOLO model from {model_path}. Please ensure the file exists and is accessible. Error: {e}")
    # You might want to exit or raise an error here if the model is critical
    # For now, we'll let it proceed, but subsequent calls will fail.
    model = None # Set model to None to handle cases where loading failed

def compute_angle(a, b, c):
    a, b, c = map(np.array, [a, b, c])
    ba, bc = a - b, c - b
    # Add a small epsilon to the denominator to prevent division by zero if norm is zero
    denominator = np.linalg.norm(ba) * np.linalg.norm(bc)
    if denominator < 1e-6: # Check if denominator is effectively zero
        print("WARNING: Zero norm detected in angle computation. Returning 0 degrees.")
        return 0.0
    cosine_angle = np.dot(ba, bc) / (denominator + 1e-6)
    return np.degrees(np.arccos(np.clip(cosine_angle, -1.0, 1.0)))

def analyze_video(video_path, mode="frame"):
    if model is None:
        print("ERROR: Model not loaded, cannot analyze video.")
        return {"posture": "error", "reason": "AI model not loaded"}

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"ERROR: Could not open video file: {video_path}")
        return {"posture": "error", "reason": "Could not open video file"}

    feedback = []
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print(f"End of video or failed to read frame at frame_count: {frame_count}")
            break
        frame_count += 1
        
        print(f"Processing frame {frame_count}...")
        results = model.predict(frame, save=False, verbose=False)

        if results and results[0].keypoints is not None and results[0].keypoints.xy.shape[0] > 0:
            kps = results[0].keypoints.xy[0].cpu().numpy()
            print(f"Keypoints detected for frame {frame_count}: {kps}")

            # Ensure keypoints exist before accessing
            if len(kps) < 17: # YOLOv8 pose model detects 17 keypoints
                print(f"WARNING: Not enough keypoints detected in frame {frame_count}. Expected 17, got {len(kps)}.")
                feedback.append({
                    "frame": frame_count,
                    "posture": "undetected",
                    "reason": "Not enough keypoints detected"
                })
                continue

            left_shoulder = kps[5]
            left_hip = kps[11]
            left_knee = kps[13]
            left_ankle = kps[15]

            back_angle = compute_angle(left_shoulder, left_hip, left_knee)
            # For knee over toe, check if knee is significantly forward of ankle in X-coordinate
            # A small threshold can account for minor variations
            knee_over_toe = left_knee[0] > left_ankle[0] + 5 # Added a small threshold (e.g., 5 pixels)

            print(f"Frame {frame_count}: Back angle={back_angle:.2f}°, Knee over toe={knee_over_toe}")

            status = "good"
            reason = []

            # Adjust squat angle thresholds based on typical squat form
            # A good squat often involves a back angle closer to 90-120 degrees relative to vertical,
            # or a hip-knee-ankle angle (knee bend) around 90 degrees.
            # Your current 'back_angle' is shoulder-hip-knee. Let's assume it should be around 150-180 for good posture.
            # If it's a deep squat, this angle will decrease.
            # Let's consider a common squat form where the torso leans forward.
            # The angle between shoulder, hip, and knee will be smaller than 180 (straight line).
            # For a proper squat, this angle might be around 90-120 degrees.
            # If back_angle < 150, it means the back is leaning forward significantly.
            # Let's refine this based on what "good" and "bad" squat looks like.
            # For a deep squat, shoulder-hip-knee angle might be around 90-120 degrees.
            # If the user is standing, it's closer to 180.
            # If the intent is to detect a 'bad' forward lean during a squat, 150 might be okay.
            # However, if it's about the depth of the squat, you'd need hip-knee-ankle angle.

            # Let's assume 'back_angle < 150' means the back is too rounded or leaning too far forward *when standing or in a shallow squat*.
            # If the goal is to check for a straight back during a squat, this check might need adjustment.
            # For simplicity, let's keep your original logic but be aware of its interpretation.
            if back_angle < 150: # This means the angle is sharper, indicating a forward lean or rounded back
                status = "bad"
                reason.append(f"Back angle {int(back_angle)}° is too sharp (< 150°), indicating forward lean or rounded back.")

            if knee_over_toe:
                status = "bad"
                reason.append("Knee over toe detected, which can put strain on knees.")

            feedback.append({
                "frame": frame_count,
                "posture": status,
                "reason": "; ".join(reason) if reason else "Good posture"
            })
        else:
            print(f"No person or keypoints detected in frame {frame_count}.")
            feedback.append({
                "frame": frame_count,
                "posture": "undetected",
                "reason": "No person detected"
            })

    cap.release()
    print("Video analysis complete.")

    if mode == "summary":
        return summarize_feedback(feedback)
    return feedback

def summarize_feedback(feedback):
    if not feedback:
        return {
            "accuracy": 100.0,
            "bad_posture_frames": 0,
            "top_issue": "No frames analyzed"
        }

    bad_frames = [f for f in feedback if f["posture"] == "bad"]
    undetected_frames = [f for f in feedback if f["posture"] == "undetected"]

    top_reason = {}
    for f in bad_frames:
        r = f["reason"]
        top_reason[r] = top_reason.get(r, 0) + 1

    top_issue = max(top_reason.items(), key=lambda x: x[1])[0] if top_reason else "None"

    return {
        "accuracy": round((1 - len(bad_frames) / len(feedback)) * 100, 2) if feedback else 100.0,
        "bad_posture_frames": len(bad_frames),
        "undetected_frames": len(undetected_frames), # Added for more insight
        "top_issue": top_issue
    }

def analyze_frame(frame):
    if model is None:
        print("ERROR: Model not loaded, cannot analyze frame.")
        return {"posture": "error", "reason": "AI model not loaded"}

    print("Analyzing single frame...")
    results = model.predict(frame, save=False, verbose=False)

    if results and results[0].keypoints is not None and results[0].keypoints.xy.shape[0] > 0:
        kps = results[0].keypoints.xy[0].cpu().numpy()
        print(f"Keypoints detected for single frame: {kps}")

        if len(kps) < 17:
            print(f"WARNING: Not enough keypoints detected in single frame. Expected 17, got {len(kps)}.")
            return {
                "posture": "undetected",
                "reason": "Not enough keypoints detected"
            }

        left_shoulder = kps[5]
        left_hip = kps[11]
        left_knee = kps[13]
        left_ankle = kps[15]

        back_angle = compute_angle(left_shoulder, left_hip, left_knee)
        knee_over_toe = left_knee[0] > left_ankle[0] + 5 # Added a small threshold

        print(f"Single frame: Back angle={back_angle:.2f}°, Knee over toe={knee_over_toe}")

        status = "good"
        reason = []

        if back_angle < 150:
            status = "bad"
            reason.append(f"Back angle {int(back_angle)}° is too sharp (< 150°).")

        if knee_over_toe:
            status = "bad"
            reason.append("Knee over toe detected.")

        return {
            "posture": status,
            "reason": "; ".join(reason) if reason else "Good posture"
        }

    print("No person or keypoints detected in single frame.")
    return {
        "posture": "undetected",
        "reason": "No person detected"
    }

