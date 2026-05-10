<template>
  <section class="panel">
    <div class="panel-head">
      <div>
        <p class="eyebrow">分析结果</p>
        <h3>系统输出</h3>
      </div>
      <span class="status-pill" :class="workupResult ? 'good' : 'soft'">
        {{ workupResult ? workupResult.workflow_stage : "等待案情输入" }}
      </span>
    </div>

    <div v-if="workupResult" class="result-stack">
      <article class="result-card accent">
        <p class="card-label">核心判断</p>
        <strong>{{ primaryFinding }}</strong>
        <p>{{ nextBestAction }}</p>
      </article>

      <div class="metric-grid">
        <article class="metric-card">
          <span>风险等级</span>
          <strong>{{ workupResult.analysis.risk_level }}</strong>
        </article>
        <article class="metric-card">
          <span>胜诉把握</span>
          <strong>{{ workupResult.success_prediction.success_probability }}</strong>
        </article>
        <article class="metric-card">
          <span>准备成本</span>
          <strong>¥{{ workupResult.cost.total_cost }}</strong>
        </article>
      </div>

      <div class="two-column">
        <article class="result-card">
          <p class="card-label">还缺哪些信息</p>
          <ul class="plain-list">
            <li v-for="item in missingQuestions" :key="item">{{ item }}</li>
          </ul>
          <p v-if="!missingQuestions.length" class="muted">当前关键信息相对完整。</p>
        </article>

        <article class="result-card">
          <p class="card-label">建议文书</p>
          <ul class="plain-list">
            <li v-for="item in workupResult.suggested_documents" :key="item">{{ item }}</li>
          </ul>
        </article>
      </div>

      <article class="result-card">
        <p class="card-label">流水线状态</p>
        <div class="pipeline-list">
          <div v-for="step in workupResult.pipeline_status" :key="step.name" class="pipeline-item">
            <div>
              <strong>{{ step.name }}</strong>
              <p>{{ step.summary || "已完成" }}</p>
            </div>
            <span>{{ step.elapsed_ms }} ms</span>
          </div>
        </div>
      </article>

      <article class="result-card">
        <p class="card-label">重庆本地参考</p>
        <div class="reference-list">
          <article v-for="ref in workupResult.local_references" :key="ref.title + ref.source" class="reference-card">
            <strong>{{ ref.title }}</strong>
            <p>{{ ref.summary || "暂无摘要" }}</p>
            <span>{{ ref.source || "重庆本地参考" }}</span>
          </article>
        </div>
      </article>
    </div>

    <div v-else class="empty-box tall">
      当前会话还没有分析结果。输入案情后，系统会返回风险、时效、证据缺口和本地参考。
    </div>
  </section>
</template>

<script setup>
defineProps({
  workupResult: { type: Object, default: null },
  primaryFinding: { type: String, default: "" },
  nextBestAction: { type: String, default: "" },
  missingQuestions: { type: Array, default: () => [] },
});
</script>
