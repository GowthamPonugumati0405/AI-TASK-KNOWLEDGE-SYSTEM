import { useEffect, useState } from "react";
import api from "../api/axios";

export default function DocumentUpload() {
  const [file, setFile] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [message, setMessage] = useState("");
  const [uploading, setUploading] = useState(false);

  const fetchDocuments = async () => {
    const { data } = await api.get("/documents/");
    setDocuments(data);
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return;
    setUploading(true);
    setMessage("");

    const formData = new FormData();
    formData.append("file", file);

    try {
      await api.post("/documents/", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setMessage("Document uploaded and indexed.");
      setFile(null);
      fetchDocuments();
    } catch (err) {
      setMessage(err.response?.data?.detail || "Upload failed.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="card">
      <h3>Knowledge Base Documents</h3>
      <form onSubmit={handleUpload} className="inline-form">
        <input
          type="file"
          accept=".txt"
          onChange={(e) => setFile(e.target.files[0])}
        />
        <button type="submit" disabled={uploading}>
          {uploading ? "Uploading..." : "Upload .txt"}
        </button>
      </form>
      {message && <p className="hint">{message}</p>}

      <table>
        <thead>
          <tr>
            <th>Title</th>
            <th>Chunks</th>
            <th>Uploaded</th>
          </tr>
        </thead>
        <tbody>
          {documents.map((doc) => (
            <tr key={doc.id}>
              <td>{doc.title}</td>
              <td>{doc.chunk_count}</td>
              <td>{new Date(doc.created_at).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
