<template>
  <main class="auth-page">
    <section class="auth-card">
      <RouterLink class="site-brand auth-brand" to="/">
        <span class="site-logo">L</span>
        <span>
          <strong>L-ERAP PRO</strong>
          <small>登录后继续保存和恢复案件</small>
        </span>
      </RouterLink>

      <div class="auth-copy">
        <p class="eyebrow">Account Login</p>
        <h1>进入案件助手工作区</h1>
        <p class="muted">使用真实账户登录后，案件、文书和活动记录会保存到服务端。</p>
      </div>

      <form class="form-stack" @submit.prevent="submitLogin">
        <ErrorAlert :message="errorMessage" title="登录失败" @close="errorMessage = ''" />

        <label class="field">
          <span>邮箱</span>
          <input v-model.trim="form.email" type="email" autocomplete="email" placeholder="name@example.com" />
        </label>

        <label class="field">
          <span>密码</span>
          <input v-model="form.password" type="password" autocomplete="current-password" placeholder="请输入密码" />
        </label>

        <div class="auth-options">
          <label class="check-row">
            <input v-model="form.rememberMe" type="checkbox" />
            <span>记住我</span>
          </label>
          <button class="text-button" type="button" @click="showForgotPassword">忘记密码？</button>
        </div>

        <button class="button primary full" type="submit" :disabled="submitting">
          {{ submitting ? "登录中..." : "登录" }}
        </button>
      </form>

      <p class="auth-switch">
        还没有账户？
        <RouterLink to="/register">创建新账户</RouterLink>
      </p>
    </section>
  </main>
</template>

<script setup>
import { inject, onMounted, reactive, ref } from "vue";
import { RouterLink, useRoute, useRouter } from "vue-router";

import { ApiError, authApi } from "../api";
import ErrorAlert from "../components/ErrorAlert.vue";
import { sessionKey } from "../session";

const REMEMBER_EMAIL_KEY = "lerap_remember_email";

const route = useRoute();
const router = useRouter();
const session = inject(sessionKey);
const submitting = ref(false);
const errorMessage = ref("");
const form = reactive({
  email: "",
  password: "",
  rememberMe: true,
});

function validateForm() {
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(form.email)) {
    return "请输入有效邮箱。";
  }
  if (!form.password) {
    return "请输入密码。";
  }
  return "";
}

function resolveRedirect() {
  const redirect = typeof route.query.redirect === "string" ? route.query.redirect : "";
  return redirect.startsWith("/") ? redirect : "/assistant";
}

function persistRememberedEmail() {
  if (form.rememberMe) {
    window.localStorage.setItem(REMEMBER_EMAIL_KEY, form.email);
    return;
  }
  window.localStorage.removeItem(REMEMBER_EMAIL_KEY);
}

async function submitLogin() {
  errorMessage.value = validateForm();
  if (errorMessage.value || submitting.value) {
    return;
  }

  submitting.value = true;
  try {
    const response = await authApi.login({
      email: form.email,
      password: form.password,
    });
    persistRememberedEmail();
    session?.setUser(response.user);
    await router.push(resolveRedirect());
  } catch (error) {
    errorMessage.value = error instanceof ApiError ? error.message : "登录失败，请稍后重试。";
  } finally {
    submitting.value = false;
  }
}

function showForgotPassword() {
  errorMessage.value = "当前版本暂未开放自助找回密码，请联系系统管理员重置。";
}

onMounted(() => {
  form.email = window.localStorage.getItem(REMEMBER_EMAIL_KEY) || "";
});
</script>
