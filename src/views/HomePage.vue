<template>
  <div class="home-page">
    <!-- Hero -->
    <section class="hero">
      <div class="hero-content">
        <h1 class="hero-title">
          <Mic :size="40" class="hero-icon" />
          一键配音，让创作更简单
        </h1>
        <p class="hero-desc">
          面向内容创作者的个性化有声读物智能生成系统 — 选择场景、粘贴文本、一键生成，几分钟获得专业配音效果
        </p>
        <div class="hero-actions">
          <router-link to="/workspace" class="btn btn-primary btn-lg">
            <Rocket :size="18" /> 立即开始创作
          </router-link>
          <router-link to="/voices" class="btn btn-secondary btn-lg">
            <Drama :size="18" /> 浏览音色库
          </router-link>
        </div>
      </div>
      <div class="hero-stats">
        <div class="stat-item">
          <div class="stat-value">20+</div>
          <div class="stat-label">预设音色</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">4</div>
          <div class="stat-label">创作场景</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">1键</div>
          <div class="stat-label">快速生成</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">免费</div>
          <div class="stat-label">零成本使用</div>
        </div>
      </div>
    </section>

    <!-- How It Works -->
    <section class="section">
      <div class="section-title">
        <Sparkles :size="22" class="title-icon" /> 三步完成配音
      </div>
      <div class="steps">
        <div class="step-card">
          <div class="step-number">1</div>
          <div class="step-icon"><Clapperboard :size="40" /></div>
          <h3>选择场景</h3>
          <p>播客、知识讲解、故事叙述、情感朗读… 选择最适合你内容的场景模板</p>
        </div>
        <div class="step-arrow">&rarr;</div>
        <div class="step-card">
          <div class="step-number">2</div>
          <div class="step-icon"><FileText :size="40" /></div>
          <h3>粘贴文本</h3>
          <p>直接输入或上传文本文件，智能分段自动为你处理排版</p>
        </div>
        <div class="step-arrow">&rarr;</div>
        <div class="step-card">
          <div class="step-number">3</div>
          <div class="step-icon"><SlidersHorizontal :size="40" /></div>
          <h3>一键生成</h3>
          <p>选择音色、调整参数，一键生成专业级有声读物，即刻试听导出</p>
        </div>
      </div>
    </section>

    <!-- Scenes -->
    <section class="section">
      <div class="section-title">
        <Clapperboard :size="22" class="title-icon" /> 创作场景
      </div>
      <div class="grid grid-4">
        <SceneCard
          v-for="scene in scenes"
          :key="scene.id"
          :scene="scene"
          @select="goToWorkspace(scene.id)"
        />
      </div>
    </section>

    <!-- Featured Voices -->
    <section class="section">
      <div class="section-title">
        <Drama :size="22" class="title-icon" /> 推荐音色
      </div>
      <div class="grid grid-4">
        <VoiceCard
          v-for="voice in featuredVoices"
          :key="voice.id"
          :voice="voice"
          :is-favorite="store.isFavorite(voice.id)"
          :show-preview="true"
          @toggle-favorite="store.toggleFavoriteVoice(voice.id)"
        />
      </div>
      <div class="section-footer">
        <router-link to="/voices" class="btn btn-secondary">
          查看全部音色 &rarr;
        </router-link>
      </div>
    </section>

    <!-- Case Demos -->
    <section class="section">
      <div class="section-title">
        <Headphones :size="22" class="title-icon" /> 效果案例
      </div>
      <div class="grid grid-3">
        <div v-for="demo in demos" :key="demo.title" class="card demo-card">
          <div class="demo-icon"><component :is="demo.lucideIcon" :size="36" /></div>
          <h3 class="demo-title">{{ demo.title }}</h3>
          <p class="demo-text">{{ demo.text }}</p>
          <div class="demo-tags">
            <span class="tag tag-primary">{{ demo.scene }}</span>
            <span class="tag tag-success">{{ demo.voice }}</span>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { useRouter } from "vue-router";
import { useAppStore } from "../stores/app.js";
import SceneCard from "../components/SceneCard.vue";
import VoiceCard from "../components/VoiceCard.vue";
import {
  Mic, Rocket, Drama, Sparkles, Clapperboard, FileText, SlidersHorizontal,
  Headphones, BookOpen, Library, Heart, Podcast
} from 'lucide-vue-next'

const router = useRouter();
const store = useAppStore();

const scenes = [
  {
    id: "podcast",
    name: "播客模式",
    iconComponent: Mic,
    description: "适合播客节目、脱口秀类内容，语气自然随性",
    color: "#6366f1",
    defaultSpeed: 1.0,
  },
  {
    id: "lecture",
    name: "知识讲解",
    iconComponent: BookOpen,
    description: "适合课程录制、知识分享，语气沉稳专业",
    color: "#10b981",
    defaultSpeed: 0.9,
  },
  {
    id: "storytelling",
    name: "故事叙述",
    iconComponent: Library,
    description: "适合有声小说、儿童故事，情感丰富饱满",
    color: "#f59e0b",
    defaultSpeed: 0.85,
  },
  {
    id: "emotional",
    name: "情感朗读",
    iconComponent: Heart,
    description: "适合散文诗歌、情感表达，语调柔和动人",
    color: "#ef4444",
    defaultSpeed: 0.8,
  },
];

