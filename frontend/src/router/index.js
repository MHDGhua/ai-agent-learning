import { createRouter, createWebHistory } from "vue-router";

import AssistantPage from "../pages/AssistantPage.vue";
import HomePage from "../pages/HomePage.vue";

function createRoutePlaceholder(title) {
  return {
    name: `${title}Placeholder`,
    template: `<main class="route-placeholder"><p class="eyebrow">L-ERAP PRO</p><h1>${title}</h1></main>`,
  };
}

const routes = [
  {
    path: "/",
    name: "home",
    component: HomePage,
    meta: { public: true },
  },
  {
    path: "/login",
    name: "login",
    component: createRoutePlaceholder("登录页"),
    meta: { public: true, guestOnly: true },
  },
  {
    path: "/register",
    name: "register",
    component: createRoutePlaceholder("注册页"),
    meta: { public: true, guestOnly: true },
  },
  {
    path: "/assistant",
    name: "assistant",
    component: AssistantPage,
    meta: { requiresAuth: true },
  },
  {
    path: "/settings",
    name: "settings",
    component: createRoutePlaceholder("个人设置页"),
    meta: { requiresAuth: true },
  },
  {
    path: "/cases",
    name: "cases",
    component: createRoutePlaceholder("我的案件列表"),
    meta: { requiresAuth: true },
  },
  {
    path: "/admin/settings",
    name: "admin-settings",
    component: createRoutePlaceholder("系统设置"),
    meta: { requiresAuth: true, requiresAdmin: true },
  },
  {
    path: "/:pathMatch(.*)*",
    name: "not-found",
    component: createRoutePlaceholder("404 页面"),
    meta: { public: true },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 };
  },
});

export default router;
export { routes };
