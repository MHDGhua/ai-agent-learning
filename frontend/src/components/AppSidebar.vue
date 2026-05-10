<template>
  <aside id="workspace-history" class="sidebar farui-sidebar">
    <div class="brand-card">
      <div class="brand-mark">L</div>
      <div class="brand-copy">
        <p class="eyebrow">L-ERAP PRO</p>
        <h1>劳动法专家</h1>
        <p class="muted">重庆劳动仲裁智能工作台</p>
        <div class="brand-chips" aria-label="工作台语义">
          <span>新版</span>
          <span>可信</span>
        </div>
      </div>
    </div>

    <nav class="sidebar-nav" aria-label="工作区模块">
      <span class="active"><i>□</i> 助理</span>
      <span><i>◇</i> 知识中心</span>
      <span><i>✧</i> 技能中心</span>
      <span><i>⌘</i> 应用中心</span>
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

    <div class="sidebar-bottom-links">
      <button type="button" @click="$emit('new-case')">↔ 切换至旧版视图</button>
      <button type="button" @click="$emit('refresh')">♢ 产品动态</button>
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
.farui-sidebar {
  gap: 18px;
  padding: 18px 16px;
  border-right-color: rgba(113, 132, 166, 0.16);
  background:
    linear-gradient(180deg, rgba(247, 249, 255, 0.96), rgba(241, 246, 255, 0.96)),
    #f3f6fd;
}

.brand-card,
.account-card,
.migration-card,
.sidebar-section {
  border: 1px solid rgba(95, 124, 177, 0.12);
  background: rgba(255, 255, 255, 0.64);
  box-shadow: none;
}

.brand-card {
  grid-template-columns: 34px 1fr;
  align-items: center;
  gap: 12px;
  padding: 0 2px 2px;
  border: 0;
  background: transparent;
}

.brand-copy {
  min-width: 0;
  display: grid;
  gap: 7px;
}

.brand-copy h1 {
  font-family: var(--font-body);
  font-size: 17px;
  line-height: 1.18;
  letter-spacing: -0.02em;
}

.brand-mark {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  color: #ffffff;
  background: linear-gradient(140deg, #6f6bff, #4f7cff 60%, #4bb7ff);
  box-shadow: 0 12px 28px rgba(67, 105, 255, 0.22);
  font-size: 17px;
}

.brand-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
}

.brand-chips span {
  min-height: 22px;
  display: inline-flex;
  align-items: center;
  padding: 0 8px;
  border-radius: 999px;
  color: #52607a;
  background: rgba(77, 121, 255, 0.08);
  font-size: 11px;
  font-weight: 800;
}

.sidebar-nav {
  gap: 12px;
}

.sidebar-nav span {
  min-height: 34px;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 8px;
  border-radius: 10px;
  color: #111827;
  background: transparent;
  font-size: 15px;
  font-weight: 700;
}

.sidebar-nav span i {
  width: 20px;
  color: #1f2937;
  font-style: normal;
  text-align: center;
}

.sidebar-nav span.active {
  color: #5b55ff;
  border-color: transparent;
  background: rgba(255, 255, 255, 0.34);
  box-shadow: none;
}

.account-card,
.migration-card,
.sidebar-section {
  display: grid;
  gap: 12px;
  padding: 14px;
  border-radius: 16px;
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
  display: grid;
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
  background: rgba(255, 255, 255, 0.82);
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
  background: rgba(255, 255, 255, 0.72);
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
  background: rgba(246, 249, 255, 0.82);
}

.section-head h2 {
  font-size: 15px;
}

.sidebar-bottom-links {
  margin-top: auto;
  display: grid;
  gap: 14px;
  padding: 8px 6px;
}

.sidebar-bottom-links button {
  min-height: 28px;
  border: 0;
  padding: 0;
  color: #24314b;
  background: transparent;
  text-align: left;
  font-weight: 700;
}

@media (max-width: 1240px) {
  .farui-sidebar {
    min-height: auto;
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .brand-card,
  .sidebar-nav,
  .sidebar-bottom-links {
    grid-column: 1 / -1;
  }
}

@media (max-width: 720px) {
  .farui-sidebar {
    grid-template-columns: 1fr;
  }
}
</style>
