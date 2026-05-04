// ============================================================================
// API Service - שירות API מרכזי
// ============================================================================
// קובץ זה מרכז את כל קריאות ה-API של האפליקציה.
// משתמש ב-Axios עם interceptor שמוסיף את ה-JWT token לכל בקשה.
//
// מודולי API:
//   - authAPI:    התחברות + בדיקת token (login, protected/me)
//   - userAPI:    ניהול משתמשים (CRUD)
//   - groupAPI:   ניהול מדורים, חברים, ישיבות
//   - meetingAPI: ניהול ישיבות ב-DB
//   - cmsAPI:     אינטגרציה עם CMS (כרגע mock מקומי)
//
// כתובת ה-API נלקחת מ-VITE_API_URL או ברירת מחדל localhost:8000
// ============================================================================

import axios from "axios";

// כתובת הבסיס של ה-API - undefined יחזור ל-localhost, מחרוזת ריקה תשתמש ב-same-origin
const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
const CMS_MODE = (import.meta.env.VITE_CMS_MODE || "mock").toLowerCase();
const CMS_URL = import.meta.env.VITE_CMS_URL || "";
const CMS_API_KEY = import.meta.env.VITE_CMS_API_KEY || "";

const api = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true, // מאפשר שליחת cookies (ל-session-based auth אם נדרש בעתיד)
  timeout: 8000, // timeout של 8 שניות — מונע תקיעות כשהבאקנד כבוי
});

const cmsClient = CMS_URL
  ? axios.create({
      baseURL: CMS_URL,
      headers: {
        "Content-Type": "application/json",
        ...(CMS_API_KEY ? { Authorization: `Bearer ${CMS_API_KEY}` } : {}),
      },
      timeout: 8000,
    })
  : null;

const useRemoteCms = CMS_MODE === "remote" && !!cmsClient;

// --- Auth API: התחברות ובדיקת חיבור ---
export const authAPI = {
  login: (loginDetails) => api.post("/auth/login", loginDetails),
  logout: () => api.post("/auth/logout"),
  refresh: () => api.post("/auth/refresh"),
  protected: () => api.get("/protected/me"),
};

// --- User API: ניהול משתמשים (קריאה, יצירה, עריכה, מחיקה) ---
export const userAPI = {
  getAllUsers: () => api.get("/users/all"),
  updateUser: (userUuid, userData) =>
    api.put(`/users/update/${userUuid}`, userData),
  getUserByS_id: (s_id) => api.get(`/users/${s_id}`),
  getUserByUuid: (uuid) => api.get(`/users/uuid/${uuid}`),
  createAgent: (userData) => api.post("/users/create-agent", userData),
  createViewer: (userData) => api.post("/users/create-viewer", userData),
  createAdmin: (userData) => api.post("/users/create-admin", userData),
  deleteUser: (userId) => api.delete(`/users/${userId}`),
};

// --- Group API: ניהול מדורים, חברים וישיבות ---
export const groupAPI = {
  createGroup: (groupData) => api.post("/groups/create", groupData),
  listGroups: () => api.get("/groups/all"),
  getGroup: (groupId) => api.get(`/groups/${groupId}`),
  deleteGroup: (groupId) => api.delete(`/groups/${groupId}`),
  updateGroup: (groupId, groupData) => api.put(`/groups/${groupId}`, groupData),
  getGroupMembers: (groupId) => api.get(`/groups/${groupId}/members`),
  addMember: (groupId, userId, accessLevel) =>
    api.post(`/groups/${groupId}/add-member/${userId}`, null, {
      params: { access_level: accessLevel },
    }),
  removeMember: (groupId, userId) =>
    api.post(`/groups/${groupId}/remove-member/${userId}`),
  removeMemberAccess: (groupId, userId, accessLevel) =>
    api.post(`/groups/${groupId}/remove-member-access/${userId}`, null, {
      params: { access_level: accessLevel },
    }),
  addMeeting: (groupId, meetingUuid) =>
    api.post(`/groups/${groupId}/add-meeting/${meetingUuid}`),
  removeMeeting: (groupId, meetingUuid) =>
    api.post(`/groups/${groupId}/remove-meeting/${meetingUuid}`),
};

