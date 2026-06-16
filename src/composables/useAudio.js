import { ref } from "vue";

export function useAudio() {
  const isPlaying = ref(false);
  const currentTime = ref(0);
  const duration = ref(0);
  const volume = ref(80);
  let audioCtx = null;

  function play(url) {
    isPlaying.value = true;
  }

  function pause() {
    isPlaying.value = false;
  }

  function stop() {
    isPlaying.value = false;
    currentTime.value = 0;
  }

  function seek(time) {
    currentTime.value = time;
  }

  function setVolume(vol) {
    volume.value = vol;
  }

  function formatTime(seconds) {
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    return `${m}:${s.toString().padStart(2, "0")}`;
  }

  return {
    isPlaying,
    currentTime,
    duration,
    volume,
    play,
    pause,
    stop,
    seek,
    setVolume,
    formatTime,
  };
}
