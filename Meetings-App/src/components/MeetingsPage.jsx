// ============================================================================
// MeetingsPage - ×§×•×ž×¤×•× × ×˜×ª ×”×¦×’×ª ×™×©×™×‘×•×ª ×›×œ×œ×™×ª (Reusable)
// ============================================================================
// ×§×•×ž×¤×•× × ×˜×” ×ž×¨×›×–×™×ª ×©×ž×¦×™×’×” ×¨×©×™×ž×ª ×™×©×™×‘×•×ª. ×ž×©×ž×©×ª ××ª ×›×œ ×“×¤×™ ×”×™×©×™×‘×•×ª
// (Audio, Video, BlastDial) ×¢× title ×•-data ×©×•× ×™×.
//
// ×™×›×•×œ×•×ª:
//   - ×—×™×¤×•×© ×œ×¤×™ Meeting ID / Group / Name
//   - ×¢×™×ž×•×“ (Pagination) ×¢× 5 ×™×©×™×‘×•×ª ×‘×¢×ž×•×“
//   - ×™×¦×™×¨×ª ×™×©×™×‘×” ×—×“×©×” (admin/super_admin ×‘×œ×‘×“)
//   - ×ž×—×™×§×ª ×™×©×™×‘×” ×ž-DB ××• CMS
//   - ×¤×ª×™×—×ª ×ž×•×“××œ ×¢× ×¤×¨×˜×™ ×™×©×™×‘×” ×ž×œ××™× ×ž-CMS
//   - ×¢×“×›×•×Ÿ ×¡×™×¡×ž×” ×©×œ ×™×©×™×‘×” ×‘-CMS
//   - ×”×¢×©×¨×ª × ×ª×•× ×™ ×™×©×™×‘×” ×ž-CMS (×©×, ×¡×™×¡×ž×”, ×ž×©×ª×ª×¤×™×, ×ž×©×š)
//   - ×‘×§×¨×ª ×’×™×©×” ×œ×¤×™ ×ª×¤×§×™×“: admin ×¨×•××” ×”×›×œ, agent ×¨×§ ×œ×¤×™ access_level
//
// Props:
//   - title: ×›×•×ª×¨×ª ×”×“×£ (Audio/Video/BlastDial)
//   - data: ×ž×¢×¨×š ×™×©×™×‘×•×ª ×ž-CMS
//   - loading: ×”×× ×¢×“×™×™×Ÿ ×˜×•×¢×Ÿ
//   - error: ×”×•×“×¢×ª ×©×’×™××”
//
// ×–×¨×™×ž×ª Agent Access:
//   × ×‘×“×§ ×œ×¤×™: ×ž×“×•×¨ ×”×ž×©×ª×ž×© â†’ access_level â†’ ×¡×•×’ ×”×™×©×™×‘×”
//   audio/video/blast_dial â†’ ×¨×•××” ×¨×§ ×™×©×™×‘×•×ª ×ž×”×¡×•×’ ×”×–×”
//   full/standard â†’ ×¨×•××” ×”×›×œ, restricted â†’ ×œ× ×¨×•××” ×›×œ×•×
// ============================================================================

