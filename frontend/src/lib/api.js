const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000';

function authHeaders() {
  const token = localStorage.getItem('mv_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...authHeaders(),
      ...(options.headers || {}),
    },
    ...options,
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || 'Request failed');
  }
  return data;
}

export const api = {
  signup: (payload) => request('/auth/signup', { method: 'POST', body: JSON.stringify(payload) }),
  login: (payload) => request('/auth/login', { method: 'POST', body: JSON.stringify(payload) }),
  ingest: (payload) => request('/memories/ingest', { method: 'POST', body: JSON.stringify(payload) }),
  listMemories: () => request('/memories'),
  getLinks: (id) => request(`/memories/${id}/links`),
  runDecay: () => request('/memories/decay', { method: 'POST' }),
  stats: () => request('/dashboard/stats'),
  timeline: () => request('/dashboard/timeline'),
  ask: (payload) => request('/ask', { method: 'POST', body: JSON.stringify(payload) }),
  reminders: () => request('/memories/reminders/list'),
  decisions: () => request('/memories/decisions'),
};
