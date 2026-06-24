const API_BASE = import.meta.env.VITE_API_BASE_URL || "/api";

function authHeaders() {
  const token = localStorage.getItem("auth_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function request(path, options = {}) {
  const headers = {
    "Content-Type": "application/json",
    ...(options.auth ? authHeaders() : {}),
    ...(options.headers || {}),
  };
  delete options.auth;

  const response = await fetch(`${API_BASE}${path}`, {
    headers,
    ...options,
  });

  if (!response.ok) {
    let message = `请求失败：${response.status}`;
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

export function fetchScenes() {
  return request("/scenes");
}

export async function fetchVoices() {
  const voices = await request("/voices", { auth: true });
  return voices.map((voice) => {
    const provider =
      voice.providers?.find((item) => item.isActive && item.isDefault) ||
      voice.providers?.find((item) => item.isActive);

    return {
      ...voice,
      dbId: voice.id,
      id: voice.voiceKey || voice.id,
      name: voice.displayName || voice.name,
      providerVoiceId: provider?.providerVoiceId,
    };
  });
}

export function createVoice(payload) {
  return request("/voices", {
    method: "POST",
    auth: true,
    body: JSON.stringify(payload),
  });
}


export function updateVoiceById(id, payload) {
  return request(`/voices/${id}`, {
    method: "PUT",
    auth: true,
    body: JSON.stringify(payload),
  });
}

export function deleteVoiceById(id) {
  return request(`/voices/${id}`, {
    method: "DELETE",
    auth: true,
  });
}

export function fetchMaterialAssets() {
  return request("/material-assets", { auth: true });
}

export function createMaterialAsset(payload) {
  return request("/material-assets", {
    method: "POST",
    auth: true,
    body: JSON.stringify(payload),
  });
}

export function updateMaterialAsset(id, payload) {
  return request(`/material-assets/${id}`, {
    method: "PUT",
    auth: true,
    body: JSON.stringify(payload),
  });
}

export function deleteMaterialAsset(id) {
  return request(`/material-assets/${id}`, {
    method: "DELETE",
    auth: true,
  });
}

export function fetchTrainingJobs() {
  return request("/training-jobs", { auth: true });
}

export function createTrainingJob(payload) {
  return request("/training-jobs", {
    method: "POST",
    auth: true,
    body: JSON.stringify(payload),
  });
}

export function updateTrainingJob(id, payload) {
  return request(`/training-jobs/${id}`, {
    method: "PUT",
    auth: true,
    body: JSON.stringify(payload),
  });
}

export function cancelTrainingJob(id) {
  return request(`/training-jobs/${id}/cancel`, {
    method: "POST",
    auth: true,
  });
}

export function fetchModelArtifacts() {
  return request("/model-artifacts", { auth: true });
}

export function createModelArtifact(payload) {
  return request("/model-artifacts", {
    method: "POST",
    auth: true,
    body: JSON.stringify(payload),
  });
}

export function updateModelArtifact(id, payload) {
  return request(`/model-artifacts/${id}`, {
    method: "PUT",
    auth: true,
    body: JSON.stringify(payload),
  });
}

export function deleteModelArtifact(id) {
  return request(`/model-artifacts/${id}`, {
    method: "DELETE",
    auth: true,
  });
}

export function preprocessText(content) {
  return request("/text/preprocess", {
    method: "POST",
    body: JSON.stringify({ content }),
  });
}

export function generateTts(payload) {
  return request("/tts/generate", {
    method: "POST",
    auth: true,
    body: JSON.stringify(payload),
  });
}


export function createTtsJob(payload) {
  return request("/tts/jobs", {
    method: "POST",
    auth: true,
    body: JSON.stringify(payload),
  });
}

export function fetchTtsJob(jobId) {
  return request(`/tts/jobs/${jobId}`, {
    auth: true,
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
