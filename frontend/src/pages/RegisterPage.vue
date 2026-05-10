<template>
  <main class="auth-page">
    <section class="auth-card register-card">
      <RouterLink class="site-brand auth-brand" to="/">
        <span class="site-logo">L</span>
        <span>
          <strong>L-ERAP PRO</strong>
          <small>创建服务端持久化账户</small>
        </span>
      </RouterLink>

      <div class="auth-copy">
        <p class="eyebrow">Create Account</p>
        <h1>注册并进入案件助手</h1>
        <p class="muted">注册成功后系统会自动登录，并把你带到案件助手工作区。</p>
      </div>

      <form class="form-stack" @submit.prevent="submitRegister">
        <ErrorAlert :message="errorMessage" title="注册失败" @close="errorMessage = ''" />

        <label class="field">
          <span>姓名</span>
          <input v-model.trim="form.fullName" type="text" autocomplete="name" placeholder="张三" />
        </label>

        <label class="field">
          <span>邮箱</span>
          <input v-model.trim="form.email" type="email" autocomplete="email" placeholder="name@example.com" />
        </label>

        <label class="field">
          <span>密码</span>
          <input v-model="form.password" type="password" autocomplete="new-password" placeholder="大小写字母 + 数字" />
        </label>

        <div class="password-meter" :data-score="passwordStrength.score">
          <span :style="{ width: passwordStrength.width }"></span>
        </div>
        <p class="password-hint">{{ passwordStrength.label }}</p>

        <label class="field">
          <span>确认密码</span>
          <input v-model="form.confirmPassword" type="password" autocomplete="new-password" placeholder="再次输入密码" />
        </label>

        <button class="button primary full" type="submit" :disabled="submitting">
          {{ submitting ? "创建中..." : "注册并登录" }}
        </button>
      </form>

      <p class="auth-switch">
        已有账户？
        <RouterLink to="/login">返回登录</RouterLink>
      </p>
    </section>
  </main>
</template>

<script setup>
import { computed, inject, reactive, ref } from "vue";
import { RouterLink, useRoute, useRouter } from "vue-router";

import { ApiError, authApi } from "../api";
import ErrorAlert from "../components/ErrorAlert.vue";
import { sessionKey } from "../session";

const route = useRoute();
const router = useRouter();
const session = inject(sessionKey);
const submitting = ref(false);
const errorMessage = ref("");
const form = reactive({
  fullName: "",
  email: "",
  password: "",
  confirmPassword: "",
});

const passwordStrength = computed(() => {
  let score = 0;
  if (form.password.length >= 8) score += 1;
  if (/[a-z]/.test(form.password)) score += 1;
  if (/[A-Z]/.test(form.password)) score += 1;
  if (/\d/.test(form.password)) score += 1;
  if (/[^A-Za-z0-9]/.test(form.password)) score += 1;

  const labels = ["请输入密码", "较弱：至少 8 位", "一般：继续加入大小写", "可用：建议加入特殊字符", "较强", "很强"];
  return {
    score,
    label: labels[score],
    width: `${Math.max(score, 1) * 20}%`,
  };
});

function validateForm() {
  if (!form.fullName.trim()) {
    return "姓名不能为空。";
  }
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(form.email)) {
    return "请输入有效邮箱。";
  }
  if (form.password.length < 8 || !/[a-z]/.test(form.password) || !/[A-Z]/.test(form.password) || !/\d/.test(form.password)) {
    return "密码至少 8 位，并同时包含大写字母、小写字母和数字。";
  }
  if (form.password !== form.confirmPassword) {
    return "两次输入的密码不一致。";
  }
  return "";
}

function resolveRedirect() {
  const redirect = typeof route.query.redirect === "string" ? route.query.redirect : "";
  return redirect.startsWith("/") ? redirect : "/assistant";
}

async function submitRegister() {
  errorMessage.value = validateForm();
  if (errorMessage.value || submitting.value) {
    return;
  }

  submitting.value = true;
  try {
    const response = await authApi.register({
      full_name: form.fullName,
      role: "案件申请人",
      email: form.email,
      password: form.password,
    });
    session?.setUser(response.user);
    await router.push(resolveRedirect());
  } catch (error) {
    errorMessage.value = error instanceof ApiError ? error.message : "注册失败，请稍后重试。";
  } finally {
    submitting.value = false;
  }
}
</script>
