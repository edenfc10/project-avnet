import { useEffect, useState } from "react";
import { madorAPI } from "../services/api";
import { useAuth } from "../context/AuthContext";

export default function Groups() {
  const { userRole } = useAuth();
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [createName, setCreateName] = useState("");
  const [createLoading, setCreateLoading] = useState(false);
  const [createError, setCreateError] = useState("");
  const [createSuccess, setCreateSuccess] = useState("");

  const isSuperAdmin = userRole === "super_admin";

  const loadGroups = async () => {
    try {
      setLoading(true);
      setError("");
      const response = await madorAPI.listMadors();
      setGroups(response.data || []);
    } catch (err) {
      const message = err.response?.data?.detail || "Failed to load groups.";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadGroups();
  }, []);

  const handleCreateGroup = async (e) => {
    e.preventDefault();

    if (!isSuperAdmin) {
      setCreateError("Only super_admin can create a group.");
      return;
    }

    const trimmed = createName.trim();
    if (!trimmed) {
      setCreateError("Group name is required.");
      return;
    }

    try {
      setCreateLoading(true);
      setCreateError("");
      setCreateSuccess("");

      await madorAPI.createMador({ name: trimmed });

      setCreateName("");
      setCreateSuccess("Group created successfully.");
      await loadGroups();
    } catch (err) {
      const message = err.response?.data?.detail || "Failed to create group.";
      setCreateError(message);
    } finally {
      setCreateLoading(false);
    }
  };

  return (
    <div className="page">
      <h2 className="page-header">Groups</h2>

      {isSuperAdmin ? (
        <div className="card">
          <h3 className="card-title">Create Group</h3>
          <form className="group-create-form" onSubmit={handleCreateGroup}>
            <input
              type="text"
              className="search-input"
              placeholder="Enter group (mador) name"
              value={createName}
              onChange={(e) => setCreateName(e.target.value)}
              maxLength={120}
            />
            <button className="search-button" type="submit" disabled={createLoading}>
              {createLoading ? "Creating..." : "Create Group"}
            </button>
          </form>

          {createError ? <div className="error-banner">{createError}</div> : null}
          {createSuccess ? <div className="success-banner">{createSuccess}</div> : null}
        </div>
      ) : (
        <div className="card">
          <div className="empty-state">Only super_admin can create a group.</div>
        </div>
      )}

      <div className="card fill">
        <h3 className="card-title">All Groups ({groups.length})</h3>

        {loading ? <div className="empty-state">Loading groups...</div> : null}
        {error ? <div className="error-banner">{error}</div> : null}

        {!loading && !error ? (
          <div className="meetings-list">
            {groups.length === 0 ? (
              <div className="empty-state">No groups found.</div>
            ) : (
              groups.map((group) => (
                <div key={group.id} className="meeting-row">
                  <div>
                    <div className="meeting-title">{group.name}</div>
                    <div className="meeting-meta">
                      Creator: {group.creator?.username || "-"} • Members: {group.members?.length || 0} • Meetings: {group.meetings?.length || 0}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        ) : null}
      </div>
    </div>
  );
}
