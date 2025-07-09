import React, { useRef, useState } from "react";
import Webcam from "react-webcam";
import axios from "axios";

const videoConstraints = {
  width: 640,
  height: 480,
  facingMode: "user",
};

const WebcamCapture = () => {
  const webcamRef = useRef(null);
  const [feedback, setFeedback] = useState(null);

  const capture = async () => {
    const screenshot = webcamRef.current.getScreenshot();

    try {
      const res = await axios.post("http://localhost:8000/analyze-frame", {
        image_data: screenshot,
      });
      setFeedback(res.data.feedback);
    } catch (error) {
      console.error("Error analyzing frame", error);
      alert("Backend error!");
    }
  };

  return (
    <div className="text-center p-4">
      <Webcam
        audio={false}
        ref={webcamRef}
        screenshotFormat="image/jpeg"
        videoConstraints={videoConstraints}
        className="rounded-lg shadow-md mx-auto"
      />
      <button
        onClick={capture}
        className="mt-4 px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
      >
        Capture & Analyze
      </button>
      {feedback && (
        <div className="mt-4 text-left">
          <p>
            <strong>Posture:</strong> {feedback.posture}
          </p>
          {feedback.reason && <p><strong>Reason:</strong> {feedback.reason}</p>}
        </div>
      )}
    </div>
  );
};

export default WebcamCapture;
