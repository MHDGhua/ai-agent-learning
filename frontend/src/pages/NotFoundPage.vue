<template>
  <main class="not-found-page">
    <section class="not-found-card">
      <p class="eyebrow">404</p>
      <h1>页面不存在</h1>
      <p class="muted">你访问的地址没有对应页面。可以返回首页，或进入案件助手继续处理案件。</p>
      <div class="button-row">
        <RouterLink class="button primary" to="/">返回首页</RouterLink>
        <RouterLink class="button secondary" to="/assistant">进入工作区</RouterLink>
      </div>
    </section>
  </main>
</template>

<script setup>
import { RouterLink } from "vue-router";
</script>
