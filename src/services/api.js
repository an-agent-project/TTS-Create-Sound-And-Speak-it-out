const API_BASE = import.meta.env.VITE_API_BASE_URL || "/api";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    let message = `请求失败，{response.status}`;
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
    if (missingAuth) return "请先登录后再克隆音色";
  }
  return detail.message || detail.msg || JSON.stringify(detail);
}

function authHeaders() {
  const token = localStorage.getItem("auth_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
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
      name: voice.displayName || voice.name,
      providerVoiceId: provider?.providerVoiceId,
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
    let message = `请求失败，{response.status}`;
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
    let message = `请求失败，{response.status}`;
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

export function preprocessText(content) {
  return request("/text/preprocess", {
    method: "POST",
    body: JSON.stringify({ content }),
  });
}

export function synthesizeVoicePreview(payload) {
  return request("/tts/preview", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
export function generateTts(payload) {
  return request("/tts/generate", {
    method: "POST",
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
