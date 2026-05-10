<template>
  <main class="settings-page">
    <AppTopbar :user="currentUser" />

    <section class="settings-hero">
      <div>
        <p class="eyebrow">Personal Settings</p>
        <h1>个人设置</h1>
        <p class="muted">管理身份标签、密码和当前账户信息。</p>
      </div>
      <button class="button secondary" type="button" :disabled="submitting" @click="logout">退出登录</button>
    </section>

    <div class="settings-grid">
      <section class="panel">
        <div class="panel-head">
          <div>
            <p class="card-label">Profile</p>
            <h3>个人资料</h3>
          </div>
        </div>
        <form class="form-stack" @submit.prevent="submitProfile">
          <div v-if="profileMessage" class="notice success">{{ profileMessage }}</div>
          <ErrorAlert :message="profileError" title="资料保存失败" @close="profileError = ''" />
          <label class="field">
            <span>姓名</span>
            <input v-model.trim="profileForm.fullName" type="text" autocomplete="name" />
          </label>
          <label class="field">
            <span>身份标签</span>
            <select v-model="profileForm.role">
              <option v-for="role in roleOptions" :key="role" :value="role">{{ role }}</option>
            </select>
          </label>
          <button class="button primary" type="submit" :disabled="submitting">
            {{ submitting ? "保存中..." : "保存资料" }}
          </button>
        </form>
      </section>

      <section class="panel">
        <div class="panel-head">
          <div>
            <p class="card-label">Security</p>
            <h3>修改密码</h3>
          </div>
        </div>
        <form class="form-stack" @submit.prevent="submitPassword">
          <div v-if="passwordMessage" class="notice success">{{ passwordMessage }}</div>
          <ErrorAlert :message="passwordError" title="密码更新失败" @close="passwordError = ''" />
          <label class="field">
            <span>当前密码</span>
            <input v-model="passwordForm.currentPassword" type="password" autocomplete="current-password" />
          </label>
          <label class="field">
            <span>新密码</span>
            <input v-model="passwordForm.newPassword" type="password" autocomplete="new-password" />
          </label>
          <label class="field">
            <span>确认新密码</span>
            <input v-model="passwordForm.confirmPassword" type="password" autocomplete="new-password" />
          </label>
          <button class="button primary" type="submit" :disabled="submitting">
            {{ submitting ? "更新中..." : "更新密码" }}
          </button>
        </form>
      </section>

      <section class="panel account-info-panel">
        <div class="panel-head">
          <div>
            <p class="card-label">Account</p>
            <h3>账户信息</h3>
          </div>
          <RouterLink class="text-button" to="/cases">我的案件</RouterLink>
        </div>
        <dl class="account-info-list">
          <div>
            <dt>邮箱</dt>
            <dd>{{ currentUser?.email || "未知" }}</dd>
          </div>
          <div>
            <dt>注册时间</dt>
            <dd>{{ formatDate(currentUser?.created_at) || "未知" }}</dd>
          </div>
          <div>
            <dt>当前身份</dt>
            <dd>{{ currentUser?.role || "案件申请人" }}</dd>
          </div>
        </dl>
      </section>
    </div>
  </main>
</template>

<script setup>
import { computed, inject, onMounted, reactive, ref } from "vue";
import { RouterLink, useRouter } from "vue-router";

import { ApiError, authApi } from "../api";
import AppTopbar from "../components/AppTopbar.vue";
import ErrorAlert from "../components/ErrorAlert.vue";
import { sessionKey } from "../session";

const router = useRouter();
const session = inject(sessionKey);
const submitting = ref(false);
const profileError = ref("");
const profileMessage = ref("");
const passwordError = ref("");
const passwordMessage = ref("");
const currentUser = computed(() => session?.user.value || null);

const roleOptions = ["案件申请人", "代理律师", "企业 HR", "工会/调解员", "管理员"];
const profileForm = reactive({
  fullName: "",
  role: "案件申请人",
});
const passwordForm = reactive({
  currentPassword: "",
  newPassword: "",
  confirmPassword: "",
});

function syncProfileForm() {
  profileForm.fullName = currentUser.value?.full_name || "";
  profileForm.role = currentUser.value?.role || "案件申请人";
}

function formatDate(value) {
  if (!value) {
    return "";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleString("zh-CN");
}

function validatePassword() {
  if (passwordForm.currentPassword.length < 8) {
    return "当前密码至少需要 8 位。";
  }
  if (
    passwordForm.newPassword.length < 8 ||
    !/[a-z]/.test(passwordForm.newPassword) ||
    !/[A-Z]/.test(passwordForm.newPassword) ||
    !/\d/.test(passwordForm.newPassword)
  ) {
    return "新密码至少 8 位，并同时包含大写字母、小写字母和数字。";
  }
  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    return "两次输入的新密码不一致。";
  }
  return "";
}

async function submitProfile() {
  profileError.value = "";
  profileMessage.value = "";
  if (!profileForm.fullName.trim()) {
    profileError.value = "姓名不能为空。";
    return;
  }

  submitting.value = true;
  try {
    const response = await authApi.updateProfile({
      full_name: profileForm.fullName,
      role: profileForm.role,
    });
    session?.setUser(response.user);
    profileMessage.value = "个人资料已更新。";
  } catch (error) {
    profileError.value = error instanceof ApiError ? error.message : "保存资料失败，请稍后重试。";
  } finally {
    submitting.value = false;
  }
}

async function submitPassword() {
  passwordError.value = validatePassword();
  passwordMessage.value = "";
  if (passwordError.value) {
    return;
  }

  submitting.value = true;
  try {
    const response = await authApi.changePassword({
      current_password: passwordForm.currentPassword,
      new_password: passwordForm.newPassword,
    });
    session?.setUser(response.user);
    passwordForm.currentPassword = "";
    passwordForm.newPassword = "";
    passwordForm.confirmPassword = "";
    passwordMessage.value = "密码已更新。";
  } catch (error) {
    passwordError.value = error instanceof ApiError ? error.message : "更新密码失败，请稍后重试。";
  } finally {
    submitting.value = false;
  }
}

async function logout() {
  submitting.value = true;
  try {
    await authApi.logout();
  } finally {
    session?.clearUser();
    submitting.value = false;
    await router.push("/login");
  }
}

onMounted(async () => {
  await session?.refreshSession();
  syncProfileForm();
});
</script>
