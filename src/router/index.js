import { createRouter, createWebHistory } from "vue-router";

const routes = [
  {
    path: "/",
    name: "Home",
    component: () => import("../views/HomePage.vue"),
  },
  {
    path: "/login",
    name: "Login",
    component: () => import("../views/LoginPage.vue"),
    meta: { hideLayout: true },
  },
  {
    path: "/workspace",
    name: "Workspace",
    component: () => import("../views/Workspace.vue"),
  },
  {
    path: "/extract",
    name: "Extraction",
    component: () => import("../views/ExtractionPage.vue"),
  },
  {
    path: "/voices/public",
    name: "PublicVoiceLibrary",
    component: () => import("../views/PublicVoiceLibrary.vue"),
  },
  {
    path: "/voices",
    name: "VoiceLibrary",
    component: () => import("../views/VoiceLibrary.vue"),
  },
  {
    path: "/workshop",
    name: "Workshop",
    component: () => import("../views/WorkshopPage.vue"),
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

  // ── Admin routes ──
  {
    path: "/admin",
    component: () => import("../views/admin/AdminLayout.vue"),
    meta: { requiresAdmin: true, hideLayout: true },
    children: [
      {
        path: "",
        redirect: "/admin/materials",
      },
      {
        path: "materials",
        name: "AdminMaterials",
        component: () => import("../views/admin/MaterialsPage.vue"),
      },
      {
        path: "voices",
        name: "AdminVoices",
        component: () => import("../views/admin/VoicesPage.vue"),
      },
      {
        path: "works",
        name: "AdminWorks",
        component: () => import("../views/admin/WorksPage.vue"),
      },
      {
        path: "reports",
        name: "AdminReports",
        component: () => import("../views/admin/ReportsPage.vue"),
      },
      {
        path: "health",
        name: "AdminHealth",
        component: () => import("../views/admin/HealthPage.vue"),
      },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem("auth_token");
  const sessionUser = sessionStorage.getItem("user");

  // Debug: log auth state
  if (to.meta.requiresAuth || to.meta.requiresAdmin) {
    console.log("[Router] navigating to", to.path, "| token:", !!token, "| sessionUser:", !!sessionUser);
  }

  if (to.meta.requiresAuth) {
    if (!token && !sessionUser) {
      console.log("[Router] NO AUTH -> redirect to /login");
      next("/login");
      return;
    }
  }

  if (to.meta.requiresAdmin) {
    if (!token && !sessionUser) {
      console.log("[Router] NO AUTH (admin) -> redirect to /login");
      next("/login");
      return;
    }
    try {
      const user = JSON.parse(localStorage.getItem("user") || sessionUser || "{}");
      if (user.role !== "admin") {
        next("/");
        return;
      }
    } catch {
      next("/");
      return;
    }
  }

  next();
});

export default router;
