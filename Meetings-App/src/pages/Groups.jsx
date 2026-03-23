import { useEffect, useState } from "react";
import { madorAPI, userAPI } from "../services/api";
import { useAuth } from "../context/AuthContext";

export default function Groups() {
  const { userRole, currentUser } = useAuth();
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [createName, setCreateName] = useState("");
  const [createLoading, setCreateLoading] = useState(false);
  const [createError, setCreateError] = useState("");
  const [createSuccess, setCreateSuccess] = useState("");
  const [deleteError, setDeleteError] = useState("");
  const [deleteSuccess, setDeleteSuccess] = useState("");
  const [deleteLoadingId, setDeleteLoadingId] = useState("");

  // Member management modal state
  const [selectedGroup, setSelectedGroup] = useState(null);
  const [allUsers, setAllUsers] = useState([]);
  const [addUserId, setAddUserId] = useState("");
  const [modalError, setModalError] = useState("");
  const [modalLoading, setModalLoading] = useState(false);
  const [accessDrafts, setAccessDrafts] = useState({});

  const isSuperAdmin = userRole === "super_admin";
  const isAdmin = userRole === "admin";
  const canManage = isSuperAdmin || isAdmin;

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

  useEffect(() => {
    if (canManage) {
      userAPI.getAllUsers()
        .then((res) => setAllUsers(res.data || []))
        .catch(() => {});
    }
  }, [canManage]);

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

  const handleGroupDoubleClick = (group) => {
    const canManageThis = canManage;
    if (!canManageThis) return;
    setSelectedGroup(group);
    setModalError("");
    setAddUserId("");
    const initialDrafts = {};
    (group.member_access_levels || []).forEach((row) => {
      initialDrafts[String(row.user_id)] = row.access_level;
    });
    setAccessDrafts(initialDrafts);
  };

  const handleDeleteGroup = async (group) => {
    if (!canManage) {
      setDeleteError("Only admin or super_admin can delete groups.");
      return;
    }

    try {
      setDeleteLoadingId(String(group.id));
      setDeleteError("");
      setDeleteSuccess("");
      await madorAPI.deleteMador(group.id);
      setGroups((prev) => prev.filter((g) => String(g.id) !== String(group.id)));
      if (selectedGroup && String(selectedGroup.id) === String(group.id)) {
        setSelectedGroup(null);
      }
      setDeleteSuccess(`Group ${group.name} deleted successfully.`);
    } catch (err) {
      setDeleteError(err.response?.data?.detail || "Failed to delete group.");
    } finally {
      setDeleteLoadingId("");
    }
  };

  const handleAddMember = async () => {
    if (!addUserId || !selectedGroup) return;
    try {
      setModalLoading(true);
      setModalError("");
      const res = await madorAPI.addMember(selectedGroup.id, addUserId);
      const updated = res.data;
      setSelectedGroup(updated);
      setAddUserId("");
      setGroups((prev) => prev.map((g) => g.id === updated.id ? updated : g));
    } catch (err) {
      setModalError(err.response?.data?.detail || "Failed to add member.");
    } finally {
      setModalLoading(false);
    }
  };

  const handleRemoveMember = async (memberUUID) => {
    if (!selectedGroup) return;
    try {
      setModalLoading(true);
      setModalError("");
      const res = await madorAPI.removeMember(selectedGroup.id, memberUUID);
      const updated = res.data;
      setSelectedGroup(updated);
      setGroups((prev) => prev.map((g) => g.id === updated.id ? updated : g));
    } catch (err) {
      setModalError(err.response?.data?.detail || "Failed to remove member.");
    } finally {
      setModalLoading(false);
    }
  };

  const handleUpdateAccessLevel = async (memberUUID) => {
    if (!selectedGroup) return;
    const nextLevel = accessDrafts[String(memberUUID)] || "standard";

    try {
      setModalLoading(true);
      setModalError("");

      await madorAPI.updateMemberAccessLevel(selectedGroup.id, memberUUID, nextLevel);
      const groupsRes = await madorAPI.listMadors();
      const refreshedGroups = groupsRes.data || [];
      setGroups(refreshedGroups);

      const refreshed = refreshedGroups.find((g) => String(g.id) === String(selectedGroup.id));
      if (refreshed) {
        setSelectedGroup(refreshed);
      }
    } catch (err) {
      setModalError(err.response?.data?.detail || "Failed to update access level.");
    } finally {
      setModalLoading(false);
    }
  };

  const getMemberAccessLevel = (memberUUID) => {
    const fromDraft = accessDrafts[String(memberUUID)];
    if (fromDraft) {
      return fromDraft;
    }

    const found = (selectedGroup?.member_access_levels || []).find(
      (row) => String(row.user_id) === String(memberUUID)
    );
    return found?.access_level || "standard";
  };

  const availableAgents = allUsers.filter(
    (u) =>
      u.role === "agent" &&
      !selectedGroup?.members?.some((m) => String(m.UUID) === String(u.UUID))
  );

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
          {deleteError ? <div className="error-banner">{deleteError}</div> : null}
          {deleteSuccess ? <div className="success-banner">{deleteSuccess}</div> : null}
        </div>
      ) : (
        <div className="card">
          <div className="empty-state">Only super_admin can create a group.</div>
          {deleteError ? <div className="error-banner">{deleteError}</div> : null}
          {deleteSuccess ? <div className="success-banner">{deleteSuccess}</div> : null}
        </div>
      )}

      <div className="card fill">
        <h3 className="card-title">All Groups ({groups.length})</h3>

        {canManage && (
          <p className="info-hint">Double-click a group to manage its members.</p>
        )}

        {loading ? <div className="empty-state">Loading groups...</div> : null}
        {error ? <div className="error-banner">{error}</div> : null}

        {!loading && !error ? (
          <div className="meetings-list">
            {groups.length === 0 ? (
              <div className="empty-state">No groups found.</div>
            ) : (
              groups.map((group) => {
                const canManageThis = canManage;
                return (
                  <div
                    key={group.id}
                    className={`meeting-row${canManageThis ? " group-clickable" : ""}`}
                    onDoubleClick={() => handleGroupDoubleClick(group)}
                    title={canManageThis ? "Double-click to manage members" : ""}
                  >
                    <div>
                      <div className="meeting-title">{group.name}</div>
                      <div className="meeting-meta">
                        Creator: {group.creator?.username || "-"} &bull; Members:{" "}
                        {group.members?.length || 0} &bull; Meetings:{" "}
                        {group.meetings?.length || 0}
                      </div>
                    </div>
                    {canManageThis && (
                      <div className="meeting-actions">
                        <span className="badge-manage">Manage</span>
                        <button
                          className="btn-danger"
                          type="button"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDeleteGroup(group);
                          }}
                          disabled={deleteLoadingId === String(group.id)}
                        >
                          {deleteLoadingId === String(group.id) ? "Deleting..." : "Delete"}
                        </button>
                      </div>
                    )}
                  </div>
                );
              })
            )}
          </div>
        ) : null}
      </div>

      {selectedGroup && (
        <div className="modal-overlay" onClick={() => setSelectedGroup(null)}>
          <div
            className="modal-card"
            style={{ width: 520, maxWidth: "calc(100vw - 32px)" }}
            onClick={(e) => e.stopPropagation()}
          >
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: 16,
              }}
            >
              <h3 className="modal-title" style={{ margin: 0 }}>
                Manage Members &mdash; {selectedGroup.name}
              </h3>
              <button
                className="btn-secondary"
                onClick={() => setSelectedGroup(null)}
                style={{ lineHeight: 1, padding: "4px 10px" }}
              >
                &#x2715;
              </button>
            </div>

            {modalError && <div className="error-banner">{modalError}</div>}

            <h4 style={{ margin: "0 0 8px 0", fontSize: 14, color: "var(--text-700)" }}>
              Current Members ({selectedGroup.members?.length || 0})
            </h4>

            {!selectedGroup.members?.length ? (
              <div className="empty-state" style={{ marginBottom: 16 }}>
                No members yet.
              </div>
            ) : (
              <div className="meetings-list" style={{ maxHeight: 200, marginBottom: 16 }}>
                {selectedGroup.members.map((member) => (
                  <div key={member.UUID} className="meeting-row">
                    <div>
                      <div className="meeting-title">{member.username}</div>
                      <div className="meeting-meta">{member.role}</div>
                    </div>
                    <div className="meeting-actions">
                      <select
                        className="search-select"
                        value={getMemberAccessLevel(member.UUID)}
                        onChange={(e) =>
                          setAccessDrafts((prev) => ({
                            ...prev,
                            [String(member.UUID)]: e.target.value,
                          }))
                        }
                        disabled={modalLoading}
                        style={{ minWidth: 120 }}
                      >
                        <option value="audio">audio</option>
                        <option value="video">video</option>
                        <option value="blast_dial">blast_dial</option>
                        <option value="full">full (legacy)</option>
                        <option value="restricted">restricted (legacy)</option>
                        <option value="standard">standard (legacy)</option>
                      </select>
                      <button
                        className="btn-secondary"
                        onClick={() => handleUpdateAccessLevel(member.UUID)}
                        disabled={modalLoading}
                      >
                        Save
                      </button>
                      <button
                        className="btn-danger"
                        onClick={() => handleRemoveMember(member.UUID)}
                        disabled={modalLoading}
                      >
                        Remove
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}

            <h4 style={{ margin: "0 0 8px 0", fontSize: 14, color: "var(--text-700)" }}>
              Add Agent
            </h4>
            {availableAgents.length === 0 ? (
              <div className="empty-state">No available agents to add.</div>
            ) : (
              <div style={{ display: "flex", gap: "0.5rem" }}>
                <select
                  className="search-input"
                  value={addUserId}
                  onChange={(e) => setAddUserId(e.target.value)}
                  style={{ flex: 1 }}
                >
                  <option value="">Select an agent...</option>
                  {availableAgents.map((u) => (
                    <option key={u.UUID} value={u.UUID}>
                      {u.username} ({u.s_id})
                    </option>
                  ))}
                </select>
                <button
                  className="search-button"
                  onClick={handleAddMember}
                  disabled={modalLoading || !addUserId}
                >
                  {modalLoading ? "..." : "Add"}
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
