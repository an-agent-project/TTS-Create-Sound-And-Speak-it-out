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
    let message = `璇锋眰澶辫触锛寋response.status}`;
    try {
      const data = await response.json();
      message = data.detail || message;
    } catch {
      // Keep the generic message when the response is not JSON.
    }
    throw new Error(message);
  }

  if (response.status === 204) {
    return null;
  }
  return response.json();
}

function errorMessage(detail, fallback) {
  if (!detail) return fallback;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    const missingAuth = detail.some((item) => item?.loc?.includes("authorization"));
    if (missingAuth) return "璇峰厛鐧诲綍鍚庡啀鍏嬮殕闊宠壊";
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

export async function fetchVoices() {
  const voices = await request("/voices", { headers: authHeaders() });
  return voices.map((voice) => {
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
  });
}

export function fetchMaterials(category = "") {
  const query = category ? `?category=${encodeURIComponent(category)}` : "";
  return request(`/materials${query}`);
}

export async function uploadMaterial(formData) {
  const response = await fetch(`${API_BASE}/materials`, {
    method: "POST",
    headers: authHeaders(),
    body: formData,
  });
  if (!response.ok) {
    let message = `璇锋眰澶辫触锛寋response.status}`;
    try {
      const data = await response.json();
      message = errorMessage(data.detail, message);
    } catch {
      // Keep the generic message when the response is not JSON.
    }
    throw new Error(message);
  }
  return response.json();
}

export async function createVoiceClone(formData) {
  const response = await fetch(`${API_BASE}/voice-clones`, {
    method: "POST",
    headers: authHeaders(),
    body: formData,
  });
  if (!response.ok) {
    let message = `璇锋眰澶辫触锛寋response.status}`;
    try {
      const data = await response.json();
      message = errorMessage(data.detail, message);
    } catch {
      // Keep the generic message when the response is not JSON.
    }
    throw new Error(message);
  }
  return response.json();
}


export async function createVoiceCloneJob(formData) {
  const response = await fetch(`${API_BASE}/voice-clones/jobs`, {
    method: "POST",
    headers: authHeaders(),
    body: formData,
  });
  if (!response.ok) {
    let message = `璇锋眰澶辫触锛?{response.status}`;
    try {
      const data = await response.json();
      message = errorMessage(data.detail, message);
    } catch {
      // Keep the generic message when the response is not JSON.
    }
    throw new Error(message);
  }
  return response.json();
}

export function createJobEventSource(jobId) {
  const token = getAuthToken();
  const query = token ? `?token=${encodeURIComponent(token)}` : "";
  return new EventSource(`${API_BASE}/jobs/${encodeURIComponent(jobId)}/events${query}`);
}
export function deleteVoiceById(id) {
  return request(`/voices/${id}`, {
    method: "DELETE",
    headers: authHeaders(),
  });
}
export function requestVoicePublish(voiceId) {
  return request(`/voices/${voiceId}/publish-requests`, {
    method: "POST",
    headers: authHeaders(),
  });
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
  return request("/works");
}

export function deleteWorkById(id) {
  return request(`/works/${id}`, {
    method: "DELETE",
  });
}

export async function fetchPublicVoices() {
  const voices = await request("/voices?scope=public", { headers: authHeaders() });
  return voices.map((voice) => {
    const provider =
      voice.providers?.find((item) => item.isActive && item.isDefault) ||
      voice.providers?.find((item) => item.isActive);
    return {
      ...voice,
      name: voice.displayName || voice.name,
      providerVoiceId: provider?.providerVoiceId,
    };
  });
}

export async function fetchPersonalVoices() {
  const voices = await request("/voices?scope=personal", { headers: authHeaders() });
  return voices.map((voice) => {
    const provider =
      voice.providers?.find((item) => item.isActive && item.isDefault) ||
      voice.providers?.find((item) => item.isActive);
    return {
      ...voice,
      name: voice.displayName || voice.name,
      providerVoiceId: provider?.providerVoiceId,
    };
  });
}

export async function cloneVoiceToPersonal(voiceId) {
  return request("/voices/" + voiceId + "/clone", {
    method: "POST",
    headers: authHeaders(),
  });
}

export async function deletePersonalVoice(voiceId) {
  return request("/voices/" + voiceId, {
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