// --- Meeting API: ניהול ישיבות ב-DB ---
export const meetingAPI = {
  getAllMeetings: (accessLevel) =>
    api.get("/meetings/all_meetings", {
      params: accessLevel ? { access_level: accessLevel } : {},
    }),
  getMeeting: (meetingUuid) => api.get(`/meetings/${meetingUuid}`),
  getMeetingByNumber: (number) => api.get(`/meetings/number/${number}`),
  createMeeting: (meetingData) =>
    api.post("/meetings/create_meeting", meetingData),
  deleteMeeting: (meetingUuid) => api.delete(`/meetings/${meetingUuid}`),
  updateMeeting: (meetingUuid, meetingData) =>
    api.put(`/meetings/${meetingUuid}`, meetingData),
  updateMeetingByNumber: (number, meetingData) =>
    api.put(`/meetings/number/${number}`, meetingData),
  getMeetingsByGroup: (groupUuid) => api.get(`/meetings/group/${groupUuid}`),
  updateMeetingPassword: (meetingUuid, newPassword) =>
    api.put(`/meetings/password/${meetingUuid}`, { password: newPassword }),
};

export const favoriteAPI = {
  getFavoriteMeetings: () => api.get("/favorites/meetings"),
  addFavoriteMeeting: (meetingUuid) => api.post(`/favorites/meetings/${meetingUuid}`),
  removeFavoriteMeeting: (meetingUuid) => api.delete(`/favorites/meetings/${meetingUuid}`),
};

export const serverAPI = {
  getAllServers: (accessLevel) =>
    api.get("/servers/all", {
      params: accessLevel ? { access_level: accessLevel } : {},
    }),
  createServer: (serverData) => api.post("/servers/", serverData),
  updateServer: (serverUuid, serverData) =>
    api.put(`/servers/${serverUuid}`, serverData),
  deleteServer: (serverUuid) => api.delete(`/servers/${serverUuid}`),
};

// --- CMS API: אינטגרציה עם CMS ---
// מצבים:
//   - mock: משתמש ב-backend mock endpoints (/cms_mock/*)
//   - remote: מתחבר לשרת CMS חיצוני
export const cmsAPI = {
  getMeetings: async (type) => {
    if (useRemoteCms) {
      return cmsClient.get("/meetings", {
        params: type ? { type } : {},
      });
    }
    // מצב mock - משתמש ב-backend mock endpoints
    return api.get("/cms_mock/meetings", {
      params: type ? { type } : {},
    });
  },
  getMeetingById: async (meetingId) => {
    if (useRemoteCms) {
      return cmsClient.get(`/meetings/${meetingId}`);
    }
    // מצב mock - משתמש ב-backend mock endpoints
    return api.get(`/cms_mock/meetings/${meetingId}`);
  },
  createMeeting: async (meetingData) => {
    if (useRemoteCms) {
      return cmsClient.post("/meetings", meetingData);
    }
    // מצב mock - משתמש ב-backend mock endpoints
    return api.post("/cms_mock/meetings", meetingData);
  },
  updateMeetingPassword: async (meetingId, newPassword) => {
    if (useRemoteCms) {
      return cmsClient.put(`/meetings/${meetingId}/password`, {
        password: newPassword,
      });
    }
    // מצב mock - משתמש ב-backend mock endpoints
    return api.put(`/cms_mock/meetings/${meetingId}/password`, {
      password: newPassword,
    });
  },
  deleteMeeting: async (meetingId, actor) => {
    if (useRemoteCms) {
      return cmsClient.delete(`/meetings/${meetingId}`, {
        data: { actor },
      });
    }
    // מצב mock - משתמש ב-backend mock endpoints
    return api.delete(`/cms_mock/meetings/${meetingId}`, {
      data: { actor },
    });
  },
};

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // הגנה: אם אין error.response או error.config, החזר את השגיאה מיד
    if (!error.response || !originalRequest) {
      return Promise.reject(error);
    }

    // אם קיבלנו 401 והבקשה היא לא ל-login ולא ל-refresh (כדי לא לנסות refresh כשאין בכלל session או לולאה אינסופית)
    if (
      error.response.status === 401 &&
      !originalRequest._retry &&
      !originalRequest.url.includes("/auth/login") &&
      !originalRequest.url.includes("/auth/refresh")
    ) {
      originalRequest._retry = true;

      try {
        console.log("Received 401, attempting to refresh token...");
        await authAPI.refresh();

        // אם הצלחנו, מריצים מחדש את הבקשה המקורית (העוגיות החדשות יישלחו אוטומטית)
        return api(originalRequest);
      } catch (refreshError) {
        // כאן אפשר להוסיף לוגיקה שמנקה את ה-State של המשתמש ב-Context
        // אל תבצע redirect אם כבר נמצאים ב-/login
        if (window.location.pathname !== "/login") {
          window.location.href = "/login";
        }
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  },
);

export default api;
