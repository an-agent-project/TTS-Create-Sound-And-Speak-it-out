<template>
  <div class="home-page">
    <section class="hero">
      <div class="hero-visual" aria-hidden="true">
        <div class="studio-light"></div>
        <div class="wave-field">
          <span v-for="bar in 44" :key="bar" :style="{ '--i': bar }"></span>
        </div>
      </div>

      <div class="hero-copy reveal-on-scroll">
        <p class="eyebrow">AI voice studio</p>
        <h1>AI Voice Studio</h1>
        <p class="hero-desc">Text in. Voice out.</p>
        <div class="hero-actions">
          <router-link to="/workspace" class="btn btn-primary btn-lg">
            <Rocket :size="18" /> 开始创作
          </router-link>
          <router-link to="/voices/public" class="btn hero-secondary btn-lg">
            <Drama :size="18" /> 试听音色
          </router-link>
        </div>
      </div>

      <div class="hero-monitor reveal-on-scroll" aria-label="音频生成状态">
        <div class="monitor-top">
          <span>Scene</span>
          <strong>知识讲解</strong>
        </div>
        <div class="monitor-line">
          <span>Voice</span>
          <strong>晓晓 · 温柔</strong>
        </div>
        <div class="monitor-line">
          <span>Emotion</span>
          <strong>calm / strong</strong>
        </div>
        <div class="mini-wave">
          <span v-for="bar in 24" :key="bar" :style="{ '--i': bar }"></span>
        </div>
      </div>
    </section>

    <section class="flow-section reveal-on-scroll">
      <div class="section-heading">
        <p class="eyebrow">Workflow</p>
        <h2>四步成片</h2>
      </div>
      <div class="flow-line">
        <button
          v-for="step in workflow"
          :key="step.title"
          class="flow-step"
          type="button"
        >
          <component :is="step.icon" :size="22" />
          <span>{{ step.title }}</span>
          <small>{{ step.text }}</small>
        </button>
      </div>
    </section>

    <section class="scenes-section reveal-on-scroll">
      <div class="section-heading">
        <p class="eyebrow">Scenes</p>
        <h2>场景即风格</h2>
      </div>
      <div class="scene-showcase">
        <div class="scene-carousel">
          <button class="carousel-nav prev" type="button" aria-label="上一个场景" @click="prevScene">
            <ChevronLeft :size="24" />
          </button>

          <article class="scene-banner" :key="activeScene.id">
            <component :is="activeScene.iconComponent" :size="34" />
            <p class="scene-kicker">{{ activeScene.kicker }}</p>
            <h3>{{ activeScene.name }}</h3>
            <p>{{ activeScene.description }}</p>
            <button class="scene-action" type="button" @click="goToWorkspace(activeScene.id)">使用场景</button>
          </article>

          <button class="carousel-nav next" type="button" aria-label="下一个场景" @click="nextScene">
            <ChevronRight :size="24" />
          </button>

          <div class="carousel-dots" aria-label="场景分页">
            <button
              v-for="(scene, index) in scenes"
              :key="scene.id"
              class="carousel-dot"
              :class="{ active: activeSceneIndex === index }"
              type="button"
              :aria-label="scene.name"
              @click="setActiveScene(index)"
            ></button>
          </div>
        </div>

        <div class="scene-linked-list" aria-label="场景列表">
          <button
            v-for="(scene, index) in scenes"
            :key="scene.id"
            class="scene-list-item"
            :class="{ active: activeSceneIndex === index }"
            type="button"
            :aria-label="scene.name"
            @click="setActiveScene(index)"
          >
            <component :is="scene.iconComponent" :size="21" />
            <span>
              <strong>{{ scene.name }}</strong>
              <small>{{ scene.description }}</small>
            </span>
          </button>
        </div>
      </div>
    </section>

    <section class="voice-section reveal-on-scroll">
      <div class="voice-copy">
        <p class="eyebrow">Voice & Emotion</p>
        <h2>声音有情绪</h2>
        <p>音色、情感、强度，一起调。</p>
        <router-link to="/workspace" class="btn btn-primary">
          <SlidersHorizontal :size="17" /> 调整一次
        </router-link>
      </div>
      <div class="mixer">
        <div v-for="track in emotionTracks" :key="track.label" class="mixer-row">
          <span>{{ track.label }}</span>
          <div class="mixer-track">
            <i :style="{ '--level': track.value + '%', '--pulse': track.pulse + 'px', '--delay': track.delay + 's' }"></i>
          </div>
          <strong>{{ track.value }}%</strong>
        </div>
      </div>
    </section>

    <section class="final-cta reveal-on-scroll">
      <p class="eyebrow">Start</p>
      <h2>从一段文本开始。</h2>
      <router-link to="/workspace" class="btn btn-primary btn-lg">
        <FileText :size="18" /> 进入创作工作台
      </router-link>
    </section>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { useAppStore } from "../stores/app.js";
