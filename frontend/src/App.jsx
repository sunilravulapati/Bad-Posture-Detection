import React from "react";
import VideoUpload from "./components/VideoUpload";
import WebcamCapture from "./components/WebcamCapture";

function App() {
  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <h1 className="text-4xl font-bold text-blue-600 mb-4 text-center">
        Bad Posture Detection
      </h1>
      <p className="text-center text-gray-600 mb-10">
        Analyze squat or desk posture using AI + rule-based logic
      </p>

      <h2 className="text-2xl font-semibold mb-4">📁 Upload Video</h2>
      <VideoUpload />

      <h2 className="text-2xl font-semibold mt-12 mb-4">🎥 Live Webcam</h2>
      <WebcamCapture />
    </div>
  );
}

export default App;
