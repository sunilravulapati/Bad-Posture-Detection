import React, { useState } from "react";
import axios from "axios";

const VideoUpload = () => {
  const [videoFile, setVideoFile] = useState(null);
  const [feedback, setFeedback] = useState([]);
  const [loading, setLoading] = useState(false);
  const [videoURL, setVideoURL] = useState(null);
  const [mode, setMode] = useState("frame");

  const backendUrl = import.meta.env.VITE_BACKEND_URL;

  const handleUpload = async () => {
    if (!videoFile) {
      alert("Please select a video file first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", videoFile);
    setLoading(true);
    setFeedback([]);

    try {
      const response = await axios.post(
        `${backendUrl}/analyze?mode=${mode}`,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      setFeedback(response.data.feedback || []);
    } catch (err) {
      alert("Upload failed. Please check if your backend is running and CORS is allowed.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    setVideoFile(file);
    setVideoURL(file ? URL.createObjectURL(file) : null);
  };

  return (
    <div className="bg-white p-6 rounded-xl shadow-lg max-w-xl mx-auto mt-10">
      <h2 className="text-2xl font-bold mb-4 text-gray-800">Posture Video Analyzer</h2>

      {/* Mode Toggle */}
      <div className="mb-4">
        <label className="mr-2 font-medium">Analysis Mode:</label>
        <select
          value={mode}
          onChange={(e) => setMode(e.target.value)}
          className="p-2 border rounded"
        >
          <option value="frame">Frame-by-Frame</option>
          <option value="summary">AI Summary</option>
        </select>
      </div>

      {/* File Input */}
      <input
        type="file"
        accept="video/*"
        onChange={handleFileChange}
        className="block w-full mb-4 text-sm text-gray-700 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:bg-blue-600 file:text-white hover:file:bg-blue-700"
      />

      {/* Preview */}
      {videoURL && (
        <video src={videoURL} controls className="w-full h-auto mb-4 rounded" />
      )}

      {/* Analyze Button */}
      <button
        onClick={handleUpload}
        className="w-full py-2 px-4 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
        disabled={loading}
      >
        {loading ? "Analyzing..." : "Analyze Video"}
      </button>

      {/* AI Summary */}
      {mode === "summary" && !loading && feedback && feedback.accuracy && (
        <div className="mt-6 bg-blue-50 p-4 rounded text-blue-900 shadow">
          <h3 className="text-lg font-semibold mb-2">Summary Report:</h3>
          <p><strong>Accuracy:</strong> {feedback.accuracy}%</p>
          <p><strong>Bad Posture Frames:</strong> {feedback.bad_posture_frames}</p>
          <p><strong>Top Issue:</strong> {feedback.top_issue || "None"}</p>
        </div>
      )}

      {/* Frame-by-Frame Feedback */}
      {mode === "frame" && feedback.length > 0 && (
        <div className="mt-6">
          <h3 className="text-xl font-semibold mb-2 text-gray-800">Feedback:</h3>
          <ul className="space-y-2 max-h-64 overflow-y-auto">
            {feedback.map((f, i) => (
              <li
                key={i}
                className={`p-3 rounded-md border shadow-sm transition-all duration-200 ${
                  f.posture === "bad"
                    ? "bg-red-100 text-red-800 border-red-300"
                    : "bg-green-100 text-green-800 border-green-300"
                }`}
              >
                Frame {f.frame}:{" "}
                <strong className="uppercase">{f.posture}</strong>{" "}
                {f.reason && <span>– {f.reason}</span>}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* No Issues */}
      {!loading && feedback.length === 0 && videoFile && mode === "frame" && (
        <p className="mt-4 text-sm text-gray-500">No posture issues detected.</p>
      )}
    </div>
  );
};

export default VideoUpload;
