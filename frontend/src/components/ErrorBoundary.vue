<template>
  <slot v-if="!error" />
  <main v-else class="app-error-boundary" role="alert">
    <section class="error-boundary-card">
      <p class="eyebrow">Runtime Error</p>
      <h1>页面渲染时发生错误</h1>
      <p class="muted">
        当前操作已被中断。请刷新页面后重试；如果问题重复出现，请保留当前输入并联系系统维护人员。
      </p>
      <pre v-if="message">{{ message }}</pre>
      <div class="button-row">
        <button class="button primary" type="button" @click="reloadPage">刷新页面</button>
        <button class="button secondary" type="button" @click="clearError">留在当前页</button>
      </div>
    </section>
  </main>
</template>

<script setup>
import { computed, onErrorCaptured, ref } from "vue";

const error = ref(null);

const message = computed(() => {
  if (!import.meta.env.DEV || !error.value) {
    return "";
  }
  return error.value?.stack || error.value?.message || String(error.value);
});

onErrorCaptured((err) => {
  error.value = err;
  console.error(err);
  return false;
});

function clearError() {
  error.value = null;
}

function reloadPage() {
  window.location.reload();
}
</script>
