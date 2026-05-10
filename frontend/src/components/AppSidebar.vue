<template>
  <aside class="sidebar">
    <div class="brand-card">
      <div class="brand-mark">L</div>
      <div>
        <p class="eyebrow">L-ERAP PRO</p>
        <h1>重庆劳动仲裁工作台</h1>
        <p class="muted">真实账户、服务端保存、同域 API。</p>
      </div>
    </div>

    <div class="account-card">
      <div class="account-line">
        <div>
          <strong>{{ user ? user.full_name : "访客模式" }}</strong>
          <p class="muted">{{ user ? user.email : "未登录，仅临时查看当前会话" }}</p>
        </div>
        <span class="status-pill" :class="user ? 'good' : 'soft'">
          {{ user ? "已登录" : "未登录" }}
        </span>
      </div>
      <div class="button-row">
        <button class="button primary" @click="$emit('login')">
          {{ user ? "切换账户" : "登录 / 注册" }}
        </button>
        <button class="button secondary" :disabled="!user || loading" @click="$emit('logout')">退出</button>
        <button class="button secondary" :disabled="!user || loading" @click="$emit('profile')">改资料</button>
        <button class="button secondary" :disabled="!user || loading" @click="$emit('password')">改密码</button>
      </div>
    </div>

    <div v-if="hasLegacyData" class="account-card migration-card">
      <div class="section-head">
        <h2>旧版数据迁移</h2>
        <span class="status-pill soft">{{ legacyPreview.history }} / {{ legacyPreview.activities }}</span>
      </div>
      <p class="muted">检测到旧版浏览器记录，可一键导入服务端，避免历史案件和动作丢失。</p>
      <button class="button primary full" :disabled="loading || !user" @click="$emit('import-legacy')">
        导入旧版记录
      </button>
    </div>

    <div class="sidebar-section">
      <div class="section-head">
        <h2>已保存案件</h2>
        <button class="text-button" :disabled="!user || loading" @click="$emit('refresh')">刷新</button>
      </div>
      <button class="button secondary full" :disabled="loading" @click="$emit('new-case')">新建当前会话</button>
      <div v-if="savedCases.length" class="saved-list">
        <article
          v-for="item in savedCases"
          :key="item.id"
          class="saved-card"
          :class="{ active: activeCaseId === item.id }"
        >
          <button class="saved-main" @click="$emit('load-case', item.id)">
            <strong>{{ item.title }}</strong>
            <p>{{ item.case_type || "劳动争议" }}</p>
            <span>{{ formatTime(item.updated_at) }}</span>
          </button>
          <button class="icon-button danger" :disabled="loading" @click="$emit('delete-case', item.id)">删</button>
        </article>
      </div>
      <div v-else class="empty-box">登录后可将会话、文书和分析结果保存到服务端。</div>
    </div>

    <div class="sidebar-section">
      <div class="section-head">
        <h2>最近动作</h2>
      </div>
      <div v-if="activities.length" class="activity-list">
        <article v-for="item in activities" :key="item.id" class="activity-card">
          <strong>{{ item.title }}</strong>
          <p>{{ item.detail }}</p>
          <span>{{ formatTime(item.created_at) }}</span>
        </article>
      </div>
      <div v-else class="empty-box">还没有服务端活动记录。</div>
    </div>
  </aside>
</template>

<script setup>
defineProps({
  user: { type: Object, default: null },
  loading: { type: Boolean, default: false },
  savedCases: { type: Array, default: () => [] },
  activeCaseId: { type: Number, default: null },
  activities: { type: Array, default: () => [] },
  hasLegacyData: { type: Boolean, default: false },
  legacyPreview: { type: Object, default: () => ({ history: 0, activities: 0 }) },
  formatTime: { type: Function, required: true },
});

defineEmits([
  "login",
  "logout",
  "profile",
  "password",
  "refresh",
  "new-case",
  "load-case",
  "delete-case",
  "import-legacy",
]);
</script>
