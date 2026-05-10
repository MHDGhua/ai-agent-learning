<template>
  <section class="panel">
    <div class="panel-head">
      <div>
        <p class="eyebrow">研判摘要</p>
        <h3>案件助手判断</h3>
      </div>
      <span class="status-pill" :class="workupResult ? 'good' : 'soft'">
        {{ resultBadge }}
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
        <p class="card-label">办理进度</p>
        <div class="progress-list">
          <div v-for="step in userFacingSteps" :key="step.name" class="progress-item">
            <div>
              <strong>{{ step.label }}</strong>
              <p>{{ step.summary }}</p>
            </div>
            <span>{{ step.status }}</span>
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
import { computed } from "vue";

const props = defineProps({
  workupResult: { type: Object, default: null },
  primaryFinding: { type: String, default: "" },
  nextBestAction: { type: String, default: "" },
  missingQuestions: { type: Array, default: () => [] },
});

const STEP_LABELS = {
  case_analysis: "案情研判",
  intake_checklist: "材料核对",
  cost_estimate: "成本估算",
  cost_prediction: "成本与把握",
  success_prediction: "胜诉把握",
  local_references: "本地参考",
  final_assembly: "结果汇总",
};

function formatStepKey(step) {
  return String(step.name || "").toLowerCase();
}

function formatStepLabel(step) {
  const key = formatStepKey(step);
  if (STEP_LABELS[key]) {
    return STEP_LABELS[key];
  }
  if (key.includes("opposition")) return "红蓝复核";
  if (key.includes("jurisdiction")) return "管辖检查";
  if (key.includes("limitation") || key.includes("time")) return "时效检查";
  if (key.includes("evidence")) return "证据核对";
  if (key.includes("recommend")) return "行动建议";
  if (key.includes("document")) return "文书准备";
  return "办理步骤";
}

function formatStepSummary(step) {
  const key = formatStepKey(step);
  if (step.warnings?.length) {
    return `需要关注：${step.warnings.join("、")}`;
  }
  const summaries = {
    case_analysis: "已完成争议类型、风险等级和争议焦点整理。",
    intake_checklist: "已整理待补信息、证据方向和管辖时效提示。",
    cost_estimate: "已估算当前准备成本。",
    cost_prediction: "已估算准备成本和当前胜诉把握。",
    success_prediction: "已评估当前胜诉把握。",
    local_references: "已匹配重庆本地公开参考资料。",
    final_assembly: "已汇总为当前页面的行动建议。",
    opposition_review: "已汇总红蓝复核观点。",
    jurisdiction_check: "已完成管辖判断。",
    limitation_check: "已完成时效检查。",
    evidence_review: "已完成证据核对。",
    service_recommendation: "已完成行动建议汇总。",
  };
  if (summaries[key]) {
    return summaries[key];
  }
  if (key.includes("opposition")) return "已汇总红蓝复核观点。";
  if (key.includes("jurisdiction")) return "已完成管辖判断。";
  if (key.includes("limitation") || key.includes("time")) return "已完成时效检查。";
  if (key.includes("evidence")) return "已完成证据核对。";
  if (key.includes("recommend")) return "已完成行动建议汇总。";
  if (key.includes("document")) return "已完成文书准备建议。";
  return "已完成";
}

function formatStepStatus(step) {
  const normalized = String(step.status || "").toLowerCase();
  if (["failed", "error"].includes(normalized)) {
    return "需复核";
  }
  if (step.warnings?.length) {
    return "需关注";
  }
  if (["completed", "complete", "ok", "success", "done"].includes(normalized)) {
    return "完成";
  }
  return "处理中";
}

const resultBadge = computed(() => {
  if (!props.workupResult) {
    return "等待案情输入";
  }
  return "已完成本轮整理";
});

const userFacingSteps = computed(() => {
  const steps = props.workupResult?.pipeline_status || [];
  return steps.map((step) => ({
    name: step.name,
    label: formatStepLabel(step),
    summary: formatStepSummary(step),
    status: formatStepStatus(step),
  }));
});
</script>

<style scoped>
.panel {
  padding: 20px;
  border-radius: 18px;
  border-color: rgba(221, 213, 200, 0.86);
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(249, 246, 239, 0.96)),
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

.result-stack {
  gap: 14px;
}

.result-card {
  border-color: rgba(221, 213, 200, 0.82);
  background: rgba(255, 255, 255, 0.95);
}

.result-card.accent {
  border: 0;
  box-shadow: 0 20px 48px rgba(31, 94, 255, 0.16);
}

.metric-card {
  background: linear-gradient(180deg, rgba(248, 244, 236, 0.96), rgba(255, 255, 255, 0.98));
}

.metric-card strong {
  font-size: 24px;
}

.plain-list {
  padding-left: 18px;
}

.progress-item {
  border: 1px solid rgba(221, 213, 200, 0.72);
  background: rgba(248, 244, 236, 0.78);
}

.progress-item strong {
  font-size: 14px;
}

.progress-item p {
  margin-top: 4px;
}

.reference-list {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.reference-card {
  background: rgba(255, 255, 255, 0.92);
}

@media (max-width: 940px) {
  .reference-list {
    grid-template-columns: 1fr;
  }
}
</style>
