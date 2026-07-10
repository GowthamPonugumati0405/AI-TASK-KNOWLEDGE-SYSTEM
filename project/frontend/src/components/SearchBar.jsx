import { useState } from "react";
import api from "../api/axios";

export default function SearchBar() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setSearched(true);
    try {
      const { data } = await api.post("/search/", { query, top_k: 5 });
      setResults(data.results);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h3>Search Knowledge Base</h3>
      <form onSubmit={handleSearch} className="inline-form">
        <input
          placeholder="Ask a question about the uploaded documents..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button type="submit" disabled={loading}>
          {loading ? "Searching..." : "Search"}
        </button>
      </form>

      {searched && !loading && results.length === 0 && (
        <p>No relevant results found. Try a different query or upload more documents.</p>
      )}

      <div className="results">
        {results.map((r, i) => (
          <div key={i} className="result-item">
            <div className="result-header">
              <strong>{r.document_title}</strong>
              <span className="score">score: {r.score.toFixed(3)}</span>
            </div>
            <p>{r.chunk_text}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
