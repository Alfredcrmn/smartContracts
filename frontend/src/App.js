import React, { useState, useEffect } from "react";
import axios from "axios";
import "./App.css"; // Importar el CSS mejorado

function App() {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");
  const [publicUrl, setPublicUrl] = useState("");
  const [extractedText, setExtractedText] = useState("");
  const [documents, setDocuments] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      const response = await axios.get("http://127.0.0.1:5000/api/documents");
      setDocuments(response.data);
    } catch (error) {
      console.error("Error obteniendo documentos:", error.response?.data || error.message);
    }
  };

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage("");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post("http://127.0.0.1:5000/api/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      setMessage(response.data.message);
      setPublicUrl(response.data.public_url);
      setExtractedText(response.data.extracted_text);
      fetchDocuments(); // Actualizar lista de documentos
    } catch (error) {
      console.error("Error en la petición:", error);
      setMessage(`Error: ${error.response?.data?.error || "Unknown error"}`);
    } finally {
      setLoading(false);
    }
  };

  const filteredDocuments = documents.filter((doc) =>
    doc.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    doc.extracted_text.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="container">
      <h1>Smart Contracts</h1>

      {/*Formulario de subida */}
      <form className="upload-form" onSubmit={handleSubmit}>
        <input type="file" className="file-input" onChange={handleFileChange} />
        <button type="submit" className="upload-btn" disabled={!file || loading}>
          {loading ? "Subiendo..." : "Subir"}
        </button>
      </form>

      {message && <p className="message">{message}</p>}

      {/*Mostrar PDF subido */}
      {publicUrl && (
        <div className="result-section">
          <h2>Documento Subido:</h2>
          <a href={publicUrl} target="_blank" rel="noopener noreferrer">
            {publicUrl}
          </a>
        </div>
      )}

      {/*Mostrar texto extraído */}
      {extractedText && (
        <div className="result-section">
          <h2>Texto Extraído:</h2>
          <pre>{extractedText}</pre>
        </div>
      )}

      <hr />

      {/*Búsqueda de documentos */}
      <input
        type="text"
        placeholder="Buscar documento..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        className="search-input"
      />

      {/*Lista de documentos */}
      <h2>Documentos Guardados</h2>
      <div className="document-list">
        {filteredDocuments.length > 0 ? (
          filteredDocuments.map((doc) => (
            <div key={doc.id} className="document-card">
              <a href={doc.url} target="_blank" rel="noopener noreferrer" className="document-link">
                {doc.name}
              </a>
            </div>
          ))
        ) : (
          <p className="no-documents">No se encontraron documentos.</p>
        )}
      </div>
    </div>
  );
}

export default App;