const featuredVoices = [
  {
    id: "zh-CN-XiaoxiaoNeural",
    name: "晓晓",
    gender: "female",
    style: "温柔",
    category: "知识类",
    description: "温柔知性的女声，适合知识讲解、课程录制",
    isRecommended: true,
  },
  {
    id: "zh-CN-YunxiNeural",
    name: "云希",
    gender: "male",
    style: "磁性",
    category: "故事类",
    description: "磁性的男声，适合故事叙述、播客节目",
    isRecommended: true,
  },
  {
    id: "zh-CN-XiaoyiNeural",
    name: "晓伊",
    gender: "female",
    style: "活泼",
    category: "情感类",
    description: "活泼可爱的女声，适合轻松内容、情感表达",
    isRecommended: true,
  },
  {
    id: "zh-CN-YunjianNeural",
    name: "云健",
    gender: "male",
    style: "活力",
    category: "播客类",
    description: "充满活力的男声，适合运动、户外类内容",
    isRecommended: true,
  },
];

const demos = [
  {
    lucideIcon: Podcast,
    title: "播客节目开场",
    text: "大家好，欢迎收听本期节目，今天我们要聊的话题是人工智能如何改变内容创作...",
    scene: "播客模式",
    voice: "云希 · 磁性男声",
  },
  {
    lucideIcon: BookOpen,
    title: "知识课程讲解",
    text: "今天我们学习Python的基础语法，首先了解变量的概念。变量就像是一个容器，用来存储数据...",
    scene: "知识讲解",
    voice: "晓晓 · 温柔女声",
  },
  {
    lucideIcon: Sparkles,
    title: "儿童故事朗读",
    text: "从前有一座山，山里住着一位老爷爷，他每天都会给小动物们讲有趣的故事...",
    scene: "故事叙述",
    voice: "晓伊 · 活泼女声",
  },
];

function goToWorkspace(sceneId) {
  store.selectedScene = scenes.find((s) => s.id === sceneId);
  router.push("/workspace");
}
</script>

<style scoped>
.hero {
  text-align: center;
  padding: 60px 20px 40px;
  background: linear-gradient(135deg, #eef2ff 0%, #faf5ff 100%);
  border-radius: var(--radius);
  margin-top: 24px;
}

.hero-title {
  font-size: 40px;
  font-weight: 800;
  color: var(--text);
  margin-bottom: 16px;
  line-height: 1.3;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.hero-icon {
  color: var(--primary);
  flex-shrink: 0;
}

.hero-desc {
  font-size: 17px;
  color: var(--text-secondary);
  max-width: 680px;
  margin: 0 auto 32px;
  line-height: 1.7;
}

.hero-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
}

.hero-stats {
  display: flex;
  justify-content: center;
  gap: 48px;
  margin-top: 48px;
  padding-top: 32px;
  border-top: 1px solid var(--border);
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 28px;
  font-weight: 800;
  color: var(--primary);
}

.stat-label {
  font-size: 13px;
  color: var(--text-muted);
  margin-top: 4px;
}

/* Section title icon */
.title-icon {
  color: var(--primary);
  flex-shrink: 0;
}

/* Steps */
.steps {
  display: flex;
  align-items: center;
  gap: 8px;
}

.step-card {
  flex: 1;
  text-align: center;
  padding: 28px 20px;
  background: var(--bg-card);
  border-radius: var(--radius);
  border: 1px solid var(--border);
  position: relative;
}

.step-number {
  position: absolute;
  top: -12px;
  left: 50%;
  transform: translateX(-50%);
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--primary);
  color: #fff;
  font-size: 13px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

.step-icon {
  margin: 8px 0 12px;
  color: var(--primary);
  display: flex;
  justify-content: center;
}

.step-card h3 {
  font-size: 17px;
  margin-bottom: 8px;
  color: var(--text);
}

.step-card p {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.6;
}

.step-arrow {
  font-size: 28px;
  color: var(--text-muted);
  flex-shrink: 0;
}

/* Demo cards */
.demo-card {
  cursor: default;
}

.demo-icon {
  margin-bottom: 12px;
  color: var(--primary);
}

.demo-title {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 8px;
}

.demo-text {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.7;
  margin-bottom: 12px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
}

.demo-tags {
  display: flex;
  gap: 6px;
}

.section-footer {
  margin-top: 20px;
  text-align: center;
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 28px;
  }
  .hero-stats {
    gap: 24px;
    flex-wrap: wrap;
  }
  .steps {
    flex-direction: column;
  }
  .step-arrow {
    transform: rotate(90deg);
  }
}
</style>

