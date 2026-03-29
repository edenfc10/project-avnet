// ============================================================================
// App.jsx - קומפוננטת האפליקציה הראשית
// ============================================================================
// מכילה את:
//   - MainLayout: התפריט הראשי (Header + Sidebar + Routes)
//   - Sidebar: ניווט צדדי עם קישורים לכל הדפים
//   - Routes: ניתוב כל הדפים (מוגנים ב-ProtectedRoute)
//
// מבנה הדפים:
//   /login      - דף התחברות (ללא הגנה)
//   /dashboard  - דף ראשי
//   /groups     - ניהול קבוצות
//   /users      - ניהול משתמשים
//   /reports    - דוחות
//   /audio      - ישיבות אודיו
//   /video      - ישיבות וידאו
//   /blastdial  - ישיבות Blastdial
//   /profile, /settings, /help - דפי העדפות
// ============================================================================

import { useEffect, useMemo, useState } from "react";
import { Routes, Route, NavLink, Navigate, useNavigate } from "react-router-dom";
import { useAuth } from "./context/AuthContext";
import { groupAPI } from "./services/api";
import "./App.css";

// Pages
import Groups from "./pages/Groups";
import Users from "./pages/Users";
import Reports from "./pages/Reports";
import AudioMeetings from "./pages/AudioMeetings";
import BlastdialMeetings from "./pages/BlastdialMeetings";
import VideoMeetings from "./pages/VideoMeetings";
import Profile from "./pages/Profile";
import Settings from "./pages/Settings";
import Help from "./pages/Help";
import Login from "./pages/Login";

// Components
import ProtectedRoute from "./components/ProtectedRoute";

// Assets
import Dashboard from "./pages/Dashboard";
import appLogo from "./assets/applogo.svg";
import dashboardIcon from "./assets/icons/dashboard.svg";
import groupsIcon from "./assets/icons/groups.svg";
import reportsIcon from "./assets/icons/reports.svg";
import audioIcon from "./assets/icons/audio-meetings.svg";
import blastdialIcon from "./assets/icons/blastdial-meetings.svg";
import videoIcon from "./assets/icons/video-meetings.svg";
import profileIcon from "./assets/icons/profile.svg";
import settingsIcon from "./assets/icons/settings.svg";
import helpIcon from "./assets/icons/help.svg";

