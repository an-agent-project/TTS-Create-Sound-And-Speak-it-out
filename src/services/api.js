const API_BASE = import.meta.env.VITE_API_BASE_URL || "/api";

async function request(path, options = {}) {
  const { headers: optionHeaders = {}, ...fetchOptions } = options;
  const response = await fetch(`${API_BASE}${path}`, {
    ...fetchOptions,
    headers: {
      "Content-Type": "application/json",
      ...optionHeaders,
    },
  });

  if (!response.ok) {
    let message = `请求失败，${response.status}`;
    try {
      const data = await response.json();
      message = errorMessage(data.detail || data.message, message);
    } catch {
      // Keep the generic message when the response is not JSON.
    }
    throw new Error(message);
  }

  if (response.status === 204) return null;
  return response.json();
}

function errorMessage(detail, fallback) {
  if (!detail) return fallback;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    const missingAuth = detail.some((item) => item?.loc?.includes("authorization"));
    if (missingAuth) return "请先登录后再继续操作";
  }
  return detail.message || detail.msg || JSON.stringify(detail);
}

function getAuthToken() {
  return localStorage.getItem("auth_token");
}

function authHeaders() {
  const token = getAuthToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function uploadForm(path, formData) {
  const response = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: authHeaders(),
    body: formData,
  });
  if (!response.ok) {
    let message = `请求失败，${response.status}`;
    try {
      const data = await response.json();
      message = errorMessage(data.detail || data.message, message);
    } catch {
      // Keep the generic message when the response is not JSON.
    }
    throw new Error(message);
  }
  return response.json();
}

export function sendAuthCode(email) {
  return request("/auth/send-code", {
    method: "POST",
    body: JSON.stringify({ email }),
  });
}

export function resetPassword(payload) {
  return request("/auth/reset-password", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function fetchScenes() {
  return request("/scenes");
}

function mapVoice(voice) {
  const provider =
    voice.providers?.find((item) => item.isActive && item.isDefault) ||
    voice.providers?.find((item) => item.isActive);
  return {
    ...voice,
    id: voice.voiceKey || voice.id,
    dbId: voice.id,
    name: voice.displayName || voice.name,
    providerVoiceId: provider?.providerVoiceId,
    isSystemVoice: voice.ownerId == null,
  };
}

export async function fetchVoices() {
  return (await request("/voices", { headers: authHeaders() })).map(mapVoice);
}

export async function fetchPublicVoices() {
  return (await request("/voices?scope=public", { headers: authHeaders() })).map(mapVoice);
}

export async function fetchPersonalVoices() {
  return (await request("/voices?scope=personal", { headers: authHeaders() })).map(mapVoice);
}

export function deleteVoiceById(id) {
  return request(`/voices/${id}`, {
    method: "DELETE",
    headers: authHeaders(),
  });
}

export async function cloneVoiceToPersonal(voiceId) {
  return request(`/voices/${voiceId}/clone`, {
    method: "POST",
    headers: authHeaders(),
  });
}

export async function deletePersonalVoice(voiceId) {
  return deleteVoiceById(voiceId);
}

export function requestVoicePublish(voiceId) {
  return request(`/voices/${voiceId}/publish-requests`, {
    method: "POST",
    headers: authHeaders(),
  });
}

export function fetchMaterials(category = "") {
  const query = category ? `?category=${encodeURIComponent(category)}` : "";
  return request(`/materials${query}`, { headers: authHeaders() });
}

export function uploadMaterial(formData) {
  return uploadForm("/materials", formData);
}

export function createVoiceClone(formData) {
  return uploadForm("/voice-clones", formData);
}

export function createVoiceCloneJob(formData) {
  return uploadForm("/voice-clones/jobs", formData);
}

export function createJobEventSource(jobId) {
  const token = getAuthToken();
  const query = token ? `?token=${encodeURIComponent(token)}` : "";
  return new EventSource(`${API_BASE}/jobs/${encodeURIComponent(jobId)}/events${query}`);
}

export function translateText(payload) {
  return request("/text/translate", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function preprocessText(content) {
  return request("/text/preprocess", {
    method: "POST",
    body: JSON.stringify({ content }),
  });
}

export function synthesizeVoicePreview(payload) {
  return request("/tts/preview", {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify(payload),
  });
}

export function generateTts(payload) {
  return request("/tts/generate", {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify(payload),
  });
}

export function startGenerateTtsJob(payload) {
  return request("/tts/generate-jobs", {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify(payload),
  });
}

export function fetchWorks() {
  return request("/works", { headers: authHeaders() });
}

export function deleteWorkById(id) {
  return request(`/works/${id}`, {
    method: "DELETE",
    headers: authHeaders(),
  });
}

export function fetchVoicePublishRequests(status = "pending") {
  const query = status ? `?status=${encodeURIComponent(status)}` : "";
  return request(`/admin/voice-publish-requests${query}`, {
    headers: authHeaders(),
  });
}

export function reviewVoicePublishRequest(requestId, action, note = "") {
  const query = new URLSearchParams({ action });
  if (note) query.set("note", note);
  return request(`/admin/voice-publish-requests/${requestId}/review?${query}`, {
    method: "POST",
    headers: authHeaders(),
  });
}
