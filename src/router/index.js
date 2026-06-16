import { createRouter, createWebHistory } from "vue-router";

const routes = [
  {
    path: "/",
    name: "Home",
    component: () => import("../views/HomePage.vue"),
  },
  {
    path: "/workspace",
    name: "Workspace",
    component: () => import("../views/Workspace.vue"),
  },
  {
    path: "/voices",
    name: "VoiceLibrary",
    component: () => import("../views/VoiceLibrary.vue"),
  },
  {
    path: "/my-works",
    name: "MyWorks",
    component: () => import("../views/MyWorks.vue"),
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
