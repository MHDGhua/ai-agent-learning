<template>
  <section class="panel">
    <div class="panel-head">
      <div>
        <p class="eyebrow">案件输入</p>
        <h3>先把事实说清楚</h3>
      </div>
      <span class="status-pill" :class="workupResult ? 'good' : 'soft'">
        {{ workupResult ? "已分析" : "未分析" }}
      </span>
    </div>

    <div v-if="errorMessage" class="notice error">{{ errorMessage }}</div>
    <div v-if="successMessage" class="notice success">{{ successMessage }}</div>
    <div v-if="!user" class="notice">
      现在可以直接试跑分析；如果希望保存历史、恢复草稿和跨设备使用，请先登录真实账户。
    </div>

    <div class="form-grid">
      <label class="field span-2">
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
        <span>系统识别的案件类型</span>
        <input :value="caseType" type="text" readonly />
      </label>
    </div>

    <div class="button-row top-gap">
      <button class="button primary" :disabled="loading || !caseForm.facts.trim()" @click="$emit('analyze')">
        {{ loading ? "处理中..." : "整理案情并评估" }}
      </button>
      <button class="button secondary" :disabled="loading || !workupResult" @click="$emit('generate-document')">
        生成文书
      </button>
    </div>
  </section>
</template>

<script setup>
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
