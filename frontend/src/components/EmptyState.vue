<template>
  <section class="empty-state-card">
    <div class="empty-state-icon">{{ icon }}</div>
    <h2>{{ title }}</h2>
    <p class="muted">{{ description }}</p>
    <RouterLink v-if="actionTo" class="button primary" :to="actionTo">{{ actionLabel }}</RouterLink>
    <button v-else-if="actionLabel" class="button primary" type="button" @click="$emit('action')">
      {{ actionLabel }}
    </button>
  </section>
</template>

<script setup>
import { RouterLink } from "vue-router";

defineProps({
  icon: { type: String, default: "空" },
  title: { type: String, required: true },
  description: { type: String, required: true },
  actionLabel: { type: String, default: "" },
  actionTo: { type: [String, Object], default: "" },
});

defineEmits(["action"]);
</script>