import {
  BookOpen,
  ChevronLeft,
  ChevronRight,
  Clapperboard,
  Drama,
  FileText,
  Heart,
  Library,
  Mic,
  Rocket,
  SlidersHorizontal,
} from "lucide-vue-next";

const router = useRouter();
const store = useAppStore();
let revealObserver;
let sceneTimer;

const workflow = [
  { title: "文本", text: "粘贴 / 上传", icon: FileText },
  { title: "场景", text: "选择模板", icon: Clapperboard },
  { title: "音色", text: "自动匹配", icon: Drama },
  { title: "作品", text: "生成保存", icon: Rocket },
];

const scenes = [
  {
    id: "podcast",
    name: "播客模式",
    iconComponent: Mic,
    description: "自然对谈",
    kicker: "Podcast",
  },
  {
    id: "lecture",
    name: "知识讲解",
    iconComponent: BookOpen,
    description: "清晰稳重",
    kicker: "Lecture",
  },
  {
    id: "storytelling",
    name: "故事叙述",
    iconComponent: Library,
    description: "节奏叙事",
    kicker: "Story",
  },
  {
    id: "emotional",
    name: "情感朗读",
    iconComponent: Heart,
    description: "柔和表达",
    kicker: "Emotion",
  },
];

const activeSceneIndex = ref(0);
const activeScene = computed(() => scenes[activeSceneIndex.value]);

const emotionTracks = [
  { label: "清晰度", value: 92, pulse: 24, delay: 0 },
  { label: "情感强度", value: 74, pulse: 42, delay: -0.9 },
  { label: "音色表现力", value: 86, pulse: 32, delay: -1.45 },
  { label: "背景融合", value: 58, pulse: 52, delay: -0.45 },
];

function goToWorkspace(sceneId) {
  store.selectedScene = scenes.find((scene) => scene.id === sceneId);
  router.push("/workspace");
}

function setActiveScene(index) {
  activeSceneIndex.value = index;
}

function nextScene() {
  activeSceneIndex.value = (activeSceneIndex.value + 1) % scenes.length;
}

function prevScene() {
  activeSceneIndex.value = (activeSceneIndex.value - 1 + scenes.length) % scenes.length;
}

onMounted(() => {
  revealObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          revealObserver.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.18 },
  );
  document.querySelectorAll(".reveal-on-scroll").forEach((el) => revealObserver.observe(el));

  sceneTimer = window.setInterval(() => {
    nextScene();
  }, 3600);
});

onBeforeUnmount(() => {
  revealObserver?.disconnect();
  window.clearInterval(sceneTimer);
});
</script>