import { useEffect, useMemo, useRef, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { cmsAPI, groupAPI, meetingAPI } from "../services/api";

// ×ž×¡×¤×¨ ×™×©×™×‘×•×ª ×‘×›×œ ×¢×ž×•×“
const PAGE_SIZE = 5;

export default function MeetingsPage({ title, data, loading = false, error = "" }) {
  const { userRole, currentUser } = useAuth();
  const canManageMeetings = userRole === "super_admin"; // ×¨×§ super_admin ×™×›×•×œ ×œ×™×¦×•×¨/×œ×ž×—×•×§
  const [query, setQuery] = useState("");           // ×˜×§×¡×˜ ×—×™×¤×•×© ×©×”×ž×©×ª×ž×© ×ž×§×œ×™×“
  const [submittedQuery, setSubmittedQuery] = useState(""); // ×˜×§×¡×˜ ×—×™×¤×•×© ×©× ×©×œ×— (××—×¨×™ Enter/×œ×—×™×¦×”)
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
  const [deletedDbIds, setDeletedDbIds] = useState([]);
  const [createLoading, setCreateLoading] = useState(false);
  const [availableGroups, setAvailableGroups] = useState([]);
  const [cmsDetailsByMeetingId, setCmsDetailsByMeetingId] = useState({});
  const cmsFetchInFlightRef = useRef(new Set());
  const [newMeeting, setNewMeeting] = useState({
    meetingId: "",
    groupId: "",
  });

  const visibleCmsMeetings = useMemo(
    () => data.filter((item) => !deletedCmsIds.includes(item.id) && !deletedDbIds.includes(item.id)),
    [data, deletedCmsIds, deletedDbIds]
  );

  const allMeetings = useMemo(
    () => [...localMeetings, ...visibleCmsMeetings],
    [localMeetings, visibleCmsMeetings]
  );

  const meetingsWithCmsDetails = useMemo(
    () => allMeetings.map((meeting) => ({
      ...meeting,
      ...(cmsDetailsByMeetingId[String(meeting.meetingId)] || {}),
    })),
    [allMeetings, cmsDetailsByMeetingId]
  );

  // --- ×¤×•× ×§×¦×™×•×ª ×¢×–×¨ ×œ×–×™×”×•×™ ×¡×•×’ ×™×©×™×‘×” ---

  // ×ž×–×”×” ×¡×•×’ ×™×©×™×‘×” ×œ×¤×™ prefix ×©×œ ×ž×¡×¤×¨ (89=audio, 77=video, 55=blast_dial)
  const inferMeetingTypeById = (meetingId) => {
    const text = String(meetingId || "");
    if (text.startsWith("89")) return "audio";
    if (text.startsWith("77")) return "video";
    if (text.startsWith("55")) return "blast_dial";

    const lowerTitle = title.toLowerCase();
    if (lowerTitle.includes("audio")) return "audio";
    if (lowerTitle.includes("video")) return "video";
    if (lowerTitle.includes("blast")) return "blast_dial";
    return "audio";
  };

  // --- ×‘×§×¨×ª ×’×™×©×” ×œ-Agent ---

  // ×ž×—×–×™×¨ ××ª ×›×œ ×¨×ž×•×ª ×”×’×™×©×” ×©×œ ×”-agent ×œ×ž×“×•×¨ ×©×œ ×”×™×©×™×‘×”
  const getAgentAccessLevelsForMeeting = (meeting) => {
    const meetingGroup = (meeting.group || "").toLowerCase().trim();
    const matchingGroup = (currentUser?.groups || []).find(
      (group) => (group.name || "").toLowerCase().trim() === meetingGroup
    );

    if (!matchingGroup || !currentUser?.UUID) {
      return [];
    }

    return (matchingGroup.member_access_levels || [])
      .filter((row) => String(row.user_id) === String(currentUser.UUID))
      .map((row) => String(row.access_level || "").toLowerCase().trim())
      .filter(Boolean);
  };

  // ×‘×•×“×§ ×× ×œ-agent ×™×© ×’×™×©×” ×œ×™×©×™×‘×” ×ž×¡×•×™×ž×ª ×œ×¤×™ access_level
  const canAgentAccessMeeting = (meeting) => {
    const memberGroups = (currentUser?.groups || []).map((group) =>
      (group.name || "").toLowerCase().trim()
    );
    const meetingGroup = (meeting.group || "").toLowerCase().trim();
    if (!memberGroups.includes(meetingGroup)) {
      return false;
    }

    const accessLevels = getAgentAccessLevelsForMeeting(meeting);
    const meetingType = String(meeting.type || inferMeetingTypeById(meeting.meetingId) || "")
      .toLowerCase()
      .trim();

    // Strict permission model: only exact types granted in the group are visible.
    if (!["audio", "video", "blast_dial"].includes(meetingType)) {
      return false;
    }

    return accessLevels.includes(meetingType);
  };

  // --- ×¡×™× ×•×Ÿ ×™×©×™×‘×•×ª ×œ×¤×™ ×”×¨×©××•×ª ---
  // admin/super_admin ×¨×•××™× ×”×›×œ, agent ×¨×•××” ×¨×§ ×ž×” ×©×ž×•×ª×¨ ×œ×•
  const visibleMeetings = useMemo(() => {
    if (userRole === "super_admin" || userRole === "admin") {
      return meetingsWithCmsDetails;
    }

    if (userRole === "agent" || userRole === "viewer") {
      // For member roles, backend endpoints already enforce group membership + access-level rules.
      // Avoid client-side over-filtering based on partial auth payload.
      return meetingsWithCmsDetails;
    }

    return [];
  }, [meetingsWithCmsDetails, userRole]);

  // --- ×—×™×¤×•×© ×œ×¤×™ ×©×“×” ×©× ×‘×—×¨ (meetingId/group/name) ---
  const filteredMeetings = useMemo(() => {
    if (!submittedQuery.trim()) return visibleMeetings;

    const q = submittedQuery.toLowerCase();

    return visibleMeetings.filter((m) => {
      if (searchBy === "meetingId") {
        return String(m.meetingId || "").toLowerCase().includes(q);
      }
      if (searchBy === "group") {
        return String(m.group || "").toLowerCase().includes(q);
      }
      if (searchBy === "name") {
        return (m.name || "").toLowerCase().includes(q);
      }
      return true;
    });
  }, [submittedQuery, searchBy, visibleMeetings]);

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
      return true;
    }

    if (userRole === "viewer") {
      return true;
    }

    return false;
  };

  const canSeeParticipants = (meeting) => {
    return true;
  };

  const getParticipantsText = (meeting) => {
    const count = meeting?.participantsCount ?? 0;
    return canSeeParticipants(meeting) ? count : "Restricted";
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
      return true;
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
      return true;
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

  const mergeMeetingWithCms = (meeting, cmsMeeting) => ({
    ...meeting,
    ...cmsMeeting,
    // DB remains source of truth for password so it is shared between users.
    password: meeting.password || cmsMeeting?.password || "",
    id: meeting.id,
    dbId: meeting.dbId,
    isLocal: meeting.isLocal,
  });

  // --- CMS Integration: ×˜×¢×™× ×ª ×¤×¨×˜×™× × ×•×¡×¤×™× ×ž-CMS ---

  const loadCmsMeetingWithRetry = async (meetingId, options = {}) => {
    const key = String(meetingId || "").trim();
    if (!key) return null;

    const retries = Number(options.retries ?? 0);
    const delayMs = Number(options.delayMs ?? 1200);

    let attempt = 0;
    while (attempt <= retries) {
      try {
        const response = await cmsAPI.getMeetingById(key);
        if (response.data) {
          return response.data;
        }
      } catch {
        // Ignore transient CMS lookup errors and keep retrying.
      }

      if (attempt < retries) {
        await new Promise((resolve) => setTimeout(resolve, delayMs));
      }
      attempt += 1;
    }

    return null;
  };

  const hasCmsDetails = (meeting) => {
    if (!meeting) return false;
    return Boolean(
      meeting.name ||
      meeting.password ||
      meeting.lastUsedAt ||
      typeof meeting.duration === "number" ||
      typeof meeting.participantsCount === "number"
    );
  };

  const enrichMeetingFromCms = async (meeting, options = {}) => {
    const key = String(meeting?.meetingId || "").trim();
    if (!key || cmsFetchInFlightRef.current.has(key)) {
      return;
    }

    cmsFetchInFlightRef.current.add(key);
    try {
      const cmsMeeting = await loadCmsMeetingWithRetry(key, options);
      if (!cmsMeeting) {
        return;
      }

      setCmsDetailsByMeetingId((prev) => ({
        ...prev,
        [key]: cmsMeeting,
      }));

      if (meeting?.isLocal) {
        setLocalMeetings((prev) =>
          prev.map((item) =>
            String(item.meetingId) === key ? mergeMeetingWithCms(item, cmsMeeting) : item
          )
        );
      }
    } finally {
      cmsFetchInFlightRef.current.delete(key);
    }
  };

  const handleLocalMeetingChange = (e) => {
    const { name, value } = e.target;
    setNewMeeting((prev) => ({ ...prev, [name]: value }));
  };

  // --- ×™×¦×™×¨×ª ×™×©×™×‘×” ×—×“×©×” (DB + CMS) ---
  const handleCreateLocalMeeting = (e) => {
    e.preventDefault();
    setCreateError("");
    setCreateSuccess("");

    if (!canManageMeetings) {
      setCreateError("Only super_admin can create meetings.");
      return;
    }

    const meetingIdText = newMeeting.meetingId.trim();
    if (!meetingIdText) {
      setCreateError("Meeting ID is required.");
      return;
    }

    if (!/^\d+$/.test(meetingIdText)) {
      setCreateError("Meeting ID must be numeric.");
      return;
    }

    if (!newMeeting.groupId) {
      setCreateError("Please select a group.");
      return;
    }

    const chosenGroup = availableGroups.find(
      (group) => String(group.id || group.UUID) === String(newMeeting.groupId)
    );

    const createInDb = async () => {
      try {
        setCreateLoading(true);
        const payload = {
          m_number: meetingIdText,
          accessLevel: inferMeetingType(),
        };
        const dbResponse = await meetingAPI.createMeeting(payload);
        const saved = dbResponse.data;
        await groupAPI.addMeeting(newMeeting.groupId, saved.UUID);

        const createdCmsResponse = await cmsAPI.createMeeting({
          meetingId: meetingIdText,
          type: inferMeetingType(),
          group: chosenGroup?.name || "Unassigned",
          name: `Meeting ${meetingIdText}`,
        });
        const createdCms = createdCmsResponse.data;

        const local = {
          id: `db-${saved.UUID}`,
          dbId: saved.UUID,
          meetingId: meetingIdText,
          name: createdCms?.name || `Meeting ${meetingIdText}`,
          type: createdCms?.type || inferMeetingType(),
          group: createdCms?.group || chosenGroup?.name || "Unassigned",
          accessLevel: createdCms?.accessLevel || "-",
          status: createdCms?.status || "",
          participantsCount: createdCms?.participantsCount ?? 0,
          duration: createdCms?.duration ?? "-",
          lastUsedAt: createdCms?.lastUsedAt || null,
          password: createdCms?.password || "",
          passwordMasked: createdCms?.passwordMasked || "-",
          cmsNode: createdCms?.cmsNode || "CMS-LOCAL-1",
          isLocal: true,
        };

        setLocalMeetings((prev) => [local, ...prev]);
        setPage(1);
        setNewMeeting({
          meetingId: "",
          groupId: "",
        });
        setCreateSuccess("Meeting added to database successfully.");

        enrichMeetingFromCms(local, { retries: 1, delayMs: 600 });
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
    setSelectedMeeting(meeting);

    if (hasCmsDetails(meeting)) {
      return;
    }

    setOpenLoading(true);

    try {
      let cmsMeeting = await loadCmsMeetingWithRetry(meeting.meetingId, {
        retries: 1,
        delayMs: 900,
      });

      if (!cmsMeeting) {
        const createdCmsResponse = await cmsAPI.createMeeting({
          meetingId: String(meeting.meetingId || ""),
          type: meeting.type || inferMeetingType(),
          group: meeting.group || "Unassigned",
          name: meeting.name || `Meeting ${meeting.meetingId}`,
        });
        cmsMeeting = createdCmsResponse.data;
      }

      if (!cmsMeeting) {
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

  // --- ×ž×—×™×§×ª ×™×©×™×‘×” (DB ××• CMS) ---
  const handleDeleteMeeting = async (meeting) => {
    setDeleteError("");
    setDeleteSuccess("");

    if (!canDeleteMeeting(meeting)) {
      setDeleteError("You are not allowed to delete this meeting.");
      return;
    }

    if (meeting.dbId || String(meeting.id || "").startsWith("db-")) {
      try {
        setDeleteLoadingId(meeting.id);
        const meetingDbId = String(meeting.dbId || String(meeting.id).replace("db-", ""));
        await meetingAPI.deleteMeeting(meetingDbId);

        handleDeleteLocalMeeting(meeting.id);
        setDeletedDbIds((prev) => [...prev, meeting.id]);
        setDeleteSuccess("Meeting deleted successfully.");
      } catch (err) {
        setDeleteError(err.response?.data?.detail || "Failed to delete meeting from database.");
      } finally {
        setDeleteLoadingId("");
      }
      return;
    }

    if (meeting.isLocal) {
      handleDeleteLocalMeeting(meeting.id);
      setDeleteSuccess("Local meeting deleted.");
      return;
    }

    const actor = {
      role: userRole,
      ownedGroups: (currentUser?.groups || []).map((group) => group.name),
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

  // --- ×¢×“×›×•×Ÿ ×¡×™×¡×ž×ª ×™×©×™×‘×” ×‘-CMS ---
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
      if (!selectedMeeting.dbId) {
        setPasswordError("Meeting is not linked to database.");
        return;
      }

      const response = await meetingAPI.updateMeeting(selectedMeeting.dbId, { password: trimmed });
      const updatedDb = response.data;
      const updated = {
        ...selectedMeeting,
        password: updatedDb?.password || trimmed,
        lastUsedAt: new Date().toISOString(),
      };

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

      // Best effort: keep mock CMS in sync for local UI enrichments.
      try {
        await cmsAPI.updateMeetingPassword(selectedMeeting.meetingId, trimmed);
      } catch {
        // Ignore CMS sync errors when DB update already succeeded.
      }

      setPasswordInput("");
      setPasswordSuccess("Password updated successfully.");
    } catch (err) {
      setPasswordError(err.response?.data?.detail || "Failed to update password.");
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
    const candidates = allMeetings.filter((meeting) => {
      const key = String(meeting.meetingId || "").trim();
      if (!key) return false;

      const hasCachedCms = Boolean(cmsDetailsByMeetingId[key]);
      const hasUsefulDetails = hasCmsDetails(meeting);

      return !hasCachedCms && !hasUsefulDetails;
    });

    candidates.forEach((meeting) => {
      enrichMeetingFromCms(meeting, { retries: 1, delayMs: 900 });
    });
  }, [allMeetings, cmsDetailsByMeetingId]);

  useEffect(() => {
    if (!createError && !createSuccess && !deleteError && !deleteSuccess && !openError && !passwordError && !passwordSuccess) {
      return;
    }

    const timer = setTimeout(() => {
      setCreateError("");
      setCreateSuccess("");
      setDeleteError("");
      setDeleteSuccess("");
      setOpenError("");
      setPasswordError("");
      setPasswordSuccess("");
    }, 3500);

    return () => clearTimeout(timer);
  }, [createError, createSuccess, deleteError, deleteSuccess, openError, passwordError, passwordSuccess]);

  useEffect(() => {
    const loadGroups = async () => {
      if (userRole === "super_admin" || userRole === "admin") {
        try {
          const response = await groupAPI.listGroups();
          setAvailableGroups(response.data || []);
        } catch {
          setAvailableGroups([]);
        }
        return;
      }

      setAvailableGroups(currentUser?.groups || []);
    };

    loadGroups();
  }, [userRole, currentUser]);

  return (
    <div className="page">
      <h2 className="page-header">{title}</h2>

      <div className="cards-row">
        {canManageMeetings ? (
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
                  name="groupId"
                  value={newMeeting.groupId}
                  onChange={handleLocalMeetingChange}
                >
                  <option value="">Select group</option>
                  {availableGroups.map((group) => {
                    const groupId = group.id || group.UUID;
                    return (
                      <option key={String(groupId)} value={String(groupId)}>
                        {group.name}
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
        ) : null}

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
                <div
                  key={m.id}
                  className="meeting-row"
                  onDoubleClick={() => handleOpenMeeting(m)}
                  title="Double-click to open"
                >
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
                      {m.group} â€¢ Participants: {getParticipantsText(m)} â€¢ Last used: {displayLastUsed(m.lastUsedAt)}
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
              â—€ Previous
            </button>

            <span className="pagination-info">
              Page {page} of {totalPages}
            </span>

            <button
              className="btn-secondary"
              disabled={page === totalPages}
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            >
              Next â–¶
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
              <p><strong>Participants:</strong> {getParticipantsText(selectedMeeting)}</p>
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
