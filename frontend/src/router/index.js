import { createRouter, createWebHistory } from "vue-router";

import AdminSettingsPage from "../pages/AdminSettingsPage.vue";
import AssistantPage from "../pages/AssistantPage.vue";
import CasesPage from "../pages/CasesPage.vue";
import HomePage from "../pages/HomePage.vue";
import LoginPage from "../pages/LoginPage.vue";
import NotFoundPage from "../pages/NotFoundPage.vue";
import RegisterPage from "../pages/RegisterPage.vue";
import SettingsPage from "../pages/SettingsPage.vue";

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
    component: LoginPage,
    meta: { public: true, guestOnly: true },
  },
  {
    path: "/register",
    name: "register",
    component: RegisterPage,
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
    component: SettingsPage,
    meta: { requiresAuth: true },
  },
  {
    path: "/cases",
    name: "cases",
    component: CasesPage,
    meta: { requiresAuth: true },
  },
  {
    path: "/admin/settings",
    name: "admin-settings",
    component: AdminSettingsPage,
    meta: { requiresAuth: true, requiresAdmin: true },
  },
  {
    path: "/:pathMatch(.*)*",
    name: "not-found",
    component: NotFoundPage,
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
