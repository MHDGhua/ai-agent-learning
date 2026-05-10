<template>
  <div class="app-shell">
    <aside class="sidebar">
      <div class="brand-card">
        <div class="brand-mark">L</div>
        <div>
          <p class="eyebrow">L-ERAP PRO</p>
          <h1>重庆劳动仲裁工作台</h1>
          <p class="muted">真实账户、服务端保存、同域 API。</p>
        </div>
      </div>

      <div class="account-card">
        <div class="account-line">
          <div>
            <strong>{{ user ? user.full_name : "访客模式" }}</strong>
            <p class="muted">{{ user ? user.email : "未登录，仅临时查看当前会话" }}</p>
          </div>
          <span class="status-pill" :class="user ? 'good' : 'soft'">
            {{ user ? "已登录" : "未登录" }}
          </span>
        </div>
        <div class="button-row">
          <button class="button primary" @click="openAuthDialog('login')">
            {{ user ? "切换账户" : "登录 / 注册" }}
          </button>
          <button class="button secondary" :disabled="!user" @click="logout">退出</button>
          <button class="button secondary" :disabled="!user" @click="showPasswordDialog = true">改密码</button>
        </div>
      </div>

      <div class="sidebar-section">
        <div class="section-head">
          <h2>已保存案件</h2>
          <button class="text-button" :disabled="!user" @click="refreshWorkspaceData">刷新</button>
        </div>
        <button class="button secondary full" @click="startNewCase">新建当前会话</button>
        <div v-if="savedCases.length" class="saved-list">
          <article
            v-for="item in savedCases"
            :key="item.id"
            class="saved-card"
            :class="{ active: activeCaseId === item.id }"
          >
            <button class="saved-main" @click="loadCase(item.id)">
              <strong>{{ item.title }}</strong>
              <p>{{ item.case_type || "劳动争议" }}</p>
              <span>{{ formatTime(item.updated_at) }}</span>
            </button>
            <button class="icon-button danger" @click="deleteCase(item.id)">删</button>
          </article>
        </div>
        <div v-else class="empty-box">登录后可将会话、文书和分析结果保存到服务端。</div>
      </div>

      <div class="sidebar-section">
        <div class="section-head">
          <h2>最近动作</h2>
        </div>
        <div v-if="activities.length" class="activity-list">
          <article v-for="item in activities" :key="item.id" class="activity-card">
            <strong>{{ item.title }}</strong>
            <p>{{ item.detail }}</p>
            <span>{{ formatTime(item.created_at) }}</span>
          </article>
        </div>
        <div v-else class="empty-box">还没有服务端活动记录。</div>
      </div>
    </aside>

    <main class="main-shell">
      <header class="topbar">
        <div>
          <p class="eyebrow">当前会话</p>
          <h2>{{ currentTitle }}</h2>
          <p class="muted">
            API 基址：
            <code>{{ apiBaseHint }}</code>
          </p>
        </div>
        <div class="topbar-actions">
          <span class="status-pill soft">{{ readinessLabel }}</span>
          <button class="button secondary" :disabled="loading" @click="startNewCase">重置</button>
          <button class="button primary" :disabled="loading || !canSave" @click="saveCurrentCase">
            {{ activeCaseId ? "更新保存" : "保存到服务端" }}
          </button>
        </div>
      </header>

      <div class="content-grid">
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
              <input
                v-model="caseForm.applicant_info.employer_name"
                type="text"
                placeholder="重庆某科技公司"
              />
            </label>

            <label class="field">
              <span>工作地点</span>
              <input
                v-model="caseForm.applicant_info.workplace"
                type="text"
                placeholder="重庆市渝北区"
              />
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
                v-model="evidenceText"
                placeholder="每行一条，例如：劳动合同、工资流水、考勤记录、聊天记录"
              />
            </label>

            <label class="field">
              <span>默认文书</span>
              <select v-model="documentType">
                <option>仲裁申请书</option>
                <option>证据清单</option>
                <option>庭前调解申请书</option>
              </select>
            </label>

            <label class="field">
              <span>系统识别的案件类型</span>
              <input :value="inferCaseType()" type="text" readonly />
            </label>
          </div>

          <div class="button-row top-gap">
            <button class="button primary" :disabled="loading || !caseForm.facts.trim()" @click="analyzeCase">
              {{ loading ? "处理中..." : "整理案情并评估" }}
            </button>
            <button class="button secondary" :disabled="loading || !workupResult" @click="generateDocument">
              生成文书
            </button>
          </div>
        </section>

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

        <section class="panel span-2">
          <div class="panel-head">
            <div>
              <p class="eyebrow">文书草稿</p>
              <h3>{{ documentType }}</h3>
            </div>
            <button class="button secondary" :disabled="loading || !documentResult" @click="saveCurrentCase">
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
      </div>
    </main>

    <div v-if="showAuthDialog" class="overlay" @click.self="showAuthDialog = false">
      <div class="dialog">
        <div class="section-head">
          <h2>{{ authMode === "register" ? "注册并登录" : "登录账户" }}</h2>
          <button class="icon-button" @click="showAuthDialog = false">×</button>
        </div>

        <div class="form-grid">
          <label v-if="authMode === 'register'" class="field span-2">
            <span>姓名</span>
            <input v-model="authForm.full_name" type="text" placeholder="案件申请人姓名" />
          </label>

          <label v-if="authMode === 'register'" class="field">
            <span>身份</span>
            <input v-model="authForm.role" type="text" placeholder="案件申请人" />
          </label>

          <label class="field" :class="{ 'span-2': authMode === 'login' }">
            <span>邮箱</span>
            <input v-model="authForm.email" type="email" placeholder="name@example.com" />
          </label>

          <label class="field span-2">
            <span>密码</span>
            <input v-model="authForm.password" type="password" placeholder="至少 8 位" />
          </label>
        </div>

        <div class="button-row top-gap">
          <button class="button primary" :disabled="loading" @click="submitAuth">
            {{ authMode === "register" ? "创建账户" : "登录" }}
          </button>
          <button class="button secondary" @click="toggleAuthMode">
            {{ authMode === "register" ? "切换到登录" : "没有账户？去注册" }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="showPasswordDialog" class="overlay" @click.self="showPasswordDialog = false">
      <div class="dialog">
        <div class="section-head">
          <h2>修改密码</h2>
          <button class="icon-button" @click="showPasswordDialog = false">×</button>
        </div>

        <div class="form-grid">
          <label class="field span-2">
            <span>当前密码</span>
            <input v-model="passwordForm.current_password" type="password" placeholder="输入当前密码" />
          </label>
          <label class="field span-2">
            <span>新密码</span>
            <input v-model="passwordForm.new_password" type="password" placeholder="至少 8 位，包含字母和数字" />
          </label>
        </div>

        <div class="button-row top-gap">
          <button class="button primary" :disabled="loading" @click="changePassword">保存新密码</button>
          <button class="button secondary" @click="showPasswordDialog = false">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";

import { ApiError, arbitrationApi, authApi, workspaceApi } from "./api";

function createEmptyCaseForm() {
  return {
    facts: "",
    goal: "",
    years: 0,
    contact_phone: "",
    applicant_info: {
      name: "",
      employer_name: "",
      workplace: "",
      salary: 0,
    },
  };
}

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

const loading = ref(false);
const errorMessage = ref("");
const successMessage = ref("");
const user = ref(null);
const authMode = ref("login");
const showAuthDialog = ref(false);
const activeCaseId = ref(null);
const savedCases = ref([]);
const activities = ref([]);
const workupResult = ref(null);
const documentResult = ref(null);
const documentValidation = ref(null);
const evidenceText = ref("");
const documentType = ref("仲裁申请书");
const showPasswordDialog = ref(false);
const caseForm = reactive(createEmptyCaseForm());
const authForm = reactive({
  full_name: "",
  role: "案件申请人",
  email: "",
  password: "",
});
const passwordForm = reactive({
  current_password: "",
  new_password: "",
});

const apiBaseHint = computed(() => import.meta.env.VITE_API_BASE_URL || "同源 API");
const currentTitle = computed(() => {
  const employer = caseForm.applicant_info.employer_name?.trim();
  if (employer) {
    return `${inferCaseType()} · ${employer}`;
  }
  return "当前会话";
});
const readinessLabel = computed(() => workupResult.value?.workflow_stage || "尚未开始");
const primaryFinding = computed(() => workupResult.value?.analysis?.summary || "先整理案情，再生成结构化判断。");
const nextBestAction = computed(
  () => workupResult.value?.service_recommendation?.next_best_action || "先补充争议事实、工资和证据。"
);
const missingQuestions = computed(() => workupResult.value?.intake?.missing_questions || []);
const canSave = computed(() => !!workupResult.value || !!documentResult.value || !!caseForm.facts.trim());

function formatTime(value) {
  if (!value) {
    return "";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleString("zh-CN", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function inferCaseType() {
  const text = `${caseForm.facts} ${caseForm.goal}`.toLowerCase();
  if (/(工伤|受伤|职业病)/.test(text)) return "工伤待遇纠纷";
  if (/(拖欠|欠薪|工资)/.test(text)) return "工资报酬纠纷";
  if (/(加班)/.test(text)) return "加班费纠纷";
  if (/(调岗|降薪|辞退|解除|开除)/.test(text)) return "违法解除纠纷";
  if (/(平台|主播|骑手|网约车|配送|接单)/.test(text)) return "新就业形态劳动关系确认";
  return "劳动争议";
}

function deriveAmount() {
  const salary = Number(caseForm.applicant_info.salary || 0);
  const years = Number(caseForm.years || 0);
  const text = `${caseForm.facts} ${caseForm.goal} ${inferCaseType()}`;
  if (!salary) {
    return 0;
  }
  if (/(工资|欠薪|劳动报酬)/.test(text)) return Math.round(salary * 3);
  if (/(工伤|受伤|职业病)/.test(text)) return Math.round(salary * 12);
  if (/(加班)/.test(text)) return Math.round(salary * Math.max(1, years));
  if (/(违法解除|解除|辞退|开除)/.test(text)) return Math.round(salary * Math.max(1, years) * 2);
  return Math.round(salary * Math.max(1, years));
}

function evidenceList() {
  return evidenceText.value
    .split(/\n|,|，|、/)
    .map((item) => item.trim())
    .filter(Boolean);
}

function buildPayload() {
  const salary = Number(caseForm.applicant_info.salary || 0);
  const years = Number(caseForm.years || 0);
  return {
    case_type: inferCaseType(),
    facts: caseForm.facts,
    evidence: evidenceList(),
    evidence_quality: evidenceList().length >= 4 ? "良好" : evidenceList().length >= 2 ? "一般" : "较差",
    applicant_background: "普通员工",
    enable_opposition_review: true,
    years,
    salary,
    amount: deriveAmount(),
    contact_name: caseForm.applicant_info.name,
    contact_phone: caseForm.contact_phone,
    applicant_info: {
      ...clone(caseForm.applicant_info),
      salary,
      years,
    },
  };
}

function buildSnapshot() {
  return {
    title: currentTitle.value,
    caseForm: clone(caseForm),
    evidenceText: evidenceText.value,
    documentType: documentType.value,
    workupResult: clone(workupResult.value),
    documentResult: clone(documentResult.value),
    documentValidation: clone(documentValidation.value),
  };
}

function applySnapshot(snapshot) {
  const incomingCaseForm = snapshot?.caseForm || createEmptyCaseForm();
  Object.assign(caseForm, createEmptyCaseForm(), incomingCaseForm);
  Object.assign(caseForm.applicant_info, createEmptyCaseForm().applicant_info, incomingCaseForm.applicant_info || {});
  evidenceText.value = snapshot?.evidenceText || "";
  documentType.value = snapshot?.documentType || "仲裁申请书";
  workupResult.value = snapshot?.workupResult || null;
  documentResult.value = snapshot?.documentResult || null;
  documentValidation.value = snapshot?.documentValidation || null;
}

function resetMessages() {
  errorMessage.value = "";
  successMessage.value = "";
}

async function withLoading(task) {
  loading.value = true;
  resetMessages();
  try {
    await task();
  } catch (error) {
    if (error instanceof ApiError) {
      errorMessage.value = error.message;
    } else {
      errorMessage.value = "发生未预期错误，请稍后重试。";
      console.error(error);
    }
  } finally {
    loading.value = false;
  }
}

function openAuthDialog(mode = "login") {
  authMode.value = mode;
  showAuthDialog.value = true;
}

function toggleAuthMode() {
  authMode.value = authMode.value === "register" ? "login" : "register";
}

async function loadSession() {
  try {
    const response = await authApi.me();
    user.value = response.user;
    await refreshWorkspaceData();
  } catch (error) {
    user.value = null;
  }
}

async function persistCurrentCase(options = {}) {
  if (!user.value || !canSave.value) {
    return;
  }
  const saved = await workspaceApi.saveCase({
    id: activeCaseId.value,
    title: currentTitle.value,
    case_type: inferCaseType(),
    primary_finding: primaryFinding.value,
    readiness: readinessLabel.value,
    next_best_action: nextBestAction.value,
    snapshot: buildSnapshot(),
  });
  activeCaseId.value = saved.id;
  await refreshWorkspaceData();
  if (!options.silent) {
    successMessage.value = "当前会话已保存到服务端。";
  }
}

async function submitAuth() {
  await withLoading(async () => {
    const response =
      authMode.value === "register"
        ? await authApi.register({
            full_name: authForm.full_name,
            role: authForm.role,
            email: authForm.email,
            password: authForm.password,
          })
        : await authApi.login({
            email: authForm.email,
            password: authForm.password,
          });
    user.value = response.user;
    if (!caseForm.applicant_info.name) {
      caseForm.applicant_info.name = response.user.full_name;
    }
    authForm.password = "";
    showAuthDialog.value = false;
    successMessage.value = authMode.value === "register" ? "账户已创建并登录。" : "登录成功。";
    await refreshWorkspaceData();
    if (caseForm.facts.trim()) {
      await persistCurrentCase({ silent: true });
    }
  });
}

async function logout() {
  await withLoading(async () => {
    await authApi.logout();
    user.value = null;
    savedCases.value = [];
    activities.value = [];
    activeCaseId.value = null;
    successMessage.value = "已退出登录。";
  });
}

async function refreshWorkspaceData() {
  if (!user.value) {
    savedCases.value = [];
    activities.value = [];
    return;
  }
  const [casesResponse, activitiesResponse] = await Promise.all([
    workspaceApi.listCases(),
    workspaceApi.listActivities(),
  ]);
  savedCases.value = casesResponse.items || [];
  activities.value = activitiesResponse.items || [];
}

async function analyzeCase() {
  await withLoading(async () => {
    const payload = buildPayload();
    workupResult.value = await arbitrationApi.workup(payload);
    if (user.value) {
      await persistCurrentCase({ silent: true });
    }
    successMessage.value = "案情已整理完成。";
  });
}

async function validateDocument(payload, content) {
  documentValidation.value = await arbitrationApi.validateDocument({
    document_type: documentType.value,
    case_data: payload,
    content,
  });
}

async function generateDocument() {
  await withLoading(async () => {
    const payload = buildPayload();
    documentResult.value = await arbitrationApi.generateDocument({
      document_type: documentType.value,
      case_data: payload,
    });
    await validateDocument(payload, documentResult.value.content);
    if (user.value) {
      await persistCurrentCase({ silent: true });
    }
    successMessage.value = `${documentType.value} 已生成。`;
  });
}

async function saveCurrentCase() {
  if (!user.value) {
    openAuthDialog("login");
    errorMessage.value = "保存到服务端前请先登录。";
    return;
  }
  await withLoading(async () => {
    await persistCurrentCase();
  });
}

async function loadCase(caseId) {
  await withLoading(async () => {
    const detail = await workspaceApi.getCase(caseId);
    activeCaseId.value = detail.id;
    applySnapshot(detail.snapshot);
    successMessage.value = "已恢复服务端保存的案件。";
  });
}

async function deleteCase(caseId) {
  await withLoading(async () => {
    await workspaceApi.deleteCase(caseId);
    if (activeCaseId.value === caseId) {
      startNewCase();
    }
    successMessage.value = "案件已删除。";
    await refreshWorkspaceData();
  });
}

async function changePassword() {
  await withLoading(async () => {
    const response = await authApi.changePassword({
      current_password: passwordForm.current_password,
      new_password: passwordForm.new_password,
    });
    user.value = response.user;
    passwordForm.current_password = "";
    passwordForm.new_password = "";
    showPasswordDialog.value = false;
    successMessage.value = "密码已更新，旧会话已失效。";
    await refreshWorkspaceData();
  });
}

function startNewCase() {
  Object.assign(caseForm, createEmptyCaseForm());
  Object.assign(caseForm.applicant_info, createEmptyCaseForm().applicant_info);
  if (user.value && !caseForm.applicant_info.name) {
    caseForm.applicant_info.name = user.value.full_name;
  }
  evidenceText.value = "";
  workupResult.value = null;
  documentResult.value = null;
  documentValidation.value = null;
  documentType.value = "仲裁申请书";
  activeCaseId.value = null;
  resetMessages();
}

onMounted(async () => {
  await loadSession();
});
</script>
