import { defineStore } from "pinia";
import { ref } from "vue";
import { deleteWorkById, fetchWorks as fetchWorksApi } from "../services/api.js";

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
    fetchWorks,
    addWork,
    deleteWork,
    toggleFavoriteVoice,
    isFavorite,
    resetWorkspace,
  };
});
