<template>
  <main class="admin-page">
    <section class="settings-hero">
      <div>
        <p class="eyebrow">System Settings</p>
        <h1>系统设置</h1>
        <p class="muted">当前为前端占位配置，后续可接入管理员后端接口。</p>
      </div>
      <span class="status-pill soft">预留接口</span>
    </section>

    <form class="admin-grid" @submit.prevent="saveSettings">
      <section class="panel">
        <div class="panel-head">
          <div>
            <p class="card-label">API Strategy</p>
            <h3>API 策略配置</h3>
          </div>
        </div>
        <label class="field">
          <span>策略名称</span>
          <input v-model.trim="form.strategyName" type="text" />
        </label>
        <label class="field">
          <span>供应商</span>
          <select v-model="form.provider">
            <option>OpenAI</option>
            <option>Local LLM</option>
            <option>Mock Strategy</option>
          </select>
        </label>
        <label class="field">
          <span>模型</span>
          <input v-model.trim="form.model" type="text" />
        </label>
      </section>

      <section class="panel">
        <div class="panel-head">
          <div>
            <p class="card-label">Model Params</p>
            <h3>模型参数</h3>
          </div>
        </div>
        <label class="field">
          <span>Temperature</span>
          <input v-model.number="form.temperature" type="number" min="0" max="2" step="0.1" />
        </label>
        <label class="field">
          <span>Top-P</span>
          <input v-model.number="form.topP" type="number" min="0" max="1" step="0.05" />
        </label>
        <label class="field">
          <span>Max Tokens</span>
          <input v-model.number="form.maxTokens" type="number" min="512" max="32000" step="128" />
        </label>
      </section>

      <section class="panel span-2">
        <div class="panel-head">
          <div>
            <p class="card-label">Knowledge Base</p>
            <h3>知识库路径配置</h3>
          </div>
        </div>
        <label class="field">
          <span>法规知识库路径</span>
          <input v-model.trim="form.knowledgeBasePath" type="text" />
        </label>
        <label class="field">
          <span>运行时数据目录</span>
          <input v-model.trim="form.runtimeDataPath" type="text" />
        </label>
        <div v-if="message" class="notice success">{{ message }}</div>
        <button class="button primary" type="submit">{{ saving ? "保存中..." : "保存占位配置" }}</button>
      </section>
    </form>
  </main>
</template>

<script setup>
import { reactive, ref } from "vue";

const saving = ref(false);
const message = ref("");
const form = reactive({
  strategyName: "default-arbitration-strategy",
  provider: "OpenAI",
  model: "gpt-4.1-mini",
  temperature: 0.2,
  topP: 0.9,
  maxTokens: 4096,
  knowledgeBasePath: "data/knowledge_base",
  runtimeDataPath: "data/runtime",
});

function saveSettings() {
  saving.value = true;
  message.value = "";
  window.setTimeout(() => {
    saving.value = false;
    message.value = "配置已在前端暂存。后续接入管理员 API 后将保存到服务端。";
  }, 250);
}
</script>
