import { useAuth } from "../context/AuthContext";
import TaskList from "../components/TaskList";
import SearchBar from "../components/SearchBar";

export default function UserDashboard() {
  const { user, logout } = useAuth();

  return (
    <div className="page">
      <header className="topbar">
        <h2>My Dashboard</h2>
        <div>
          <span>Hi, {user.username}</span>
          <button onClick={logout}>Logout</button>
        </div>
      </header>

      <SearchBar />
      <TaskList isAdmin={false} />
    </div>
  );
}
