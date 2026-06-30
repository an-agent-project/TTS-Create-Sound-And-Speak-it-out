import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { deleteWorkById, fetchWorks as fetchWorksApi } from "../services/api.js";

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
    pitch: 0,
    emotion: "calm",
    bgmType: "none",
    bgmVolume: 30,
  });

  const isLoggedIn = ref(false);
  const token = ref("");
  const user = ref(emptyUser());

  // ── Admin ──
  const isAdmin = computed(() => user.value.role === "admin");

  function emptyUser() {
    return {
      id: 0,
      username: "",
      email: "",
      avatar: "",
      phone: "",
      role: "user",
      created_at: "",
    };
  }

  function normalizeUser(apiUser) {
    if (!apiUser) return emptyUser();
    return {
      id: apiUser.id || 0,
      username: apiUser.username || "",
      email: apiUser.email || "",
      avatar: apiUser.avatar || "",
      phone: apiUser.phone || "",
      role: apiUser.role || "user",
      created_at: apiUser.created_at || apiUser.createdAt || "",
    };
  }

  function saveToken(nextToken) {
    token.value = nextToken || "";
    if (token.value) {
      localStorage.setItem(AUTH_TOKEN_KEY, token.value);
    } else {
      localStorage.removeItem(AUTH_TOKEN_KEY);
    }
  }

  function authHeaders() {
    if (!token.value) return {};
    return { Authorization: `Bearer ${token.value}` };
  }

  function setAuth(payload) {
    const nextToken = payload?.access_token || payload?.accessToken || "";
    if (nextToken) saveToken(nextToken);
    user.value = normalizeUser(payload?.user || payload);
    isLoggedIn.value = Boolean(user.value.id);
    if (isLoggedIn.value) {
      localStorage.setItem("user", JSON.stringify(user.value));
      sessionStorage.setItem("user", JSON.stringify(user.value));
    }
  }

  function setUser(apiUser) {
    user.value = normalizeUser(apiUser);
    isLoggedIn.value = Boolean(user.value.id);
    if (isLoggedIn.value) {
      localStorage.setItem("user", JSON.stringify(user.value));
    }
  }

  async function login(identifier, password) {
    const value = identifier.trim();
    const body = value.includes("@")
      ? { email: value.toLowerCase(), password }
      : { username: value, password };
    const resp = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const data = await resp.json();
    if (!resp.ok) {
      return { success: false, message: data.detail || "登录失败" };
    }
    setAuth(data);
    return { success: true };
  }

  async function register(username, password, email = "", code = "") {
    const body = {
      username,
      password,
      email: email || undefined,
      code: code || undefined,
    };
    const resp = await fetch("/api/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const data = await resp.json();
    if (!resp.ok) {
      return { success: false, message: data.detail || "注册失败" };
    }
    setAuth(data);
    return { success: true };
  }

  function logout() {
    isLoggedIn.value = false;
    saveToken("");
    user.value = emptyUser();
    localStorage.removeItem("user");
    sessionStorage.removeItem("user");
  }

  async function fetchMe() {
    if (!token.value) return;
    try {
      const resp = await fetch("/api/auth/me", { headers: authHeaders() });
      if (!resp.ok) {
        if (resp.status === 401) { logout(); return; }
        // server error or network issue - keep token, try cache
        const cached = localStorage.getItem("user");
        if (cached) {
          user.value = normalizeUser(JSON.parse(cached));
          isLoggedIn.value = Boolean(user.value.id);
        }
        return;
      }
      setUser(await resp.json());
    } catch {
      // network error - keep token, try cache
      const cached = localStorage.getItem("user");
      if (cached) {
        user.value = normalizeUser(JSON.parse(cached));
        isLoggedIn.value = Boolean(user.value.id);
      }
    }
  }

  async function updateMe(fields) {
    const previousUser = { ...user.value };
    for (const key of Object.keys(fields)) {
      if (key in user.value) user.value[key] = fields[key];
    }
    try {
      const resp = await fetch("/api/auth/me", {
        method: "PUT",
        headers: { ...authHeaders(), "Content-Type": "application/json" },
        body: JSON.stringify(fields),
      });
      if (!resp.ok) {
        let message = "资料保存失败";
        try {
          const data = await resp.json();
          message = data.detail || message;
        } catch {
          // Keep fallback message when the response is not JSON.
        }
        user.value = previousUser;
        localStorage.setItem("user", JSON.stringify(user.value));
        throw new Error(message);
      }
      setUser(await resp.json());
      return { success: true };
    } catch (error) {
      user.value = previousUser;
      localStorage.setItem("user", JSON.stringify(user.value));
      throw error;
    }
  }
  function updatePhone(phone) {
    return updateMe({ phone });
  }

  function updateAvatar(avatar) {
    return updateMe({ avatar });
  }

  async function changePassword(oldPassword, newPassword) {
    const resp = await fetch("/api/auth/change-password", {
      method: "POST",
      headers: { ...authHeaders(), "Content-Type": "application/json" },
      body: JSON.stringify({ old_password: oldPassword, new_password: newPassword }),
    });
    if (!resp.ok) {
      const data = await resp.json();
      return { success: false, message: data.detail || "密码修改失败" };
    }
    return { success: true };
  }

  const savedToken = localStorage.getItem(AUTH_TOKEN_KEY);
  if (savedToken) {
    token.value = savedToken;
    isLoggedIn.value = true;
    // Try to restore user from cache immediately
    const cachedUser = localStorage.getItem("user") || sessionStorage.getItem("user");
    if (cachedUser) {
      try { user.value = normalizeUser(JSON.parse(cachedUser)); } catch {}
    }
    fetchMe();
  }

  async function fetchWorks() {
    works.value = await fetchWorksApi();
  }

  function addWork(work) {
    const existed = works.value.some((item) => item.id === work.id);
    if (!existed) {
      works.value.unshift(work);
    }
  }

  async function deleteWork(id) {
    await deleteWorkById(id);
    works.value = works.value.filter((w) => w.id !== id);
  }

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

  function resetWorkspace() {
    selectedScene.value = null;
    selectedVoice.value = null;
    textContent.value = "";
    currentWork.value = null;
    settings.value = {
      speed: 1.0,
      pitch: 0,
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
    isAdmin,
    authHeaders,
    setAuth,
    setUser,
    login,
    register,
    logout,
    fetchMe,
    updateMe,
    updatePhone,
    updateAvatar,
    changePassword,
    fetchWorks,
    addWork,
    deleteWork,
    toggleFavoriteVoice,
    isFavorite,
    resetWorkspace,
  };
});
