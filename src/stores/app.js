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
    registeredAt: "",
  });

  function login(userData) {
    isLoggedIn.value = true;
    user.value = {
      id: userData.id || Date.now().toString(),
      username: userData.username || "鐢ㄦ埛",
      email: userData.email || "",
      avatar: userData.avatar || "",
      registeredAt: userData.registeredAt || new Date().toISOString(),
    };
    // Persist to localStorage
    localStorage.setItem("user", JSON.stringify(user.value));
    localStorage.setItem("isLoggedIn", "true");
  }

  function register(userData) {
    const newUser = {
      id: Date.now().toString(),
      username: userData.username || "鐢ㄦ埛",
      email: userData.email || "",
      password: userData.password || "",
      avatar: "",
      registeredAt: new Date().toISOString(),
    };
    // Store users in localStorage
    const users = JSON.parse(localStorage.getItem("users") || "[]");
    users.push(newUser);
    localStorage.setItem("users", JSON.stringify(users));

    login(newUser);
  }

  function logout() {
    isLoggedIn.value = false;
    user.value = { id: "", username: "", email: "", avatar: "", registeredAt: "" };
    localStorage.removeItem("user");
    localStorage.removeItem("isLoggedIn");
  }

  function updatePhone(phoneNumber) {
    user.value.phone = phoneNumber;
    // Also update in users list
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

  // Call init
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
    login,
    register,
    logout,
    updatePhone, updateAvatar,
    addWork,
    deleteWork,
    toggleFavoriteVoice,
    isFavorite,
    resetWorkspace,
  };
});