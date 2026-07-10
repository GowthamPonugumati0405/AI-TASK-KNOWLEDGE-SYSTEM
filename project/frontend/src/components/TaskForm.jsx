import { useState } from "react";
import api from "../api/axios";

export default function TaskForm({ onCreated }) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [assignedTo, setAssignedTo] = useState("");
  const [message, setMessage] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage("");
    try {
      await api.post("/tasks/", {
        title,
        description,
        assigned_to: Number(assignedTo),
      });
      setTitle("");
      setDescription("");
      setAssignedTo("");
      setMessage("Task created.");
      onCreated?.();
    } catch (err) {
      setMessage(err.response?.data?.detail || "Failed to create task.");
    }
  };

  return (
    <div className="card">
      <h3>Assign New Task</h3>
      <form onSubmit={handleSubmit} className="inline-form">
        <input
          placeholder="Title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
        />
        <input
          placeholder="Description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
        <input
          placeholder="Assign to user ID"
          type="number"
          value={assignedTo}
          onChange={(e) => setAssignedTo(e.target.value)}
          required
        />
        <button type="submit">Create Task</button>
      </form>
      {message && <p className="hint">{message}</p>}
    </div>
  );
}
