import React, { useState } from "react";

function App() {
  const [files, setFiles] = useState([]);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [step, setStep] = useState(1); // 1 = Upload, 2 = Ask
  const [loading, setLoading] = useState(false);

  // Add new files to the list, preserving previous ones
  const handleFileChange = (e) => {
    const selected = Array.from(e.target.files);
    // Avoid duplicates by name (optional)
    const existingNames = new Set(files.map((file) => file.name));
    const newFiles = selected.filter((file) => !existingNames.has(file.name));
    setFiles([...files, ...newFiles]);
    e.target.value = null; // Reset input so same file can be re-added
  };

  const handleRemoveFile = (index) => {
    const updatedFiles = [...files];
    updatedFiles.splice(index, 1);
    setFiles(updatedFiles);
  };

  const handleFileUpload = async () => {
    setLoading(true);
    setAnswer("");

    const formData = new FormData();
    files.forEach((file) => formData.append("files", file));

    try {
      const response = await fetch("http://localhost:8888/upload", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      if (data.status === "ready") {
        setStep(2);
      } else {
        alert("Upload failed: " + (data.error || "Unknown error"));
      }
    } catch (err) {
      alert("Upload error: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleQuestionSubmit = async () => {
    setLoading(true);
    setAnswer("");

    try {
      const res = await fetch("http://localhost:8888/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question }),
      });

      const data = await res.json();
      if (data.answer) {
        setAnswer(data.answer);
      } else {
        setAnswer("Error: " + (data.error || "Unknown issue"));
      }
    } catch (err) {
      setAnswer("Error: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 600, margin: "auto", padding: "1rem" }}>
      <h1>PDFBot Q&A</h1>

      {step === 1 && (
        <>
          <input
            type="file"
            multiple
            accept=".pdf,.jpg,.jpeg,.png"
            onChange={handleFileChange}
          />

          {/* Show list of selected files with remove option */}
          <ul style={{ marginTop: "1rem", paddingLeft: "1rem" }}>
            {files.map((file, index) => (
              <li key={index}>
                {file.name}
                <button
                  onClick={() => handleRemoveFile(index)}
                  style={{
                    marginLeft: "0.5rem",
                    color: "red",
                    border: "none",
                    background: "transparent",
                    cursor: "pointer",
                  }}
                >
                  ❌
                </button>
              </li>
            ))}
          </ul>

          <button
            onClick={handleFileUpload}
            disabled={loading || files.length === 0}
            style={{ display: "block", marginTop: "1rem" }}
          >
            {loading ? "Uploading..." : "Upload Files"}
          </button>
        </>
      )}

      {step === 2 && (
        <>
          <textarea
            rows={3}
            style={{ width: "100%", marginTop: "1rem" }}
            placeholder="Ask a question about your uploaded documents..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
          />
          <br />
          <button
            onClick={handleQuestionSubmit}
            disabled={loading || !question.trim()}
          >
            {loading ? "Processing..." : "Ask Question"}
          </button>

          {answer && (
            <div style={{ marginTop: "1.5rem", background: "#f0f0f0", padding: "1rem" }}>
              <strong>Answer:</strong>
              <p>{answer}</p>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default App;
