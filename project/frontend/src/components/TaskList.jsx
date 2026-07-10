import { useEffect, useState } from "react";
import api from "../api/axios";

export default function TaskList({ isAdmin }) {
  const [tasks, setTasks] = useState([]);
  const [statusFilter, setStatusFilter] = useState("");
  const [loading, setLoading] = useState(true);

  const fetchTasks = async () => {
    setLoading(true);
    const params = {};
    if (statusFilter) params.status = statusFilter;
    const { data } = await api.get("/tasks/", { params });
    setTasks(data);
    setLoading(false);
  };

  useEffect(() => {
    fetchTasks();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [statusFilter]);

  const updateStatus = async (taskId, status) => {
    await api.patch(`/tasks/${taskId}/status`, { status });
    fetchTasks();
  };

  return (
    <div className="card">
      <div className="card-header">
        <h3>{isAdmin ? "All Tasks" : "My Tasks"}</h3>
        <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
          <option value="">All statuses</option>
          <option value="pending">Pending</option>
          <option value="completed">Completed</option>
        </select>
      </div>

      {loading ? (
        <p>Loading...</p>
      ) : tasks.length === 0 ? (
        <p>No tasks found.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Title</th>
              <th>Description</th>
              <th>Status</th>
              {!isAdmin && <th>Action</th>}
            </tr>
          </thead>
          <tbody>
            {tasks.map((task) => (
              <tr key={task.id}>
                <td>{task.title}</td>
                <td>{task.description}</td>
                <td>
                  <span className={`badge ${task.status}`}>{task.status}</span>
                </td>
                {!isAdmin && (
                  <td>
                    {task.status === "pending" ? (
                      <button onClick={() => updateStatus(task.id, "completed")}>
                        Mark Completed
                      </button>
                    ) : (
                      <button onClick={() => updateStatus(task.id, "pending")}>
                        Reopen
                      </button>
                    )}
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
