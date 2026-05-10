<template>
  <section class="panel span-2">
    <div class="panel-head">
      <div>
        <p class="eyebrow">文书草稿</p>
        <h3>{{ documentType }}</h3>
      </div>
      <button class="button secondary" :disabled="loading || !documentResult" @click="$emit('save')">
        保存当前文书
      </button>
    </div>

    <div v-if="documentResult" class="document-card">
      <p class="muted">{{ documentResult.advice }}</p>
      <pre>{{ documentResult.content }}</pre>
    </div>
    <div v-else class="empty-box">完成案情整理后即可生成并保存文书草稿。</div>

    <div v-if="documentValidation" class="validation-grid">
      <article class="result-card">
        <p class="card-label">校验结果</p>
        <strong>{{ documentValidation.is_valid ? "字段基本一致" : "需要人工复核" }}</strong>
        <p class="muted">校验时间：{{ formatTime(documentValidation.checked_at) }}</p>
      </article>
      <article class="result-card">
        <p class="card-label">问题</p>
        <ul class="plain-list">
          <li v-for="item in documentValidation.issues" :key="item">{{ item }}</li>
        </ul>
        <p v-if="!documentValidation.issues.length" class="muted">未发现强制性问题。</p>
      </article>
      <article class="result-card">
        <p class="card-label">警告</p>
        <ul class="plain-list">
          <li v-for="item in documentValidation.warnings" :key="item">{{ item }}</li>
        </ul>
        <p v-if="!documentValidation.warnings.length" class="muted">当前没有明显警告。</p>
      </article>
      <article class="result-card">
        <p class="card-label">建议</p>
        <ul class="plain-list">
          <li v-for="item in documentValidation.suggestions" :key="item">{{ item }}</li>
        </ul>
      </article>
    </div>
  </section>
</template>

<script setup>
defineProps({
  documentType: { type: String, default: "仲裁申请书" },
  documentResult: { type: Object, default: null },
  documentValidation: { type: Object, default: null },
  formatTime: { type: Function, required: true },
  loading: { type: Boolean, default: false },
});

defineEmits(["save"]);
</script>
