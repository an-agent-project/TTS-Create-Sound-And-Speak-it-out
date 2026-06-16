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
  {
    path: "/profile",
    name: "Profile",
    component: () => import("../views/ProfilePage.vue"),
    meta: { requiresAuth: true },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Navigation guard for auth-required routes
router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth) {
    const isLoggedIn = localStorage.getItem("isLoggedIn") === "true";
    if (!isLoggedIn) {
      next("/");
      return;
    }
  }
  next();
});

export default router;