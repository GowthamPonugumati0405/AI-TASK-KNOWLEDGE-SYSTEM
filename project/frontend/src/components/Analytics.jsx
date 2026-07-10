import { useEffect, useState } from "react";
import api from "../api/axios";

export default function Analytics() {
  const [data, setData] = useState(null);

  useEffect(() => {
    api.get("/analytics/").then((res) => setData(res.data));
  }, []);

  if (!data) return <p>Loading analytics...</p>;

  return (
    <div className="card">
      <h3>Analytics</h3>
      <div className="stat-grid">
        <div className="stat">
          <span className="stat-value">{data.total_tasks}</span>
          <span className="stat-label">Total Tasks</span>
        </div>
        <div className="stat">
          <span className="stat-value">{data.completed_tasks}</span>
          <span className="stat-label">Completed</span>
        </div>
        <div className="stat">
          <span className="stat-value">{data.pending_tasks}</span>
          <span className="stat-label">Pending</span>
        </div>
        <div className="stat">
          <span className="stat-value">{data.total_documents}</span>
          <span className="stat-label">Documents</span>
        </div>
        <div className="stat">
          <span className="stat-value">{data.total_users}</span>
          <span className="stat-label">Users</span>
        </div>
      </div>

      <h4>Most Searched Queries</h4>
      {data.most_searched_queries.length === 0 ? (
        <p>No searches logged yet.</p>
      ) : (
        <ul>
          {data.most_searched_queries.map((q, i) => (
            <li key={i}>
              "{q.query}" — {q.count} time{q.count > 1 ? "s" : ""}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
