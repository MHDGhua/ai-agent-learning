<template>
  <section class="panel span-2">
    <div class="panel-head">
      <div>
        <p class="eyebrow">文书草稿</p>
        <h3>{{ documentType }}</h3>
      </div>
      <button class="button secondary" :disabled="loading || !documentResult" @click="$emit('save')">
        保存草稿
      </button>
    </div>

    <div v-if="documentResult" class="document-card">
      <div class="document-head">
        <span class="status-pill good">已生成草稿</span>
        <span class="document-meta">{{ documentType }}</span>
      </div>
      <p class="muted">{{ documentResult.advice }}</p>
      <pre>{{ documentResult.content }}</pre>
    </div>
    <div v-else class="empty-box">完成案情整理后即可生成并保存文书草稿。</div>

    <div v-if="documentValidation" class="validation-grid">
      <article class="result-card">
        <p class="card-label">复核结果</p>
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

<style scoped>
.panel {
  padding: 20px;
  border-radius: 18px;
  border-color: rgba(221, 213, 200, 0.86);
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(250, 247, 240, 0.95)),
    var(--surface);
  box-shadow: 0 18px 50px rgba(31, 36, 51, 0.06);
}

.panel-head {
  align-items: start;
}

.panel-head h3 {
  font-size: 22px;
  line-height: 1.2;
}

.document-card {
  display: grid;
  gap: 14px;
  padding: 18px;
  border: 1px solid rgba(221, 213, 200, 0.8);
  border-radius: 16px;
  background: linear-gradient(180deg, rgba(248, 244, 236, 0.88), rgba(255, 255, 255, 0.96));
}

.document-head {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.document-meta {
  color: var(--muted);
  font-size: 13px;
  font-weight: 800;
}

.document-card pre {
  margin: 0;
  padding: 16px;
  border: 1px solid rgba(221, 213, 200, 0.7);
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.94);
}

.validation-grid {
  gap: 14px;
}

.result-card {
  background: rgba(255, 255, 255, 0.94);
}

.result-card strong {
  font-size: 18px;
}

@media (max-width: 940px) {
  .document-head {
    align-items: stretch;
  }
}
</style>
