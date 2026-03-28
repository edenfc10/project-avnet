// ============================================================================
// Users Page - ניהול משתמשים
// ============================================================================
// דף זה מאפשר:
//   - צפייה בכל המשתמשים עם חיפוש וסינון לפי תפקיד
//   - יצירת משתמש חדש (admin יוצר agent, super_admin יוצר agent/admin)
//   - מחיקת משתמש (לא מוחק את עצמו, admin לא מוחק super_admin)
// ============================================================================

import { useEffect, useMemo, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { userAPI } from "../services/api";

export default function Users() {
  const { userRole, currentUser } = useAuth();
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
  const [deleteError, setDeleteError] = useState("");
  const [deleteSuccess, setDeleteSuccess] = useState("");
  const [deleteLoadingSid, setDeleteLoadingSid] = useState("");

  const canCreateUsers = userRole === "super_admin" || userRole === "admin";
  const canDeleteUsers = userRole === "super_admin" || userRole === "admin";

  const roleOptions = useMemo(() => {
    if (userRole === "super_admin") {
      return ["admin", "agent", "viewer"];
    }
    if (userRole === "admin") {
      return ["agent", "viewer"];
    }
    return [];
  }, [userRole]);

  const visibleUsers = useMemo(() => {
    const query = searchText.trim().toLowerCase();

    const usersForRole =
      userRole === "super_admin"
        ? users
        : users.filter((user) => user.role !== "super_admin");

    return usersForRole.filter((user) => {
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
  }, [users, searchText, roleFilter, userRole]);

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
      } else if (formData.role === "viewer") {
        await userAPI.createViewer(payload);
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

  const canDeleteTarget = (targetUser) => {
    if (!canDeleteUsers || !targetUser) {
      return false;
    }

    if ((targetUser.s_id || "") === (currentUser?.s_id || "")) {
      return false;
    }

    if (userRole === "admin" && targetUser.role === "super_admin") {
      return false;
    }

    return true;
  };

  const handleDeleteUser = async (targetUser) => {
    if (!canDeleteTarget(targetUser)) {
      setDeleteError("You are not allowed to delete this user.");
      return;
    }

    try {
      setDeleteLoadingSid(targetUser.s_id);
      setDeleteError("");
      setDeleteSuccess("");

      await userAPI.deleteUser(targetUser.s_id);
      setDeleteSuccess(`User ${targetUser.username} deleted successfully.`);
      await fetchUsers();
    } catch (err) {
      setDeleteError(err.response?.data?.detail || "Failed to delete user.");
    } finally {
      setDeleteLoadingSid("");
    }
  };

  useEffect(() => {
    if (!createError && !createSuccess && !deleteError && !deleteSuccess) {
      return;
    }

    const timer = setTimeout(() => {
      setCreateError("");
      setCreateSuccess("");
      setDeleteError("");
      setDeleteSuccess("");
    }, 3500);

    return () => clearTimeout(timer);
  }, [createError, createSuccess, deleteError, deleteSuccess]);

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
          {deleteError ? <div className="error-banner">{deleteError}</div> : null}
          {deleteSuccess ? <div className="success-banner">{deleteSuccess}</div> : null}
        </div>
      ) : (
        <div className="card">
          <div className="empty-state">Agents cannot create users.</div>
          {deleteError ? <div className="error-banner">{deleteError}</div> : null}
          {deleteSuccess ? <div className="success-banner">{deleteSuccess}</div> : null}
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
            {userRole === "super_admin" ? <option value="super_admin">super_admin</option> : null}
            <option value="admin">admin</option>
            <option value="agent">agent</option>
            <option value="viewer">viewer</option>
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
                {canDeleteUsers ? (
                  <div className="meeting-actions">
                    <button
                      className="btn-danger"
                      type="button"
                      onClick={() => handleDeleteUser(user)}
                      disabled={!canDeleteTarget(user) || deleteLoadingSid === user.s_id}
                      title={
                        canDeleteTarget(user)
                          ? "Delete user"
                          : "You are not allowed to delete this user"
                      }
                    >
                      {deleteLoadingSid === user.s_id ? "Deleting..." : "Delete"}
                    </button>
                  </div>
                ) : null}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
