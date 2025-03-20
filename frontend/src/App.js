import React, { useState, useEffect } from "react";
import axios from "axios";

function App() {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");
  const [publicUrl, setPublicUrl] = useState("");
  const [extractedText, setExtractedText] = useState("");
  const [documents, setDocuments] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [loading, setLoading] = useState(false);

  // 📌 Cargar lista de documentos al inicio
  useEffect(() => {
    fetchDocuments();
  }, []);

  // 📌 Obtener documentos desde el backend
  const fetchDocuments = async () => {
    try {
      const response = await axios.get("http://localhost:5000/api/documents");
      setDocuments(response.data);
    } catch (error) {
      console.error("Error fetching documents:", error);
    }
  };

  // 📌 Manejar selección de archivo
  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  // 📌 Manejar subida de archivo
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
  
      console.log("✅ Respuesta del backend:", response.data);
      setMessage(response.data.message);
      setPublicUrl(response.data.public_url);
      setExtractedText(response.data.extracted_text);
    } catch (error) {
      console.error("❌ Error en la petición:", error);
      console.error("❌ Respuesta completa:", error.response);
      setMessage(`Error: ${error.response?.data?.error || "Unknown error"}`);
    } finally {
      setLoading(false);
    }
  };
  
  

  // 📌 Filtrar documentos según la búsqueda
  const filteredDocuments = documents.filter((doc) =>
    doc.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div style={{ maxWidth: "600px", margin: "auto", textAlign: "center" }}>
      <h1>Gestor de Documentos</h1>

      {/* 📌 Formulario de subida */}
      <form onSubmit={handleSubmit} style={{ marginBottom: "20px" }}>
        <input type="file" onChange={handleFileChange} />
        <button type="submit" disabled={!file || loading}>
          {loading ? "Subiendo..." : "Subir"}
        </button>
      </form>

      {message && <p><strong>{message}</strong></p>}

      {/* 📌 Mostrar PDF subido */}
      {publicUrl && (
        <div>
          <h2>Documento Subido:</h2>
          <a href={publicUrl} target="_blank" rel="noopener noreferrer">
            {publicUrl}
          </a>
        </div>
      )}

      {/* 📌 Mostrar texto extraído */}
      {extractedText && (
        <div>
          <h2>Texto Extraído:</h2>
          <pre>{extractedText}</pre>
        </div>
      )}

      <hr />

      {/* 📌 Búsqueda de documentos */}
      <input
        type="text"
        placeholder="Buscar documento..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        style={{ width: "100%", padding: "8px", marginBottom: "10px" }}
      />

      {/* 📌 Lista de documentos */}
      <h2>Documentos Guardados</h2>
      <ul style={{ listStyle: "none", padding: 0 }}>
        {filteredDocuments.length > 0 ? (
          filteredDocuments.map((doc) => (
            <li key={doc.id} style={{ marginBottom: "10px" }}>
              <a href={doc.url} target="_blank" rel="noopener noreferrer">
                {doc.name}
              </a>
            </li>
          ))
        ) : (
          <p>No se encontraron documentos.</p>
        )}
      </ul>
    </div>
  );
}

export default App;
