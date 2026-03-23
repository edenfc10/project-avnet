import { useEffect, useMemo, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { cmsAPI, madorAPI } from "../services/api";

const PAGE_SIZE = 5;

export default function MeetingsPage({ title, data, loading = false, error = "" }) {
  const { userRole, currentUser } = useAuth();
  const [query, setQuery] = useState("");
  const [submittedQuery, setSubmittedQuery] = useState("");
  const [searchBy, setSearchBy] = useState("meetingId");
  const [page, setPage] = useState(1);
  const [selectedMeeting, setSelectedMeeting] = useState(null);
  const [localMeetings, setLocalMeetings] = useState([]);
  const [createError, setCreateError] = useState("");
  const [createSuccess, setCreateSuccess] = useState("");
  const [openLoading, setOpenLoading] = useState(false);
  const [openError, setOpenError] = useState("");
  const [passwordInput, setPasswordInput] = useState("");
  const [passwordUpdating, setPasswordUpdating] = useState(false);
  const [passwordError, setPasswordError] = useState("");
  const [passwordSuccess, setPasswordSuccess] = useState("");
  const [deleteError, setDeleteError] = useState("");
  const [deleteSuccess, setDeleteSuccess] = useState("");
  const [deleteLoadingId, setDeleteLoadingId] = useState("");
  const [deletedCmsIds, setDeletedCmsIds] = useState([]);
  const [createLoading, setCreateLoading] = useState(false);
  const [availableMadors, setAvailableMadors] = useState([]);
  const [newMeeting, setNewMeeting] = useState({
    meetingId: "",
    madorId: "",
  });

  const visibleCmsMeetings = useMemo(
    () => data.filter((item) => !deletedCmsIds.includes(item.id)),
    [data, deletedCmsIds]
  );

  const allMeetings = useMemo(
    () => [...localMeetings, ...visibleCmsMeetings],
    [localMeetings, visibleCmsMeetings]
  );

  const filteredMeetings = useMemo(() => {
    if (!submittedQuery.trim()) return allMeetings;

    const q = submittedQuery.toLowerCase();

    return allMeetings.filter((m) => {
      if (searchBy === "meetingId") {
        return m.meetingId.toLowerCase().includes(q);
      }
      if (searchBy === "group") {
        return m.group.toLowerCase().includes(q);
      }
      if (searchBy === "name") {
        return (m.name || "").toLowerCase().includes(q);
      }
      return true;
    });
  }, [submittedQuery, searchBy, allMeetings]);

  const totalPages = Math.max(1, Math.ceil(filteredMeetings.length / PAGE_SIZE));

  const pagedMeetings = useMemo(() => {
    const start = (page - 1) * PAGE_SIZE;
    return filteredMeetings.slice(start, start + PAGE_SIZE);
  }, [filteredMeetings, page]);

  const handleSearch = () => {
    setSubmittedQuery(query);
    setPage(1);
  };

  const displayDuration = (duration) => {
    if (typeof duration === "number") {
      return `${duration} min`;
    }
    return duration || "-";
  };

  const displayLastUsed = (value) => {
    if (!value) {
      return "N/A";
    }
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) {
      return value;
    }
    return date.toLocaleString();
  };

  const displayStatus = (status) => {
    if (!status || status === "linked") {
      return "";
    }
    return status.replaceAll("_", " ");
  };

  const shouldShowStatus = (status) => Boolean(status && status !== "linked");

  const canSeePassword = (meeting) => {
    if (userRole === "super_admin" || userRole === "admin") {
      return true;
    }

    if (userRole === "agent") {
      const memberMadors = (currentUser?.madors || []).map((mador) =>
        (mador.name || "").toLowerCase().trim()
      );
      const meetingGroup = (meeting.group || "").toLowerCase().trim();
      return memberMadors.includes(meetingGroup);
    }

    return false;
  };

  const getPasswordText = (meeting) => {
    if (!meeting?.password) {
      return "-";
    }
    return canSeePassword(meeting) ? meeting.password : "Restricted";
  };

  const canChangePassword = (meeting) => {
    if (!meeting) {
      return false;
    }

    if (userRole === "super_admin") {
      return true;
    }

    if (userRole === "admin") {
      const memberMadors = (currentUser?.madors || []).map((mador) =>
        (mador.name || "").toLowerCase().trim()
      );
      const meetingGroup = (meeting.group || "").toLowerCase().trim();
      return memberMadors.includes(meetingGroup);
    }

    return false;
  };

  const canDeleteMeeting = (meeting) => {
    if (!meeting) {
      return false;
    }

    if (userRole === "super_admin") {
      return true;
    }

    if (userRole === "admin") {
      if (meeting.mador_owner_id && currentUser?.UUID) {
        return String(meeting.mador_owner_id) === String(currentUser.UUID);
      }

      const ownedMadors = (currentUser?.madors || []).map((mador) =>
        (mador.name || "").toLowerCase().trim()
      );
      const meetingGroup = (meeting.group || "").toLowerCase().trim();
      return ownedMadors.includes(meetingGroup);
    }

    return false;
  };

  const inferMeetingType = () => {
    const lowerTitle = title.toLowerCase();
    if (lowerTitle.includes("audio")) return "audio";
    if (lowerTitle.includes("video")) return "video";
    if (lowerTitle.includes("blast")) return "blast_dial";
    return "audio";
  };

  const handleLocalMeetingChange = (e) => {
    const { name, value } = e.target;
    setNewMeeting((prev) => ({ ...prev, [name]: value }));
  };

  const handleCreateLocalMeeting = (e) => {
    e.preventDefault();
    setCreateError("");
    setCreateSuccess("");

    const meetingIdText = newMeeting.meetingId.trim();
    if (!meetingIdText) {
      setCreateError("Meeting ID is required.");
      return;
    }

    if (!/^\d+$/.test(meetingIdText)) {
      setCreateError("Meeting ID must be numeric.");
      return;
    }

    if (!newMeeting.madorId) {
      setCreateError("Please select a mador.");
      return;
    }

    const chosenMador = availableMadors.find(
      (mador) => String(mador.id || mador.UUID) === String(newMeeting.madorId)
    );

    const createInDb = async () => {
      try {
        setCreateLoading(true);
        const payload = { meeting_id: Number(meetingIdText) };
        const dbResponse = await madorAPI.createMeeting(newMeeting.madorId, payload);
        const saved = dbResponse.data;

        const cmsResponse = await cmsAPI.getMeetingById(meetingIdText);
        const existingCms = cmsResponse.data;

        const local = {
          id: `db-${saved.id}`,
          meetingId: meetingIdText,
          name: existingCms?.name || "Pending CMS fetch",
          type: existingCms?.type || inferMeetingType(),
          group: existingCms?.group || chosenMador?.name || "Unassigned",
          accessLevel: existingCms?.accessLevel || "-",
          status: existingCms?.status || "",
          participantsCount: existingCms?.participantsCount ?? 0,
          duration: existingCms?.duration ?? "-",
          lastUsedAt: existingCms?.lastUsedAt || null,
          password: existingCms?.password || "",
          passwordMasked: existingCms?.passwordMasked || "-",
          cmsNode: existingCms?.cmsNode || "LOCAL",
          isLocal: true,
          mador_id: saved.mador_id,
          mador_owner_id: saved.mador_owner_id,
        };

        setLocalMeetings((prev) => [local, ...prev]);
        setPage(1);
        setNewMeeting({
          meetingId: "",
          madorId: "",
        });
        setCreateSuccess("Meeting added to database successfully.");
      } catch (err) {
        setCreateError(err.response?.data?.detail || "Failed to add meeting to database.");
      } finally {
        setCreateLoading(false);
      }
    };

    createInDb();
  };

  const handleOpenMeeting = async (meeting) => {
    setOpenError("");
    setOpenLoading(true);
    setSelectedMeeting(meeting);

    try {
      const response = await cmsAPI.getMeetingById(meeting.meetingId);
      const cmsMeeting = response.data;

      if (!cmsMeeting) {
        setOpenError("Meeting was not found in CMS.");
        return;
      }

      const merged = {
        ...meeting,
        ...cmsMeeting,
        id: meeting.id,
        isLocal: meeting.isLocal,
      };

      setSelectedMeeting(merged);

      if (meeting.isLocal) {
        setLocalMeetings((prev) => prev.map((item) => (item.id === meeting.id ? merged : item)));
      }
    } catch (err) {
      setOpenError(err.response?.data?.detail || "Failed to fetch meeting from CMS.");
    } finally {
      setOpenLoading(false);
    }
  };

  const handleDeleteLocalMeeting = (meetingId) => {
    setLocalMeetings((prev) => prev.filter((meeting) => meeting.id !== meetingId));

    if (selectedMeeting?.id === meetingId) {
      setSelectedMeeting(null);
    }
  };

  const handleDeleteMeeting = async (meeting) => {
    setDeleteError("");
    setDeleteSuccess("");

    if (!canDeleteMeeting(meeting)) {
      setDeleteError("You are not allowed to delete this meeting.");
      return;
    }

    if (meeting.isLocal) {
      handleDeleteLocalMeeting(meeting.id);
      setDeleteSuccess("Local meeting deleted.");
      return;
    }

    const actor = {
      role: userRole,
      ownedGroups: (currentUser?.madors || []).map((mador) => mador.name),
    };

    try {
      setDeleteLoadingId(meeting.id);
      const response = await cmsAPI.deleteMeeting(meeting.meetingId, actor);
      const result = response.data;

      if (!result?.deleted) {
        setDeleteError("Delete failed. You may not own this meeting.");
        return;
      }

      setDeletedCmsIds((prev) => [...prev, meeting.id]);
      if (selectedMeeting?.id === meeting.id) {
        setSelectedMeeting(null);
      }
      setDeleteSuccess("Meeting deleted successfully.");
    } catch (err) {
      setDeleteError(err.response?.data?.detail || "Failed to delete meeting.");
    } finally {
      setDeleteLoadingId("");
    }
  };

  const handleUpdatePassword = async () => {
    if (!selectedMeeting) {
      return;
    }

    setPasswordError("");
    setPasswordSuccess("");

    if (!canChangePassword(selectedMeeting)) {
      setPasswordError("You are not allowed to change this meeting password.");
      return;
    }

    const trimmed = passwordInput.trim();
    if (!trimmed) {
      setPasswordError("New password is required.");
      return;
    }

    try {
      setPasswordUpdating(true);
      const response = await cmsAPI.updateMeetingPassword(selectedMeeting.meetingId, trimmed);
      const updated = response.data;

      if (!updated) {
        setPasswordError("Meeting was not found in CMS.");
        return;
      }

      setSelectedMeeting((prev) => ({
        ...prev,
        ...updated,
        id: prev.id,
        isLocal: prev.isLocal,
      }));

      if (selectedMeeting.isLocal) {
        setLocalMeetings((prev) =>
          prev.map((item) =>
            item.id === selectedMeeting.id
              ? { ...item, ...updated, id: item.id, isLocal: item.isLocal }
              : item
          )
        );
      }

      setPasswordInput("");
      setPasswordSuccess("Password updated in CMS.");
    } catch (err) {
      setPasswordError(err.response?.data?.detail || "Failed to update password in CMS.");
    } finally {
      setPasswordUpdating(false);
    }
  };

  useEffect(() => {
    setPasswordInput("");
    setPasswordError("");
    setPasswordSuccess("");
  }, [selectedMeeting?.id]);

  useEffect(() => {
    const loadMadors = async () => {
      if (userRole === "super_admin") {
        try {
          const response = await madorAPI.listMadors();
          setAvailableMadors(response.data || []);
        } catch {
          setAvailableMadors([]);
        }
        return;
      }

      setAvailableMadors(currentUser?.madors || []);
    };

    loadMadors();
  }, [userRole, currentUser]);

  return (
    <div className="page">
      <h2 className="page-header">{title}</h2>

      <div className="cards-row">
        <div className="card">
          <h3 className="card-title">Add Meeting To Database</h3>
          <form className="meeting-create-form" onSubmit={handleCreateLocalMeeting}>
            <div className="meeting-form-grid">
              <input
                className="search-input"
                type="text"
                name="meetingId"
                value={newMeeting.meetingId}
                onChange={handleLocalMeetingChange}
                placeholder="Meeting ID"
              />

              <select
                className="search-select"
                name="madorId"
                value={newMeeting.madorId}
                onChange={handleLocalMeetingChange}
              >
                <option value="">Select mador</option>
                {availableMadors.map((mador) => {
                  const madorId = mador.id || mador.UUID;
                  return (
                    <option key={String(madorId)} value={String(madorId)}>
                      {mador.name}
                    </option>
                  );
                })}
              </select>
            </div>

            <button className="search-button" type="submit" disabled={createLoading}>
              {createLoading ? "Adding..." : "Add Meeting"}
            </button>
          </form>

          {createError ? <div className="error-banner">{createError}</div> : null}
          {createSuccess ? <div className="success-banner">{createSuccess}</div> : null}
          {deleteError ? <div className="error-banner">{deleteError}</div> : null}
          {deleteSuccess ? <div className="success-banner">{deleteSuccess}</div> : null}
        </div>

        {/* Search Card */}
        <div className="card">
          <div className="search-row">
            <select
              className="search-select"
              value={searchBy}
              onChange={(e) => setSearchBy(e.target.value)}
            >
              <option value="meetingId">Meeting ID</option>
              <option value="group">Group</option>
              <option value="name">Name</option>
            </select>

            <input
              type="text"
              placeholder={
                searchBy === "meetingId"
                  ? "Search by meeting ID..."
                  : searchBy === "group"
                    ? "Search by group..."
                    : "Search by name..."
              }
              className="search-input"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSearch()}
            />

            <button className="search-button" onClick={handleSearch}>
              Search
            </button>
          </div>
        </div>

        {/* Results Card */}
        <div className="card fill">
          <h3 className="card-title">
            Meetings Found ({filteredMeetings.length})
          </h3>

          <div className="meetings-list">
            {loading ? (
              <div className="empty-state">Loading CMS meetings...</div>
            ) : error ? (
              <div className="error-banner">{error}</div>
            ) : pagedMeetings.length === 0 ? (
              <div className="empty-state">No meetings match your search.</div>
            ) : (
              pagedMeetings.map((m) => (
                <div key={m.id} className="meeting-row">
                  <div>
                    <div className="meeting-title-row">
                      <div className="meeting-title">{m.meetingId}</div>
                      {shouldShowStatus(m.status) ? (
                        <span className={`meeting-status-badge status-${m.status || "unknown"}`}>
                          {displayStatus(m.status)}
                        </span>
                      ) : null}
                    </div>
                    <div className="meeting-name">{m.name || "Unnamed meeting"}</div>
                    <div className="meeting-meta">
                      {m.group} • Participants: {m.participantsCount ?? 0} • Last used: {displayLastUsed(m.lastUsedAt)}
                    </div>
                  </div>
                  <div className="meeting-actions">
                    <button
                      className="btn-secondary"
                      onClick={() => handleOpenMeeting(m)}
                    >
                      Open
                    </button>
                    <button
                      className="btn-danger"
                      onClick={() => handleDeleteMeeting(m)}
                      disabled={!canDeleteMeeting(m) || deleteLoadingId === m.id}
                      title={
                        canDeleteMeeting(m)
                          ? "Delete meeting"
                          : "You are not allowed to delete this meeting"
                      }
                    >
                      {deleteLoadingId === m.id
                        ? "Deleting..."
                        : m.isLocal
                          ? "Delete Local"
                          : "Delete"}
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Pagination */}
          <div className="pagination">
            <button
              className="btn-secondary"
              disabled={page === 1}
              onClick={() => setPage((p) => Math.max(1, p - 1))}
            >
              ◀ Previous
            </button>

            <span className="pagination-info">
              Page {page} of {totalPages}
            </span>

            <button
              className="btn-secondary"
              disabled={page === totalPages}
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            >
              Next ▶
            </button>
          </div>
        </div>
      </div>

      {/* Modal */}
      {selectedMeeting && (
        <div
          className="modal-overlay"
          onClick={() => setSelectedMeeting(null)}
        >
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <h3 className="modal-title">Meeting Details</h3>

            <div className="modal-content">
              {openLoading ? <p>Fetching details from CMS...</p> : null}
              {openError ? <p className="open-error-text">{openError}</p> : null}
              <p><strong>Meeting ID:</strong> {selectedMeeting.meetingId}</p>
              <p><strong>Name:</strong> {selectedMeeting.name || "-"}</p>
              {shouldShowStatus(selectedMeeting.status) ? (
                <p><strong>Status:</strong> {displayStatus(selectedMeeting.status)}</p>
              ) : null}
              <p><strong>Group:</strong> {selectedMeeting.group}</p>
              <p><strong>Access Level:</strong> {selectedMeeting.accessLevel || "-"}</p>
              <p><strong>Participants:</strong> {selectedMeeting.participantsCount ?? 0}</p>
              <p><strong>Last Used:</strong> {displayLastUsed(selectedMeeting.lastUsedAt)}</p>
              <p><strong>Duration:</strong> {displayDuration(selectedMeeting.duration)}</p>
              <p><strong>Password:</strong> {getPasswordText(selectedMeeting)}</p>
              <p><strong>CMS Node:</strong> {selectedMeeting.cmsNode || "-"}</p>

              <div className="password-update-block">
                <p><strong>Update Password (CMS)</strong></p>
                <div className="password-update-row">
                  <input
                    className="search-input"
                    type="text"
                    value={passwordInput}
                    onChange={(e) => setPasswordInput(e.target.value)}
                    placeholder="Enter new password"
                    disabled={!canChangePassword(selectedMeeting) || passwordUpdating}
                  />
                  <button
                    className="search-button"
                    type="button"
                    onClick={handleUpdatePassword}
                    disabled={!canChangePassword(selectedMeeting) || passwordUpdating}
                  >
                    {passwordUpdating ? "Updating..." : "Update"}
                  </button>
                </div>
                {!canChangePassword(selectedMeeting) ? (
                  <p className="open-error-text">You are not allowed to change this password.</p>
                ) : null}
                {passwordError ? <p className="open-error-text">{passwordError}</p> : null}
                {passwordSuccess ? <p className="open-success-text">{passwordSuccess}</p> : null}
              </div>
            </div>

            <div className="modal-actions">
              <button
                className="btn-secondary"
                onClick={() => setSelectedMeeting(null)}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}