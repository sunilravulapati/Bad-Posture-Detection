import cv2
import mediapipe as mp
import numpy as np

mp_pose = mp.solutions.pose

def compute_angle(a, b, c):
    """Compute the angle at point b given three points a, b, c."""
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    if angle > 180.0:
        angle = 360 - angle
    return angle

def analyze_video(path):
    """Analyze posture in a video file."""
    cap = cv2.VideoCapture(path)
    feedback = []

    if not cap.isOpened():
        return [{"error": "Cannot open video file."}]

    with mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(image)

            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark

                shoulder = [
                    landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                    landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y
                ]
                hip = [
                    landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                    landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y
                ]
                knee = [
                    landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                    landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y
                ]

                back_angle = compute_angle(shoulder, hip, knee)

                frame_number = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
                if back_angle < 150:
                    feedback.append({
                        "frame": frame_number,
                        "posture": "bad",
                        "reason": "Back angle < 150°"
                    })
                else:
                    feedback.append({
                        "frame": frame_number,
                        "posture": "good"
                    })

    cap.release()
    return feedback

def analyze_image(image_bgr):
    """Analyze posture in a single image (BGR format)."""
    with mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5) as pose:
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        results = pose.process(image_rgb)

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            shoulder = [
                landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y
            ]
            hip = [
                landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y
            ]
            knee = [
                landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y
            ]

            back_angle = compute_angle(shoulder, hip, knee)

            if back_angle < 150:
                return {"posture": "bad", "reason": "Back angle < 150°"}
            else:
                return {"posture": "good"}

    return {"posture": "no_person_detected", "reason": "No landmarks found"}

def summarize_video(path):
    frame_feedback = analyze_video(path)
    total = len(frame_feedback)
    bad_frames = [f for f in frame_feedback if f["posture"] == "bad"]

    summary = {
        "total_frames": total,
        "bad_posture_frames": len(bad_frames),
        "accuracy": round((total - len(bad_frames)) / total * 100, 2),
        "top_issue": None,
    }

    reason_count = {}
    for f in bad_frames:
        if "reason" in f:
            reason_count[f["reason"]] = reason_count.get(f["reason"], 0) + 1

    if reason_count:
        summary["top_issue"] = max(reason_count, key=reason_count.get)

    return summary
