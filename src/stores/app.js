import { defineStore } from "pinia";
import { ref, computed } from "vue";

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

  // User auth state
  const isLoggedIn = ref(false);
  const user = ref({
    id: "",
    username: "",
    email: "",
    avatar: "",
    phone: "",
    registeredAt: "",
  });

  // ???? API ??????
  function setUser(apiUser) {
    if (!apiUser) return;
    isLoggedIn.value = true;
    user.value = {
      id: String(apiUser.id || ""),
      username: apiUser.username || "",
      email: apiUser.email || "",
      avatar: apiUser.avatar || "",
      phone: apiUser.phone || "",
      registeredAt: apiUser.createdAt || "",
    };
    localStorage.setItem("user", JSON.stringify(user.value));
    localStorage.setItem("isLoggedIn", "true");
  }

  // ???? localStorage ????????
  function login(username, password) {
    const users = JSON.parse(localStorage.getItem("users") || "[]");
    const found = users.find(
      (u) => u.username === username && u.password === password
    );
    if (!found) {
      return { success: false, message: "????????" };
    }
    isLoggedIn.value = true;
    user.value = {
      id: found.id,
      username: found.username,
      email: found.email || "",
      avatar: found.avatar || "",
      phone: found.phone || "",
      registeredAt: found.registeredAt,
    };
    localStorage.setItem("user", JSON.stringify(user.value));
    localStorage.setItem("isLoggedIn", "true");
    return { success: true };
  }

  // ???? localStorage ????????
  function register(username, password) {
    if (!username || !password) {
      return { success: false, message: "??????????" };
    }
    if (password.length < 4) {
      return { success: false, message: "????????4?" };
    }
    const users = JSON.parse(localStorage.getItem("users") || "[]");
    if (users.find((u) => u.username === username)) {
      return { success: false, message: "????????" };
    }
    const newUser = {
      id: Date.now().toString(),
      username,
      email: "",
      password,
      avatar: "",
      phone: "",
      registeredAt: new Date().toISOString(),
    };
    users.push(newUser);
    localStorage.setItem("users", JSON.stringify(users));
    isLoggedIn.value = true;
    user.value = {
      id: newUser.id,
      username: newUser.username,
      email: newUser.email,
      avatar: newUser.avatar,
      phone: newUser.phone,
      registeredAt: newUser.registeredAt,
    };
    localStorage.setItem("user", JSON.stringify(user.value));
    localStorage.setItem("isLoggedIn", "true");
    return { success: true };
  }

  function logout() {
    isLoggedIn.value = false;
    user.value = { id: "", username: "", email: "", avatar: "", phone: "", registeredAt: "" };
    localStorage.removeItem("user");
    localStorage.removeItem("isLoggedIn");
  }

  function updatePhone(phoneNumber) {
    user.value.phone = phoneNumber;
    const users = JSON.parse(localStorage.getItem("users") || "[]");
    const idx = users.findIndex((u) => u.id === user.value.id);
    if (idx > -1) {
      users[idx].phone = phoneNumber;
      localStorage.setItem("users", JSON.stringify(users));
    }
    localStorage.setItem("user", JSON.stringify(user.value));
  }

  function updateAvatar(avatarData) {
    user.value.avatar = avatarData;
    const users = JSON.parse(localStorage.getItem("users") || "[]");
    const idx = users.findIndex((u) => u.id === user.value.id);
    if (idx > -1) {
      users[idx].avatar = avatarData;
      localStorage.setItem("users", JSON.stringify(users));
    }
    localStorage.setItem("user", JSON.stringify(user.value));
  }

  // Init from localStorage
  function initFromStorage() {
    const stored = localStorage.getItem("isLoggedIn");
    if (stored === "true") {
      const userData = JSON.parse(localStorage.getItem("user") || "{}");
      if (userData.id) {
        isLoggedIn.value = true;
        user.value = userData;
      }
    }
  }

  initFromStorage();

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
    user,
    setUser,
    login,
    register,
    logout,
    updatePhone,
    updateAvatar,
    addWork,
    deleteWork,
    toggleFavoriteVoice,
    isFavorite,
    resetWorkspace,
  };
});