// Main Layout Component
function MainLayout() {
  const navigate = useNavigate();
  const { logout, userRole, currentUser } = useAuth();
  const isAdminOrSuperAdmin = userRole === "admin" || userRole === "super_admin";
  const [memberGroups, setMemberGroups] = useState([]);

  useEffect(() => {
    const loadGroupsForMember = async () => {
      if (!userRole || isAdminOrSuperAdmin) {
        setMemberGroups([]);
        return;
      }

      try {
        const response = await groupAPI.listGroups();
        setMemberGroups(response.data || []);
      } catch {
        setMemberGroups([]);
      }
    };

    loadGroupsForMember();
  }, [userRole, isAdminOrSuperAdmin]);

  const allowedMeetingTypes = useMemo(() => {
    if (isAdminOrSuperAdmin) {
      return new Set(["audio", "video", "blast_dial"]);
    }

    if (userRole === "viewer") {
      return new Set(["audio", "video", "blast_dial"]);
    }

    const currentUserId = String(currentUser?.UUID || "").trim();
    if (!currentUserId) {
      return new Set();
    }

    const allowed = new Set();
    const normalizedCurrentUserId = currentUserId.toLowerCase();
    memberGroups.forEach((group) => {
      (group.member_access_levels || []).forEach((row) => {
        const rowUserId = String(row.user_id || row.userId || "").trim().toLowerCase();
        if (!rowUserId || rowUserId !== normalizedCurrentUserId) {
          return;
        }

        const level = String(row.access_level || "").toLowerCase().trim();
        if (["audio", "video", "blast_dial"].includes(level)) {
          allowed.add(level);
        }
      });
    });

    if (userRole === "viewer") {
      allowed.add("blast_dial");
    }

    return allowed;
  }, [currentUser?.UUID, isAdminOrSuperAdmin, memberGroups, userRole]);

  const defaultRoute = isAdminOrSuperAdmin
    ? "/dashboard"
    : allowedMeetingTypes.has("audio")
      ? "/audio"
      : allowedMeetingTypes.has("blast_dial")
        ? "/blastdial"
        : allowedMeetingTypes.has("video")
          ? "/video"
          : "/groups";

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="app-container">
      {/* Header */}
      <header className="header">
        <div className="header-left">
          <img src={appLogo} alt="App Logo" className="app-logo" />
          <div className="header-title">Meet Manager</div>
        </div>
        <div className="header-actions">
          <div className="header-user-panel" title={`Connected as ${userRole || "unknown"}`}>
            <span className="header-user-name">{currentUser?.username || "User"}</span>
            <span className={`header-role-badge role-${userRole || "agent"}`}>
              {userRole || "unknown"}
            </span>
          </div>
          <button className="profile-button" onClick={handleLogout} title="Sign out">
            Sign out
          </button>
        </div>
      </header>

      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-section">
          <div className="sidebar-section-title">Job Manager</div>
          {isAdminOrSuperAdmin && (
            <NavLink to="/dashboard">
              <img src={dashboardIcon} className="nav-icon" alt="Dashboard" />
              Dashboard
            </NavLink>
          )}
          <NavLink to="/groups">
            <img src={groupsIcon} className="nav-icon" alt="Groups" />
            Groups
          </NavLink>
          <NavLink to="/users">
            <img src={profileIcon} className="nav-icon" alt="Users" />
            Users
          </NavLink>
          {isAdminOrSuperAdmin && (
            <NavLink to="/reports">
              <img src={reportsIcon} className="nav-icon" alt="Reports" />
              Reports
            </NavLink>
          )}
        </div>

        <div className="sidebar-section">
          <div className="sidebar-section-title">Meetings</div>
          {allowedMeetingTypes.has("audio") ? (
            <NavLink to="/audio">
              <img src={audioIcon} className="nav-icon" alt="Audio Meetings" />
              Audio Meetings
            </NavLink>
          ) : null}
          {allowedMeetingTypes.has("blast_dial") ? (
            <NavLink to="/blastdial">
              <img src={blastdialIcon} className="nav-icon" alt="Blastdial Meetings" />
              Blastdial Meetings
            </NavLink>
          ) : null}
          {allowedMeetingTypes.has("video") ? (
            <NavLink to="/video">
              <img src={videoIcon} className="nav-icon" alt="Video Meetings" />
              Video Meetings
            </NavLink>
          ) : null}
        </div>

        <div className="sidebar-section">
          <div className="sidebar-section-title">Preferences</div>
          <NavLink to="/profile">
            <img src={profileIcon} className="nav-icon" alt="Profile" />
            Profile
          </NavLink>
          <NavLink to="/settings">
            <img src={settingsIcon} className="nav-icon" alt="Settings" />
            Settings
          </NavLink>
          <NavLink to="/help">
            <img src={helpIcon} className="nav-icon" alt="Help" />
            Help
          </NavLink>
        </div>
      </aside>

      {/* Main */}
      <main className="main-content">
        <Routes>
          <Route path="/" element={<Navigate to={defaultRoute} replace />} />
          <Route
            path="/dashboard"
            element={isAdminOrSuperAdmin ? <Dashboard /> : <Navigate to={defaultRoute} replace />}
          />
          <Route path="/groups" element={<Groups />} />
          <Route path="/groups" element={<Navigate to="/groups" replace />} />
          <Route path="/users" element={<Users />} />
          <Route
            path="/reports"
            element={isAdminOrSuperAdmin ? <Reports /> : <Navigate to={defaultRoute} replace />}
          />
          <Route path="/audio" element={<AudioMeetings />} />
          <Route path="/blastdial" element={<BlastdialMeetings />} />
          <Route path="/video" element={<VideoMeetings />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/help" element={<Help />} />
        </Routes>
      </main>
    </div>
  );
}

export default function App() {
  const { loading } = useAuth();

  if (loading) {
    return <div className="loading-screen">Loading...</div>;
  }

  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/*"
        element={
          <ProtectedRoute>
            <MainLayout />
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}

