import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import TaskForm from "../components/TaskForm";
import TaskList from "../components/TaskList";
import DocumentUpload from "../components/DocumentUpload";
import SearchBar from "../components/SearchBar";
import Analytics from "../components/Analytics";

export default function AdminDashboard() {
  const { user, logout } = useAuth();
  const [refreshKey, setRefreshKey] = useState(0);

  return (
    <div className="page">
      <header className="topbar">
        <h2>Admin Dashboard</h2>
        <div>
          <span>Hi, {user.username}</span>
          <button onClick={logout}>Logout</button>
        </div>
      </header>

      <Analytics key={`analytics-${refreshKey}`} />
      <DocumentUpload />
      <SearchBar />
      <TaskForm onCreated={() => setRefreshKey((k) => k + 1)} />
      <TaskList isAdmin key={`tasks-${refreshKey}`} />
    </div>
  );
}
