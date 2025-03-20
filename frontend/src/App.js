import React, { useState } from "react";
import axios from "axios";

function App() {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");
  const [publicUrl, setPublicUrl] = useState("");
  const [extractedText, setExtractedText] = useState("");

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post("http://localhost:5000/api/upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      setMessage(response.data.message);
      setPublicUrl(response.data.public_url);
      setExtractedText(response.data.extracted_text);
    } catch (error) {
      console.error("Error uploading file:", error);
      setMessage("Error uploading file");
    }
  };

  return (
    <div>
      <h1>Upload PDF and Extract Text</h1>
      <form onSubmit={handleSubmit}>
        <input type="file" onChange={handleFileChange} />
        <button type="submit">Upload</button>
      </form>

      {message && <p>{message}</p>}
      {publicUrl && (
        <div>
          <h2>Public URL:</h2>
          <a href={publicUrl} target="_blank" rel="noopener noreferrer">
            {publicUrl}
          </a>
        </div>
      )}
      {extractedText && (
        <div>
          <h2>Extracted Text:</h2>
          <pre>{extractedText}</pre>
        </div>
      )}
    </div>
  );
}

export default App;