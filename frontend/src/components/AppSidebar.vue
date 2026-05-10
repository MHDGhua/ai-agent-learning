<template>
  <aside class="sidebar">
    <div class="brand-card">
      <div class="brand-mark">L</div>
      <div class="brand-copy">
        <p class="eyebrow">L-ERAP PRO</p>
        <h1>重庆劳动仲裁助手</h1>
        <p class="muted">浅色工作台，围绕历史、助手和文书继续办理。</p>
        <div class="brand-chips" aria-label="工作台语义">
          <span>历史</span>
          <span>助手</span>
          <span>文书</span>
        </div>
      </div>
    </div>

    <nav class="sidebar-nav" aria-label="工作区模块">
      <span>历史回看</span>
      <span class="active">助手中枢</span>
      <span>文书草稿</span>
      <span>案件归档</span>
    </nav>

    <div class="account-card">
      <div class="account-line">
        <div>
          <strong>{{ user ? user.full_name : "本地预览" }}</strong>
          <p class="muted">{{ user ? user.role : "未登录，可先整理案情，后续再保存案件。" }}</p>
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
        <h2>历史资料导入</h2>
        <span class="status-pill soft">{{ legacyPreview.history }} / {{ legacyPreview.activities }}</span>
      </div>
      <p class="muted">检测到旧版本地记录，可导入当前账户继续使用。</p>
      <button class="button primary full" :disabled="loading || !user" @click="$emit('import-legacy')">
        导入历史资料
      </button>
    </div>

    <div class="sidebar-section">
      <div class="section-head">
        <h2>最近案件</h2>
        <button class="text-button" :disabled="!user || loading" @click="$emit('refresh')">刷新</button>
      </div>
      <button class="button secondary full" :disabled="loading" @click="$emit('new-case')">新建案件</button>
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
      <div v-else class="empty-box">登录后可保存案件、文书和分析结果，后续继续补充。</div>
    </div>

    <div class="sidebar-section">
      <div class="section-head">
        <h2>最近办理</h2>
      </div>
      <div v-if="activities.length" class="activity-list">
        <article v-for="item in activities" :key="item.id" class="activity-card">
          <strong>{{ item.title }}</strong>
          <p>{{ item.detail }}</p>
          <span>{{ formatTime(item.created_at) }}</span>
        </article>
      </div>
      <div v-else class="empty-box">还没有案件办理记录。</div>
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

<style scoped>
.sidebar {
  gap: 14px;
  padding: 16px 14px 14px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.96), rgba(246, 240, 230, 0.92)),
    rgba(238, 241, 247, 0.92);
}

.brand-card,
.account-card,
.migration-card,
.sidebar-section {
  border: 1px solid rgba(221, 213, 200, 0.78);
  background: rgba(255, 255, 255, 0.82);
  box-shadow: 0 14px 34px rgba(31, 36, 51, 0.06);
}

.brand-card {
  align-items: start;
  gap: 12px;
  padding: 15px;
}

.brand-copy {
  min-width: 0;
  display: grid;
  gap: 8px;
}

.brand-copy h1 {
  font-size: 20px;
  line-height: 1.18;
  letter-spacing: -0.04em;
}

.brand-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.brand-chips span {
  min-height: 26px;
  display: inline-flex;
  align-items: center;
  padding: 0 10px;
  border-radius: 999px;
  color: var(--brand-2);
  background: rgba(31, 94, 255, 0.08);
  font-size: 12px;
  font-weight: 800;
}

.sidebar-nav {
  gap: 8px;
}

.sidebar-nav span {
  min-height: 40px;
  padding: 0 13px;
  border-radius: 11px;
  color: #566175;
  background: rgba(255, 255, 255, 0.65);
}

.sidebar-nav span.active {
  color: var(--brand);
  border-color: rgba(31, 94, 255, 0.14);
  background: rgba(31, 94, 255, 0.08);
  box-shadow: none;
}

.account-card,
.migration-card {
  display: grid;
  gap: 14px;
}

.account-line {
  align-items: start;
}

.account-line strong {
  display: block;
  margin-bottom: 4px;
}

.button-row {
  gap: 8px;
}

.button-row .button,
.button-row .text-button {
  flex: 1 1 0;
}

.saved-list,
.activity-list {
  gap: 10px;
}

.saved-card {
  gap: 8px;
}

.saved-main {
  display: grid;
  gap: 4px;
  min-height: 78px;
  padding: 13px 14px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.94);
}

.saved-main strong {
  margin-bottom: 0;
  font-size: 14px;
  line-height: 1.35;
}

.saved-main p,
.saved-main span {
  color: var(--muted);
  font-size: 12px;
  line-height: 1.5;
}

.activity-card {
  padding: 14px;
  background: rgba(255, 255, 255, 0.9);
}

.activity-card strong {
  font-size: 14px;
}

.activity-card p,
.activity-card span {
  color: var(--muted);
  font-size: 12px;
}

.empty-box {
  background: rgba(248, 244, 236, 0.72);
}

.section-head h2 {
  font-size: 15px;
}
</style>
