<template>
  <ErrorBoundary>
    <RouterView v-slot="{ Component, route }">
      <Transition name="page-fade" mode="out-in">
        <component :is="Component" :key="route.fullPath" />
      </Transition>
    </RouterView>
  </ErrorBoundary>
</template>

<script setup>
import { RouterView } from "vue-router";

import ErrorBoundary from "./components/ErrorBoundary.vue";
</script>
