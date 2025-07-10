import React, { useRef, useState, useEffect } from "react";
import axios from "axios";

const videoConstraints = {
  width: 640,
  height: 480,
  facingMode: "user",
};

const API_BASE_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";

const WebcamCapture = () => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [feedback, setFeedback] = useState(null);
  const [message, setMessage] = useState("Initializing webcam...");
  const [stream, setStream] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const enableStream = async () => {
      try {
        const mediaStream = await navigator.mediaDevices.getUserMedia({ video: videoConstraints });
        if (videoRef.current) {
          videoRef.current.srcObject = mediaStream;
          setStream(mediaStream);
          setMessage("Webcam ready. Click 'Capture & Analyze' to begin.");
        }
      } catch (err) {
        console.error("Error accessing webcam:", err);
        setMessage(`Error: Could not access webcam. (${err.name}: ${err.message})`);
      }
    };

    enableStream();

    return () => {
      if (stream) {
        stream.getTracks().forEach((track) => track.stop());
      }
    };
  }, []);

  const capture = async () => {
    if (!videoRef.current || !canvasRef.current) return;

    setIsLoading(true);
    setMessage("Capturing image and analyzing...");

    const video = videoRef.current;
    const canvas = canvasRef.current;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob(async (blob) => {
      if (!blob) {
        alert("Failed to capture image");
        setIsLoading(false);
        return;
      }

      const formData = new FormData();
      formData.append("file", blob, "frame.jpg");

      try {
        const response = await axios.post(`${API_BASE_URL}/analyze-frame`, formData, {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        });

        setFeedback(response.data.feedback || response.data.result);
        setMessage("Analysis complete.");
      } catch (error) {
        console.error("Error analyzing frame:", error);
        alert("Backend error!");
        setMessage("Error occurred while analyzing.");
      } finally {
        setIsLoading(false);
      }
    }, "image/jpeg");
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-4 font-sans rounded-lg">
      <h1 className="text-3xl font-bold mb-6 text-gray-800">Posture Analyzer</h1>
      <div className="bg-white p-6 rounded-lg shadow-lg mb-6">
        <video
          ref={videoRef}
          autoPlay
          playsInline
          muted
          className="rounded-lg w-full max-w-md"
          style={{ display: stream ? "block" : "none" }}
        />
        <canvas ref={canvasRef} style={{ display: "none" }} />
        {!stream && (
          <div className="w-full max-w-md h-80 bg-gray-200 flex items-center justify-center rounded-lg text-gray-500">
            <p>Waiting for webcam...</p>
          </div>
        )}
      </div>
      <button
        onClick={capture}
        className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-full shadow-md transition duration-300 ease-in-out transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-75"
        disabled={!stream || isLoading}
      >
        {isLoading ? "Analyzing..." : "Capture & Analyze"}
      </button>

      {message && (
        <div className="mt-4 p-3 bg-blue-100 text-blue-800 rounded-md text-center w-full max-w-md">
          <p>{message}</p>
        </div>
      )}

      {feedback && (
        <div className="mt-6 p-6 bg-white rounded-lg shadow-lg w-full max-w-md">
          <h2 className="text-xl font-semibold mb-3 text-gray-700">Analysis Result:</h2>
          <p className="text-lg mb-2">
            <strong className="text-gray-900">Posture:</strong>{" "}
            <span className={feedback.posture === "good" ? "text-green-600" : "text-red-600"}>
              {feedback.posture?.toUpperCase() || ""}
            </span>
          </p>
          <p className="text-lg">
            <strong className="text-gray-900">Reason:</strong>{" "}
            {feedback.reason || "No reason provided."}
          </p>
        </div>
      )}
    </div>
  );
};

export default WebcamCapture;
// Note: This component uses the webcam to capture a single frame and analyze it.
// It does not handle video recording or multiple frames. For a full video analysis,
// consider using a different approach or integrating with the existing VideoUpload component.