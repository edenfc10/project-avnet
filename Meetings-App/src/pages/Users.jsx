import { useEffect, useMemo, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { userAPI } from "../services/api";

export default function Users() {
  const { userRole } = useAuth();
  const [users, setUsers] = useState([]);
  const [usersLoading, setUsersLoading] = useState(true);
  const [usersError, setUsersError] = useState("");

  const [searchText, setSearchText] = useState("");
  const [roleFilter, setRoleFilter] = useState("all");

  const [formData, setFormData] = useState({
    s_id: "",
    username: "",
    password: "",
    role: "agent",
  });
  const [submitting, setSubmitting] = useState(false);
  const [createError, setCreateError] = useState("");
  const [createSuccess, setCreateSuccess] = useState("");

  const canCreateUsers = userRole === "super_admin" || userRole === "admin";

  const roleOptions = useMemo(() => {
    if (userRole === "super_admin") {
      return ["admin", "agent"];
    }
    if (userRole === "admin") {
      return ["agent"];
    }
    return [];
  }, [userRole]);

  const visibleUsers = useMemo(() => {
    const query = searchText.trim().toLowerCase();

    return users.filter((user) => {
      const matchRole = roleFilter === "all" || user.role === roleFilter;
      if (!matchRole) {
        return false;
      }

      if (!query) {
        return true;
      }

      const bySid = (user.s_id || "").toLowerCase().includes(query);
      const byUsername = (user.username || "").toLowerCase().includes(query);
      return bySid || byUsername;
    });
  }, [users, searchText, roleFilter]);

  const fetchUsers = async () => {
    try {
      setUsersLoading(true);
      setUsersError("");
      const response = await userAPI.getAllUsers();
      setUsers(response.data || []);
    } catch (err) {
      setUsers([]);
      setUsersError(err.response?.data?.detail || "Failed to load users.");
    } finally {
      setUsersLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!canCreateUsers) {
      setCreateError("You are not allowed to create users.");
      return;
    }

    if (!formData.s_id.trim() || !formData.username.trim() || !formData.password.trim()) {
      setCreateError("All fields are required.");
      return;
    }

    if (!roleOptions.includes(formData.role)) {
      setCreateError("You are not allowed to create this role.");
      return;
    }

    const payload = {
      s_id: formData.s_id.trim(),
      username: formData.username.trim(),
      password: formData.password,
    };

    try {
      setSubmitting(true);
      setCreateError("");
      setCreateSuccess("");

      if (formData.role === "admin") {
        await userAPI.createAdmin(payload);
      } else {
        await userAPI.createAgent(payload);
      }

      setCreateSuccess(`${formData.role} user created successfully.`);
      setFormData({
        s_id: "",
        username: "",
        password: "",
        role: roleOptions[0] || "agent",
      });
      await fetchUsers();
    } catch (err) {
      setCreateError(err.response?.data?.detail || "Failed to create user.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="page">
      <h2 className="page-header">Users</h2>

      {canCreateUsers ? (
        <div className="card">
          <h3 className="card-title">Create New User</h3>
          <form className="user-create-form" onSubmit={handleSubmit}>
            <div className="user-form-grid">
              <input
                className="search-input"
                type="text"
                name="s_id"
                placeholder="S_ID"
                value={formData.s_id}
                onChange={handleChange}
                required
              />
              <input
                className="search-input"
                type="text"
                name="username"
                placeholder="Username"
                value={formData.username}
                onChange={handleChange}
                required
              />
              <input
                className="search-input"
                type="password"
                name="password"
                placeholder="Password"
                value={formData.password}
                onChange={handleChange}
                required
              />
              <select
                className="search-select"
                name="role"
                value={formData.role}
                onChange={handleChange}
              >
                {roleOptions.map((option) => (
                  <option key={option} value={option}>
                    {option}
                  </option>
                ))}
              </select>
            </div>

            <button className="search-button" type="submit" disabled={submitting}>
              {submitting ? "Creating..." : "Create User"}
            </button>
          </form>

          {createError ? <div className="error-banner">{createError}</div> : null}
          {createSuccess ? <div className="success-banner">{createSuccess}</div> : null}
        </div>
      ) : (
        <div className="card">
          <div className="empty-state">Agents cannot create users.</div>
        </div>
      )}

      <div className="card fill">
        <h3 className="card-title">Users Directory</h3>

        <div className="users-filter-row">
          <input
            className="search-input"
            type="text"
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            placeholder="Search by S_ID or username"
          />

          <select
            className="search-select"
            value={roleFilter}
            onChange={(e) => setRoleFilter(e.target.value)}
          >
            <option value="all">All Roles</option>
            <option value="super_admin">super_admin</option>
            <option value="admin">admin</option>
            <option value="agent">agent</option>
          </select>

          <button className="btn-secondary" type="button" onClick={fetchUsers}>
            Refresh
          </button>
        </div>

        {usersError ? <div className="error-banner">{usersError}</div> : null}

        <div className="meetings-list">
          {usersLoading ? (
            <div className="empty-state">Loading users...</div>
          ) : visibleUsers.length === 0 ? (
            <div className="empty-state">No users found for this filter.</div>
          ) : (
            visibleUsers.map((user) => (
              <div key={user.UUID} className="meeting-row">
                <div>
                  <div className="meeting-title-row">
                    <div className="meeting-title">{user.username}</div>
                    <span className={`user-role-badge role-${user.role}`}>{user.role}</span>
                  </div>
                  <div className="meeting-meta">S_ID: {user.s_id}</div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
