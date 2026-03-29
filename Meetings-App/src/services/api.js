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

import axios from 'axios';
import {
  getMockCmsMeetings,
  getMockCmsMeetingById,
  createMockCmsMeeting,
  updateMockCmsMeetingPassword,
  deleteMockCmsMeeting,
} from '../mocks/cmsMeetings';

// כתובת הבסיס של ה-API - מ-environment variable או ברירת מחדל
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor - מוסיף JWT token אוטומטית לכל בקשה יוצאת
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => Promise.reject(error));

// --- Auth API: התחברות ובדיקת חיבור ---
export const authAPI = {
  login: (loginDetails) => api.post('/auth/login', loginDetails),
  protected: () => api.get('/protected/me'),
};

// --- User API: ניהול משתמשים (קריאה, יצירה, מחיקה) ---
export const userAPI = {
  getAllUsers: () => api.get('/users/all'),
  getUserByS_id: (s_id) => api.get(`/users/${s_id}`),
  createAgent: (userData) => api.post('/users/create-agent', userData),
  createViewer: (userData) => api.post('/users/create-viewer', userData),
  createAdmin: (userData) => api.post('/users/create-admin', userData),
  deleteUser: (userId) => api.delete(`/users/${userId}`),
};

// --- Group API: ניהול מדורים, חברים וישיבות ---
export const groupAPI = {
  createGroup: (groupData) => api.post('/groups/create', groupData),
  listGroups: () => api.get('/groups/all'),
  getGroup: (groupId) => api.get(`/groups/${groupId}`),
  deleteGroup: (groupId) => api.delete(`/groups/${groupId}`),
  updateGroup: (groupId, groupData) => api.put(`/groups/${groupId}`, groupData),
  addMember: (groupId, userId, accessLevel) =>
    api.post(`/groups/${groupId}/add-member/${userId}`, null, {
      params: { access_level: accessLevel },
    }),
  removeMember: (groupId, userId) => api.post(`/groups/${groupId}/remove-member/${userId}`),
  addMeeting: (groupId, meetingUuid) => api.post(`/groups/${groupId}/add-meeting/${meetingUuid}`),
};

// --- Meeting API: ניהול ישיבות ב-DB ---
export const meetingAPI = {
  getAllMeetings: () => api.get('/meetings/all'),
  getMeeting: (meetingUuid) => api.get(`/meetings/${meetingUuid}`),
  getMeetingByNumber: (number) => api.get(`/meetings/number/${number}`),
  createMeeting: (meetingData) => api.post('/meetings/create', meetingData),
  deleteMeeting: (meetingUuid) => api.delete(`/meetings/${meetingUuid}`),
  updateMeeting: (meetingUuid, meetingData) => api.put(`/meetings/${meetingUuid}`, meetingData),
  getMeetingsByGroup: (groupUuid) => api.get(`/meetings/group/${groupUuid}`),
};

// --- CMS API: אינטגרציה עם CMS (כרגע mock מקומי, בעתיד יחליף ל-API אמיתי) ---
export const cmsAPI = {
  getMeetings: async (type) => {
    const meetings = await getMockCmsMeetings(type);
    return { data: meetings };
  },
  getMeetingById: async (meetingId) => {
    const meeting = await getMockCmsMeetingById(meetingId);
    return { data: meeting };
  },
  createMeeting: async (meetingData) => {
    const meeting = await createMockCmsMeeting(meetingData);
    return { data: meeting };
  },
  updateMeetingPassword: async (meetingId, newPassword) => {
    const meeting = await updateMockCmsMeetingPassword(meetingId, newPassword);
    return { data: meeting };
  },
  deleteMeeting: async (meetingId, actor) => {
    const result = await deleteMockCmsMeeting(meetingId, actor);
    return { data: result };
  },
};

export default api;

