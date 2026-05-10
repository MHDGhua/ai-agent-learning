<template>
  <main class="cases-page">
    <section class="settings-hero">
      <div>
        <p class="eyebrow">Case Library</p>
        <h1>我的案件</h1>
        <p class="muted">从服务端持久化记录中恢复案件、分析和文书草稿。</p>
      </div>
      <RouterLink class="button primary" to="/assistant">新建案件</RouterLink>
    </section>

    <div v-if="errorMessage" class="notice error">{{ errorMessage }}</div>
    <div v-if="loading" class="empty-box">案件列表加载中...</div>

    <section v-else-if="cases.length" class="case-grid" aria-label="案件列表">
      <button v-for="item in cases" :key="item.id" class="case-card" type="button" @click="openCase(item.id)">
        <div class="case-card-head">
          <span class="status-pill">{{ item.readiness || "已保存" }}</span>
          <small>{{ formatDate(item.created_at) }}</small>
        </div>
        <strong>{{ item.title || "未命名案件" }}</strong>
        <p>{{ item.primary_finding || item.case_type || "劳动争议案件" }}</p>
        <div class="case-card-foot">
          <span>{{ item.case_type || "劳动争议" }}</span>
          <span>最近活动：{{ formatDate(item.updated_at) || "刚刚" }}</span>
        </div>
      </button>
    </section>

    <section v-else class="empty-state-card">
      <div class="empty-state-icon">案</div>
      <h2>还没有保存的案件</h2>
      <p class="muted">进入案件助手完成一次分析后，可以把事实、证据和文书保存到这里。</p>
      <RouterLink class="button primary" to="/assistant">进入案件助手</RouterLink>
    </section>
  </main>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { RouterLink, useRouter } from "vue-router";

import { ApiError, workspaceApi } from "../api";

const router = useRouter();
const cases = ref([]);
const loading = ref(false);
const errorMessage = ref("");

function formatDate(value) {
  if (!value) {
    return "";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleString("zh-CN", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

async function loadCases() {
  loading.value = true;
  errorMessage.value = "";
  try {
    const response = await workspaceApi.listCases();
    cases.value = response.items || [];
  } catch (error) {
    errorMessage.value = error instanceof ApiError ? error.message : "案件列表加载失败。";
  } finally {
    loading.value = false;
  }
}

async function openCase(caseId) {
  await router.push({ name: "assistant", query: { caseId } });
}

onMounted(loadCases);
</script>
