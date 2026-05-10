<template>
  <div v-if="message" class="notice error error-alert" role="alert">
    <div>
      <strong v-if="title">{{ title }}</strong>
      <p>{{ message }}</p>
    </div>
    <button v-if="dismissible" class="icon-button danger" type="button" aria-label="关闭错误提示" @click="$emit('close')">
      ×
    </button>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, default: "" },
  message: { type: String, default: "" },
  dismissible: { type: Boolean, default: true },
});

defineEmits(["close"]);
</script>

<style scoped>
.error-alert {
  display: flex;
  align-items: start;
  justify-content: space-between;
  gap: 14px;
}

.error-alert strong {
  display: block;
  margin-bottom: 4px;
}

.error-alert p {
  margin: 0;
}

.error-alert .icon-button {
  flex: 0 0 auto;
  width: 32px;
  height: 32px;
  border-color: rgba(180, 35, 24, 0.2);
}
</style>
