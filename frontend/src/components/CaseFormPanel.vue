<template>
  <section class="panel intake-panel">
    <div class="panel-head">
      <div>
        <p class="eyebrow">案件输入</p>
        <h3>先把事实说清楚</h3>
      </div>
      <span class="status-pill" :class="workupResult ? 'good' : 'soft'">
        {{ workupResult ? "已整理" : "待整理" }}
      </span>
    </div>

    <div class="intro-card">
      <div>
        <strong>把事实、目标和证据一次放进来</strong>
        <p class="muted">右侧会自动整理成可复核的分析和文书草稿，适合继续补充和回看。</p>
      </div>
      <div class="intro-tags" aria-label="输入顺序建议">
        <span>先事实</span>
        <span>再目标</span>
        <span>后证据</span>
      </div>
    </div>

    <ErrorAlert :message="errorMessage" title="操作失败" :dismissible="false" />
    <div v-if="successMessage" class="notice success">{{ successMessage }}</div>
    <div v-if="!user" class="notice">
      可以先直接整理案情；如果希望保存历史、恢复草稿和跨设备继续办理，请先登录账户。
    </div>

    <div class="form-grid">
      <label class="field span-2 hero-field">
        <span>案情事实</span>
        <textarea
          v-model="caseForm.facts"
          placeholder="按时间顺序描述入职、争议经过、沟通记录、离职或目前状态。"
        />
      </label>

      <label class="field span-2">
        <span>你的目标</span>
        <input
          v-model="caseForm.goal"
          type="text"
          placeholder="例如：要回 3 个月工资并准备仲裁申请书"
        />
      </label>

      <label class="field">
        <span>申请人姓名</span>
        <input v-model="caseForm.applicant_info.name" type="text" placeholder="张三" />
      </label>

      <label class="field">
        <span>联系电话</span>
        <input v-model="caseForm.contact_phone" type="text" placeholder="手机号码" />
      </label>

      <label class="field">
        <span>单位名称</span>
        <input v-model="caseForm.applicant_info.employer_name" type="text" placeholder="重庆某科技公司" />
      </label>

      <label class="field">
        <span>工作地点</span>
        <input v-model="caseForm.applicant_info.workplace" type="text" placeholder="重庆市渝北区" />
      </label>

      <label class="field">
        <span>月工资</span>
        <input v-model.number="caseForm.applicant_info.salary" type="number" min="0" />
      </label>

      <label class="field">
        <span>工作年限</span>
        <input v-model.number="caseForm.years" type="number" min="0" step="0.1" />
      </label>

      <label class="field span-2">
        <span>现有证据</span>
        <textarea
          :value="evidenceText"
          placeholder="每行一条，例如：劳动合同、工资流水、考勤记录、聊天记录"
          @input="$emit('update:evidence-text', $event.target.value)"
        />
      </label>

      <label class="field">
        <span>默认文书</span>
        <select :value="documentType" @change="$emit('update:document-type', $event.target.value)">
          <option>仲裁申请书</option>
          <option>证据清单</option>
          <option>庭前调解申请书</option>
        </select>
      </label>

      <label class="field">
        <span>当前判断的案件类型</span>
        <input :value="caseType" type="text" readonly />
      </label>
    </div>

    <div class="button-row top-gap action-row">
      <button class="button primary" :disabled="loading || !caseForm.facts.trim()" @click="$emit('analyze')">
        {{ loading ? "整理中..." : "整理案情并评估" }}
      </button>
      <button class="button secondary" :disabled="loading || !workupResult" @click="$emit('generate-document')">
        生成文书
      </button>
    </div>
  </section>
</template>

<script setup>
import ErrorAlert from "./ErrorAlert.vue";

defineProps({
  loading: { type: Boolean, default: false },
  user: { type: Object, default: null },
  workupResult: { type: Object, default: null },
  errorMessage: { type: String, default: "" },
  successMessage: { type: String, default: "" },
  caseForm: { type: Object, required: true },
  evidenceText: { type: String, default: "" },
  documentType: { type: String, default: "仲裁申请书" },
  caseType: { type: String, default: "劳动争议" },
});

defineEmits(["update:evidence-text", "update:document-type", "analyze", "generate-document"]);
</script>

<style scoped>
.intake-panel {
  padding: 20px;
  border-radius: 18px;
  border-color: rgba(221, 213, 200, 0.9);
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(251, 247, 239, 0.94)),
    var(--surface);
  box-shadow: 0 20px 56px rgba(31, 36, 51, 0.07);
}

.panel-head {
  gap: 16px;
}

.panel-head h3 {
  font-size: clamp(24px, 2.8vw, 34px);
}

.intro-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 16px 18px;
  border: 1px solid rgba(31, 94, 255, 0.12);
  border-radius: 16px;
  background: linear-gradient(135deg, rgba(31, 94, 255, 0.06), rgba(255, 255, 255, 0.9));
}

.intro-card strong {
  display: block;
  margin-bottom: 6px;
  font-size: 16px;
}

.intro-tags {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;
}

.intro-tags span {
  min-height: 28px;
  display: inline-flex;
  align-items: center;
  padding: 0 10px;
  border-radius: 999px;
  color: var(--brand-2);
  background: rgba(31, 94, 255, 0.08);
  font-size: 12px;
  font-weight: 800;
}

.form-grid {
  gap: 16px;
}

.field {
  gap: 8px;
}

.field span {
  color: #5a6479;
}

.hero-field textarea {
  min-height: 240px;
  border-radius: 16px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.92), rgba(255, 255, 255, 1)),
    var(--surface-strong);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.8);
}

.field input,
.field select,
.field textarea {
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.94);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.75);
}

.field input[readonly] {
  color: var(--brand-2);
  background: rgba(31, 94, 255, 0.05);
}

.action-row {
  padding-top: 4px;
}

.action-row .button {
  min-width: 180px;
}

@media (max-width: 940px) {
  .intro-card {
    flex-direction: column;
    align-items: stretch;
  }

  .intro-tags {
    justify-content: flex-start;
  }

  .action-row .button {
    min-width: 0;
  }
}
</style>
