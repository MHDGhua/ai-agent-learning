<template>
  <div class="loading-wrap" :class="{ fullscreen }" role="status" aria-live="polite">
    <span class="loading-spinner"></span>
    <p v-if="label">{{ label }}</p>
  </div>
</template>

<script setup>
defineProps({
  fullscreen: { type: Boolean, default: false },
  label: { type: String, default: "加载中..." },
});
</script>

<style scoped>
.loading-wrap {
  display: inline-grid;
  place-items: center;
  gap: 12px;
  color: var(--muted);
  font-weight: 800;
}

.loading-wrap.fullscreen {
  min-height: 100vh;
  width: 100%;
}

.loading-spinner {
  width: 38px;
  height: 38px;
  border: 4px solid rgba(31, 94, 255, 0.16);
  border-top-color: var(--brand);
  border-radius: 999px;
  animation: spin 0.72s linear infinite;
}

.loading-wrap p {
  margin: 0;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
