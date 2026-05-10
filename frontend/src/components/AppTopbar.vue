<template>
  <header class="app-topbar">
    <RouterLink class="topbar-brand" to="/">
      <span class="site-logo">L</span>
      <span>
        <strong>L-ERAP PRO</strong>
        <small>重庆劳动法专家系统</small>
      </span>
    </RouterLink>

    <button class="topbar-menu-button" type="button" :aria-expanded="menuOpen" @click="menuOpen = !menuOpen">
      菜单
    </button>

    <nav class="topbar-nav" :class="{ open: menuOpen }" aria-label="主导航">
      <RouterLink v-for="item in navItems" :key="item.to" :to="item.to" @click="menuOpen = false">
        {{ item.label }}
      </RouterLink>
      <RouterLink v-if="isAdmin" to="/admin/settings" @click="menuOpen = false">系统设置</RouterLink>
    </nav>

    <div class="topbar-user">
      <button class="avatar-button" type="button" :aria-expanded="dropdownOpen" @click="dropdownOpen = !dropdownOpen">
        <span>{{ avatarText }}</span>
        <strong>{{ currentUser?.full_name || "未登录" }}</strong>
      </button>
      <div v-if="dropdownOpen" class="user-menu" role="menu">
        <RouterLink role="menuitem" to="/settings" @click="closeDropdown">个人设置</RouterLink>
        <RouterLink role="menuitem" to="/cases" @click="closeDropdown">我的案件</RouterLink>
        <button role="menuitem" type="button" :disabled="loggingOut || !currentUser" @click="logout">
          {{ loggingOut ? "退出中..." : "退出登录" }}
        </button>
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed, inject, ref } from "vue";
import { RouterLink, useRouter } from "vue-router";

import { authApi } from "../api";
import { sessionKey } from "../session";

const props = defineProps({
  user: { type: Object, default: null },
});

const router = useRouter();
const session = inject(sessionKey);
const menuOpen = ref(false);
const dropdownOpen = ref(false);
const loggingOut = ref(false);

const navItems = [
  { label: "首页", to: "/" },
  { label: "案件助手", to: "/assistant" },
  { label: "我的案件", to: "/cases" },
  { label: "个人设置", to: "/settings" },
];

const currentUser = computed(() => props.user || session?.user.value || null);
const avatarText = computed(() => currentUser.value?.full_name?.trim()?.slice(0, 1) || "L");
const isAdmin = computed(() => {
  const role = String(currentUser.value?.role || "").toLowerCase();
  return Boolean(currentUser.value?.is_admin || currentUser.value?.role === "管理员" || role === "admin");
});

function closeDropdown() {
  dropdownOpen.value = false;
  menuOpen.value = false;
}

async function logout() {
  if (!currentUser.value || loggingOut.value) {
    return;
  }
  loggingOut.value = true;
  try {
    await authApi.logout();
  } finally {
    session?.clearUser();
    closeDropdown();
    loggingOut.value = false;
    await router.push("/login");
  }
}
</script>

<style scoped>
.app-topbar {
  position: sticky;
  top: 0;
  z-index: 30;
  display: grid;
  grid-template-columns: minmax(220px, 1fr) auto minmax(160px, auto);
  align-items: center;
  gap: 18px;
  padding: 14px clamp(16px, 4vw, 40px);
  border-bottom: 1px solid rgba(221, 213, 200, 0.78);
  background: rgba(255, 253, 248, 0.86);
  box-shadow: 0 12px 34px rgba(31, 36, 51, 0.06);
  backdrop-filter: blur(18px);
}

.topbar-brand {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  color: var(--ink);
  text-decoration: none;
}

.topbar-brand strong,
.topbar-brand small {
  display: block;
}

.topbar-brand strong {
  font-family: var(--font-display);
}

.topbar-brand small {
  color: var(--muted);
  font-size: 12px;
}

.topbar-nav {
  display: inline-flex;
  justify-content: center;
  gap: 8px;
}

.topbar-nav a,
.user-menu a,
.user-menu button,
.topbar-menu-button,
.avatar-button {
  border: 0;
  color: var(--ink);
  background: transparent;
  text-decoration: none;
  font-weight: 850;
}

.topbar-nav a {
  min-height: 38px;
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  padding: 0 13px;
}

.topbar-nav a.router-link-active,
.topbar-nav a:hover {
  color: var(--brand);
  background: var(--brand-soft);
}

.topbar-menu-button {
  display: none;
  min-height: 38px;
  border: 1px solid var(--line);
  border-radius: 999px;
  padding: 0 14px;
  background: var(--surface);
}

.topbar-user {
  position: relative;
  justify-self: end;
}

.avatar-button {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  min-height: 42px;
  border: 1px solid var(--line);
  border-radius: 999px;
  padding: 4px 12px 4px 4px;
  background: var(--surface);
}

.avatar-button span {
  width: 32px;
  height: 32px;
  display: grid;
  place-items: center;
  border-radius: 999px;
  color: #ffffff;
  background: linear-gradient(135deg, var(--brand), var(--brand-2));
}

.user-menu {
  position: absolute;
  top: calc(100% + 10px);
  right: 0;
  min-width: 180px;
  display: grid;
  gap: 6px;
  padding: 8px;
  border: 1px solid var(--line);
  border-radius: 14px;
  background: var(--surface);
  box-shadow: var(--shadow-strong);
}

.user-menu a,
.user-menu button {
  min-height: 38px;
  display: flex;
  align-items: center;
  border-radius: 10px;
  padding: 0 12px;
  text-align: left;
}

.user-menu a:hover,
.user-menu button:hover:not(:disabled) {
  color: var(--brand);
  background: var(--brand-soft);
}

@media (max-width: 820px) {
  .app-topbar {
    grid-template-columns: 1fr auto;
  }

  .topbar-menu-button {
    display: inline-flex;
    align-items: center;
    justify-content: center;
  }

  .topbar-nav {
    grid-column: 1 / -1;
    display: none;
    grid-template-columns: 1fr;
    justify-content: stretch;
  }

  .topbar-nav.open {
    display: grid;
  }

  .topbar-nav a {
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.72);
  }

  .topbar-user {
    justify-self: stretch;
  }

  .avatar-button {
    width: 100%;
    justify-content: flex-start;
  }
}
</style>