<style scoped>
.home-page {
  width: 100vw;
  margin-left: calc(50% - 50vw);
  padding: 0 max(24px, calc((100vw - 1120px) / 2)) 72px;
  background:
    radial-gradient(circle at 82% 38%, rgba(45, 138, 78, 0.18), transparent 28%),
    linear-gradient(180deg, #071210 0%, #091713 46%, #07120f 100%);
  color: #f7fbf7;
}

.hero {
  position: relative;
  width: 100vw;
  min-height: calc(100svh - 84px);
  margin-left: calc(-1 * max(24px, calc((100vw - 1120px) / 2)));
  padding: 72px max(24px, calc((100vw - 1120px) / 2)) 56px;
  overflow: hidden;
  background:
    linear-gradient(90deg, rgba(6, 18, 17, 0.94) 0%, rgba(7, 23, 20, 0.88) 46%, rgba(10, 40, 31, 0.72) 100%),
    radial-gradient(circle at 74% 26%, rgba(48, 165, 103, 0.5), transparent 32%),
    linear-gradient(135deg, #071210, #15352b);
  color: #f7fbf7;
  display: grid;
  grid-template-columns: minmax(0, 1.05fr) minmax(280px, 0.75fr);
  align-items: center;
  gap: 48px;
}

.hero-visual {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.studio-light {
  position: absolute;
  right: 8%;
  top: 12%;
  width: 34vw;
  aspect-ratio: 1;
  background: radial-gradient(circle, rgba(68, 204, 122, 0.28), transparent 68%);
  filter: blur(12px);
}

.wave-field {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 10%;
  height: 28vh;
  display: flex;
  align-items: end;
  justify-content: center;
  gap: clamp(4px, 0.8vw, 13px);
  opacity: 0.38;
}

.wave-field span,
.mini-wave span {
  width: clamp(3px, 0.42vw, 7px);
  height: calc(22px + (var(--i) % 9) * 13px);
  border-radius: 999px;
  background: linear-gradient(180deg, rgba(231, 255, 238, 0.95), rgba(53, 191, 107, 0.45));
  animation: pulse-wave 2.8s ease-in-out infinite;
  animation-delay: calc(var(--i) * -0.08s);
}

.hero-copy {
  position: relative;
  z-index: 1;
  max-width: 660px;
}

.eyebrow {
  color: #64c987;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  margin-bottom: 12px;
}

.hero h1 {
  font-size: clamp(46px, 8vw, 92px);
  line-height: 1.02;
  font-weight: 900;
  max-width: 760px;
}

.hero-desc {
  margin: 22px 0 32px;
  max-width: 520px;
  color: rgba(247, 251, 247, 0.78);
  font-size: 18px;
  line-height: 1.8;
}

.hero-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.hero-secondary {
  color: #f7fbf7;
  border: 1px solid rgba(247, 251, 247, 0.28);
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(12px);
}

.hero-secondary:hover {
  background: rgba(255, 255, 255, 0.14);
}

.hero-monitor {
  position: relative;
  z-index: 1;
  width: min(100%, 380px);
  justify-self: end;
  padding: 24px;
  border: 1px solid rgba(255, 255, 255, 0.18);
  background: rgba(7, 20, 18, 0.5);
  backdrop-filter: blur(18px);
  border-radius: 8px;
  box-shadow: 0 24px 80px rgba(0, 0, 0, 0.26);
}

.monitor-top,
.monitor-line {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  padding: 13px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.12);
}

.monitor-top span,
.monitor-line span {
  color: rgba(247, 251, 247, 0.54);
  font-size: 13px;
}

.monitor-top strong,
.monitor-line strong {
  color: #fff;
  font-size: 14px;
}

.mini-wave {
  height: 86px;
  display: flex;
  align-items: end;
  gap: 6px;
  padding-top: 22px;
}

.mini-wave span {
  width: 6px;
}

.flow-section,
.scenes-section,
.voice-section,
.final-cta {
  padding: 88px 0 0;
}

.section-heading {
  display: flex;
  justify-content: space-between;
  align-items: end;
  gap: 32px;
  margin-bottom: 28px;
}

.section-heading h2,
.voice-copy h2,
.final-cta h2 {
  font-size: clamp(30px, 4vw, 48px);
  line-height: 1.15;
  max-width: 680px;
  color: #f7fbf7;
}

.flow-line {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  border-top: 1px solid rgba(126, 211, 148, 0.2);
  border-bottom: 1px solid rgba(126, 211, 148, 0.2);
}

.flow-step {
  min-height: 160px;
  padding: 28px 24px;
  text-align: left;
  background: transparent;
  color: #f7fbf7;
  border-right: 1px solid rgba(126, 211, 148, 0.2);
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 10px;
  transition: background var(--transition), transform var(--transition);
}

.flow-step:last-child {
  border-right: 0;
}

.flow-step svg,
.scene-banner svg {
  color: #64c987;
}

.flow-step span {
  font-size: 19px;
  font-weight: 800;
}

.flow-step small {
  color: rgba(247, 251, 247, 0.62);
  font-size: 14px;
  line-height: 1.7;
}

.flow-step:hover {
  background: rgba(100, 201, 135, 0.1);
  transform: translateY(-2px);
}

.scene-showcase {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(280px, 1fr);
  gap: 28px;
  align-items: stretch;
}

.scene-carousel {
  position: relative;
  min-height: 420px;
  border: 1px solid rgba(126, 211, 148, 0.18);
  background:
    radial-gradient(circle at 78% 26%, rgba(100, 201, 135, 0.16), transparent 34%),
    linear-gradient(135deg, rgba(45, 138, 78, 0.12), transparent 50%),
    rgba(7, 20, 18, 0.52);
  overflow: hidden;
}

.scene-banner {
  min-height: 100%;
  padding: 54px 74px 74px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 16px;
  animation: scene-fade 0.42s ease;
}

.scene-kicker {
  color: #64c987;
  font-size: 13px;
  font-weight: 800;
  text-transform: uppercase;
}

.scene-banner h3 {
  font-size: clamp(34px, 4vw, 58px);
  line-height: 1;
}

.scene-banner p:not(.scene-kicker) {
  color: rgba(247, 251, 247, 0.62);
  font-size: 18px;
}

.scene-action {
  width: max-content;
  margin-top: 6px;
  padding: 10px 18px;
  border-radius: var(--radius-sm);
  background: rgba(100, 201, 135, 0.12);
  color: #f7fbf7;
  border: 1px solid rgba(126, 211, 148, 0.18);
  font-weight: 700;
  transition: background var(--transition), transform var(--transition);
}

.scene-action:hover {
  background: rgba(100, 201, 135, 0.22);
  transform: translateY(-1px);
}

.carousel-nav {
  position: absolute;
  top: 50%;
  z-index: 2;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #f7fbf7;
  background: rgba(7, 20, 18, 0.62);
  border: 1px solid rgba(126, 211, 148, 0.2);
  transform: translateY(-50%);
  transition: background var(--transition), transform var(--transition);
}

.carousel-nav:hover {
  background: rgba(100, 201, 135, 0.18);
  transform: translateY(-50%) scale(1.04);
}

.carousel-nav.prev {
  left: 24px;
}

.carousel-nav.next {
  right: 24px;
}

.carousel-dots {
  position: absolute;
  left: 50%;
  bottom: 24px;
  transform: translateX(-50%);
  display: flex;
  gap: 10px;
  z-index: 2;
}

.carousel-dot {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  background: rgba(247, 251, 247, 0.28);
  transition: width var(--transition), background var(--transition);
}

.carousel-dot.active {
  width: 26px;
  border-radius: 999px;
  background: #64c987;
}

.scene-linked-list {
  display: flex;
  flex-direction: column;
  min-height: 420px;
  border: 1px solid rgba(126, 211, 148, 0.18);
  background: rgba(7, 20, 18, 0.42);
}

.scene-list-item {
  flex: 1;
  min-height: 96px;
  padding: 22px 24px;
  display: grid;
  grid-template-columns: 34px minmax(0, 1fr);
  align-items: center;
  gap: 16px;
  text-align: left;
  color: rgba(247, 251, 247, 0.62);
  background: transparent;
  border-bottom: 1px solid rgba(126, 211, 148, 0.16);
  transition: background var(--transition), color var(--transition), transform var(--transition);
}

.scene-list-item:last-child {
  border-bottom: 0;
}

.scene-list-item svg {
  color: #64c987;
}

.scene-list-item span {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 7px;
}

.scene-list-item strong {
  color: #f7fbf7;
  font-size: 19px;
  line-height: 1.25;
}

.scene-list-item small {
  color: currentColor;
  font-size: 14px;
  line-height: 1.45;
}

.scene-list-item:hover {
  background: rgba(100, 201, 135, 0.08);
  color: rgba(247, 251, 247, 0.78);
}

.scene-list-item.active {
  color: rgba(247, 251, 247, 0.86);
  background:
    linear-gradient(90deg, rgba(100, 201, 135, 0.2), rgba(100, 201, 135, 0.06)),
    rgba(100, 201, 135, 0.08);
  box-shadow: inset 4px 0 0 #64c987;
}

.scene-list-item.active strong {
  color: #ffffff;
}

@keyframes scene-fade {
  from {
    opacity: 0;
    transform: translateY(14px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.voice-section {
  display: grid;
  grid-template-columns: minmax(0, 0.9fr) minmax(300px, 1fr);
  gap: 56px;
  align-items: center;
}

.voice-copy p:not(.eyebrow) {
  color: rgba(247, 251, 247, 0.66);
  font-size: 17px;
  line-height: 1.8;
  margin: 18px 0 26px;
  max-width: 520px;
}

.mixer {
  padding: 12px 0;
  border-top: 1px solid rgba(126, 211, 148, 0.2);
  border-bottom: 1px solid rgba(126, 211, 148, 0.2);
}

.mixer-row {
  display: grid;
  grid-template-columns: 96px 1fr 46px;
  align-items: center;
  gap: 18px;
  padding: 18px 0;
  border-bottom: 1px solid rgba(126, 211, 148, 0.16);
}

.mixer-row:last-child {
  border-bottom: 0;
}

.mixer-row span {
  font-weight: 700;
}

.mixer-row strong {
  color: #64c987;
  font-size: 14px;
}

.mixer-track {
  height: 8px;
  background: rgba(247, 251, 247, 0.14);
  border-radius: 999px;
  overflow: hidden;
}

.mixer-track i {
  position: relative;
  display: block;
  height: 100%;
  width: var(--level);
  background: linear-gradient(90deg, #2d8a4e, #7ed394);
  border-radius: inherit;
  overflow: hidden;
  animation: level-wave 4.2s ease-in-out infinite;
  animation-delay: var(--delay);
}


.final-cta {
  text-align: center;
}

.final-cta h2 {
  margin: 0 auto 24px;
}

.reveal-on-scroll {
  opacity: 0;
  transform: translateY(34px);
  transition: opacity 0.7s ease, transform 0.7s ease;
}

.reveal-on-scroll.is-visible {
  opacity: 1;
  transform: translateY(0);
}

@keyframes pulse-wave {
  0%,
  100% {
    transform: scaleY(0.48);
  }
  50% {
    transform: scaleY(1);
  }
}

@keyframes level-wave {
  0%,
  100% {
    width: calc(var(--level) - var(--pulse));
    filter: saturate(1);
  }
  50% {
    width: min(100%, calc(var(--level) + var(--pulse)));
    filter: saturate(1.24) brightness(1.08);
  }
}

@media (prefers-reduced-motion: reduce) {
  .wave-field span,
  .mini-wave span,
  .mixer-track i,
  .reveal-on-scroll {
    animation: none;
    transition: none;
  }
  .reveal-on-scroll {
    opacity: 1;
    transform: none;
  }
}

@media (max-width: 900px) {
  .hero {
    min-height: auto;
    grid-template-columns: 1fr;
    padding-top: 56px;
  }
  .hero-monitor {
    justify-self: start;
  }
  .flow-line,
  .voice-section {
    grid-template-columns: 1fr;
  }
  .flow-step {
    border-right: 0;
    border-bottom: 1px solid var(--border);
  }
  .flow-step:last-child {
    border-bottom: 0;
  }
  .scene-showcase {
    grid-template-columns: 1fr;
  }
  .scene-carousel {
    min-height: 390px;
  }
  .scene-linked-list {
    min-height: auto;
  }
  .scene-list-item {
    min-height: 78px;
  }
  .scene-banner {
    padding: 32px;
    padding-bottom: 72px;
  }
}

@media (max-width: 600px) {
  .hero {
    padding: 44px 18px 48px;
  }
  .hero h1 {
    font-size: 42px;
  }
  .hero-desc {
    font-size: 16px;
  }
  .hero-actions .btn {
    width: 100%;
  }
  .flow-section,
  .scenes-section,
  .voice-section,
  .final-cta {
    padding-top: 64px;
  }
  .mixer-row {
    grid-template-columns: 82px 1fr;
  }
  .mixer-row strong {
    display: none;
  }
}
</style>
