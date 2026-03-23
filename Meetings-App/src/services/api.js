import axios from 'axios';
import {
  getMockCmsMeetings,
  getMockCmsMeetingById,
  createMockCmsMeeting,
  updateMockCmsMeetingPassword,
  deleteMockCmsMeeting,
} from '../mocks/cmsMeetings';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => Promise.reject(error));

// Auth API
export const authAPI = {
  login: (loginDetails) => api.post('/auth/login', loginDetails),
  protected: () => api.get('/protected/me'),
};

// User API
export const userAPI = {
  getAllUsers: () => api.get('/users/all'),
  getUserByS_id: (s_id) => api.get(`/users/${s_id}`),
  createAgent: (userData) => api.post('/users/create-agent', userData),
  createAdmin: (userData) => api.post('/users/create-admin', userData),
  deleteUser: (userId) => api.delete(`/users/${userId}`),
};

// Mador API
export const madorAPI = {
  createMador: (madorData) => api.post('/madors/', madorData),
  listMadors: () => api.get('/madors/'),
  deleteMador: (madorId) => api.delete(`/madors/${madorId}`),
  addMember: (madorId, userId) => api.post(`/madors/${madorId}/members/${userId}`),
  removeMember: (madorId, userId) => api.delete(`/madors/${madorId}/members/${userId}`),
  updateMemberAccessLevel: (madorId, userId, accessLevel) =>
    api.put(`/madors/${madorId}/members/${userId}/access-level`, { access_level: accessLevel }),
  createMeeting: (madorId, meetingData) => api.post(`/madors/${madorId}/meetings`, meetingData),
  getMeetings: (madorId) => api.get(`/madors/${madorId}/meetings`),
  deleteMeetingByDbId: (meetingDbId) => api.delete(`/madors/meetings/${meetingDbId}`),
};

// CMS API (mock for frontend integration)
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
