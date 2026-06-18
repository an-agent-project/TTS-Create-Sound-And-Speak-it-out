import { defineStore } from "pinia";
import { ref } from "vue";

const AUTH_TOKEN_KEY = "auth_token";

export const useAppStore = defineStore("app", () => {
  const works = ref([]);
  const favoriteVoices = ref([]);

  const selectedScene = ref(null);
  const selectedVoice = ref(null);
  const textContent = ref("");
  const currentWork = ref(null);

  const settings = ref({
    speed: 1.0,
    pitch: "normal",
    emotion: "calm",
    bgmType: "none",
    bgmVolume: 30,
  });

  // ── Auth state ───────────────────────────────────────────────────

  const isLoggedIn = ref(false);
  const token = ref("");
  const user = ref({
    id: 0,
    username: "",
    email: "",
    avatar: "",
    phone: "",
    created_at: "",
  });

  /** Persist token to localStorage so it survives page-reloads. */
  function _saveToken(t) {
    token.value = t;
    localStorage.setItem(AUTH_TOKEN_KEY, t);
  }

  /** Build Authorization header if we have a token. */
  function _authHeaders() {
    if (!token.value) return {};
    return { Authorization: `Bearer ${token.value}` };
  }

  // ── Auth actions ─────────────────────────────────────────────────

  async function login(username, password) {
    const resp = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    const data = await resp.json();
    if (!resp.ok) {
      return { success: false, message: data.detail || "登录失败" };
    }
    _saveToken(data.access_token);
    isLoggedIn.value = true;
    user.value = {
      id: data.user.id,
      username: data.user.username,
      email: data.user.email || "",
      avatar: data.user.avatar || "",
      phone: data.user.phone || "",
      created_at: data.user.created_at || "",
    };
    return { success: true };
  }

  async function register(username, password, email) {
    const resp = await fetch("/api/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password, email: email || undefined }),
    });
    const data = await resp.json();
    if (!resp.ok) {
      return { success: false, message: data.detail || "注册失败" };
    }
    _saveToken(data.access_token);
    isLoggedIn.value = true;
    user.value = {
      id: data.user.id,
      username: data.user.username,
      email: data.user.email || "",
      avatar: data.user.avatar || "",
      phone: data.user.phone || "",
      created_at: data.user.created_at || "",
    };
    return { success: true };
  }

  function logout() {
    isLoggedIn.value = false;
    token.value = "";
    user.value = { id: 0, username: "", email: "", avatar: "", phone: "", created_at: "" };
    localStorage.removeItem(AUTH_TOKEN_KEY);
  }

  /** Fetch the latest user profile from the server (used after page reload). */
  async function fetchMe() {
    if (!token.value) return;
    try {
      const resp = await fetch("/api/auth/me", { headers: _authHeaders() });
      if (!resp.ok) {
        // Token expired / invalid — force logout
        logout();
        return;
      }
      const data = await resp.json();
      user.value = {
        id: data.id,
        username: data.username,
        email: data.email || "",
        avatar: data.avatar || "",
        phone: data.phone || "",
        created_at: data.created_at || "",
      };
      isLoggedIn.value = true;
    } catch {
      // Network error — stay logged in with cached state
    }
  }

  /** Generic profile update — sends partial fields to PUT /api/auth/me. */
  async function updateMe(fields) {
    // Optimistically update local state
    for (const key of Object.keys(fields)) {
      if (key in user.value) user.value[key] = fields[key];
    }
    try {
      await fetch("/api/auth/me", {
        method: "PUT",
        headers: { ..._authHeaders(), "Content-Type": "application/json" },
        body: JSON.stringify(fields),
      });
    } catch {
      // Silently fail — local state already updated
    }
  }

  /** Change password via the dedicated backend endpoint. */
  async function changePassword(oldPassword, newPassword) {
    const resp = await fetch("/api/auth/change-password", {
      method: "POST",
      headers: { ..._authHeaders(), "Content-Type": "application/json" },
      body: JSON.stringify({ old_password: oldPassword, new_password: newPassword }),
    });
    if (!resp.ok) {
      const data = await resp.json();
      return { success: false, message: data.detail || "密码修改失败" };
    }
    return { success: true };
  }

  // ── Initialisation ───────────────────────────────────────────────

  const savedToken = localStorage.getItem(AUTH_TOKEN_KEY);
  if (savedToken) {
    token.value = savedToken;
    // Validate against the server (don't block app startup)
    fetchMe();
  }

  // ── Works ────────────────────────────────────────────────────────

  function addWork(work) {
    works.value.unshift({
      id: Date.now().toString(),
      ...work,
      status: "completed",
      createdAt: new Date().toISOString(),
      duration: Math.ceil(work.content.length / 5),
    });
  }

  function deleteWork(id) {
    works.value = works.value.filter((w) => w.id !== id);
  }

  // ── Voice favorites ──────────────────────────────────────────────

  function toggleFavoriteVoice(voiceId) {
    const idx = favoriteVoices.value.indexOf(voiceId);
    if (idx > -1) {
      favoriteVoices.value.splice(idx, 1);
    } else {
      favoriteVoices.value.push(voiceId);
    }
  }

  function isFavorite(voiceId) {
    return favoriteVoices.value.includes(voiceId);
  }

  // ── Workspace helpers ────────────────────────────────────────────

  function resetWorkspace() {
    selectedScene.value = null;
    selectedVoice.value = null;
    textContent.value = "";
    currentWork.value = null;
    settings.value = {
      speed: 1.0,
      pitch: "normal",
      emotion: "calm",
      bgmType: "none",
      bgmVolume: 30,
    };
  }

  return {
    works,
    favoriteVoices,
    selectedScene,
    selectedVoice,
    textContent,
    currentWork,
    settings,
    isLoggedIn,
    token,
    user,
    login,
    register,
    logout,
    fetchMe,
    updateMe,
    changePassword,
    addWork,
    deleteWork,
    toggleFavoriteVoice,
    isFavorite,
    resetWorkspace,
  };
});
