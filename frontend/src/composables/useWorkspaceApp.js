import { computed, onMounted, reactive, ref } from "vue";

import { ApiError, arbitrationApi, authApi, workspaceApi } from "../api";

const LEGACY_KEYS = {
  history: "lerap_ui_history",
  activities: "lerap_ui_activities",
  imported: "lerap_legacy_imported_v1",
};

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

function safeParseLocalStorage(key, fallback) {
  try {
    const raw = window.localStorage.getItem(key);
    return raw ? JSON.parse(raw) : fallback;
  } catch {
    return fallback;
  }
}

function formatReadinessLabel(value) {
  if (!value) {
    return "已完成整理";
  }
  const text = String(value).trim();
  const normalized = text.toLowerCase();
  if (["completed", "complete", "ok", "success", "done"].includes(normalized)) {
    return "已完成整理";
  }
  if (text.includes("补充")) {
    return "待补充";
  }
  if (text.includes("提交")) {
    return "可提交材料";
  }
  if (text.includes("复核") || text.includes("校验")) {
    return "需复核";
  }
  if (text.includes("完成")) {
    return "已完成整理";
  }
  return "已完成整理";
}

export function useWorkspaceApp() {
  const loading = ref(false);
  const errorMessage = ref("");
  const successMessage = ref("");
  const user = ref(null);
  const authMode = ref("login");
  const showAuthDialog = ref(false);
  const showPasswordDialog = ref(false);
  const showProfileDialog = ref(false);
  const activeCaseId = ref(null);
  const savedCases = ref([]);
  const activities = ref([]);
  const workupResult = ref(null);
  const documentResult = ref(null);
  const documentValidation = ref(null);
  const evidenceText = ref("");
  const documentType = ref("仲裁申请书");
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
  const profileForm = reactive({
    full_name: "",
    role: "案件申请人",
  });
  const legacyHistoryEntries = ref([]);
  const legacyActivities = ref([]);
  const legacyImported = ref(false);

  const currentTitle = computed(() => {
    const employer = caseForm.applicant_info.employer_name?.trim();
    if (employer) {
      return `${inferCaseType()} · ${employer}`;
    }
    return "当前会话";
  });
  const readinessLabel = computed(() =>
    workupResult.value ? formatReadinessLabel(workupResult.value.workflow_stage) : "尚未开始"
  );
  const primaryFinding = computed(
    () => workupResult.value?.analysis?.summary || "先整理案情，再生成结构化判断。"
  );
  const nextBestAction = computed(
    () => workupResult.value?.service_recommendation?.next_best_action || "先补充争议事实、工资和证据。"
  );
  const missingQuestions = computed(() => workupResult.value?.intake?.missing_questions || []);
  const canSave = computed(() => !!workupResult.value || !!documentResult.value || !!caseForm.facts.trim());
  const hasLegacyData = computed(
    () => !legacyImported.value && (legacyHistoryEntries.value.length > 0 || legacyActivities.value.length > 0)
  );
  const legacyPreview = computed(() => ({
    history: legacyHistoryEntries.value.length,
    activities: legacyActivities.value.length,
  }));

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

  function closeAuthDialog() {
    showAuthDialog.value = false;
  }

  function toggleAuthMode() {
    authMode.value = authMode.value === "register" ? "login" : "register";
  }

  function openProfileDialog() {
    if (!user.value) {
      return;
    }
    profileForm.full_name = user.value.full_name;
    profileForm.role = user.value.role;
    showProfileDialog.value = true;
  }

  function closeProfileDialog() {
    showProfileDialog.value = false;
  }

  function openPasswordDialog() {
    showPasswordDialog.value = true;
  }

  function closePasswordDialog() {
    showPasswordDialog.value = false;
  }

  function setEvidenceText(value) {
    evidenceText.value = value;
  }

  function setDocumentType(value) {
    documentType.value = value;
  }

  function loadLegacyData() {
    legacyHistoryEntries.value = safeParseLocalStorage(LEGACY_KEYS.history, []);
    legacyActivities.value = safeParseLocalStorage(LEGACY_KEYS.activities, []);
    legacyImported.value = window.localStorage.getItem(LEGACY_KEYS.imported) === "true";
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

  async function loadSession() {
    try {
      const response = await authApi.session();
      if (!response.user) {
        user.value = null;
        profileForm.full_name = "";
        profileForm.role = "案件申请人";
        return;
      }
      user.value = response.user;
      profileForm.full_name = response.user.full_name;
      profileForm.role = response.user.role;
      if (!caseForm.applicant_info.name) {
        caseForm.applicant_info.name = response.user.full_name;
      }
      await refreshWorkspaceData();
    } catch {
      user.value = null;
      profileForm.full_name = "";
      profileForm.role = "案件申请人";
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
      successMessage.value = "当前案件已保存。";
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
      profileForm.full_name = response.user.full_name;
      profileForm.role = response.user.role;
      if (!caseForm.applicant_info.name) {
        caseForm.applicant_info.name = response.user.full_name;
      }
      authForm.password = "";
      closeAuthDialog();
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
      showProfileDialog.value = false;
      showPasswordDialog.value = false;
      successMessage.value = "已退出登录。";
    });
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
      errorMessage.value = "保存案件前请先登录。";
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
      successMessage.value = "已恢复保存的案件。";
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
      closePasswordDialog();
      successMessage.value = "密码已更新，旧会话已失效。";
      await refreshWorkspaceData();
    });
  }

  async function updateProfile() {
    await withLoading(async () => {
      const previousName = user.value?.full_name || "";
      const response = await authApi.updateProfile({
        full_name: profileForm.full_name,
        role: profileForm.role,
      });
      user.value = response.user;
      if (!caseForm.applicant_info.name || caseForm.applicant_info.name === previousName) {
        caseForm.applicant_info.name = response.user.full_name;
      }
      closeProfileDialog();
      successMessage.value = "账户资料已更新。";
      await refreshWorkspaceData();
      if (canSave.value && user.value) {
        await persistCurrentCase({ silent: true });
      }
    });
  }

  async function importLegacyData() {
    if (!user.value) {
      openAuthDialog("login");
      errorMessage.value = "导入旧版本记录前请先登录。";
      return;
    }
    await withLoading(async () => {
      const response = await workspaceApi.importLegacy({
        history_entries: legacyHistoryEntries.value,
        activities: legacyActivities.value,
      });
      window.localStorage.setItem(LEGACY_KEYS.imported, "true");
      loadLegacyData();
      successMessage.value = `旧数据导入完成：${response.imported_cases} 个案件，${response.imported_activities} 条动作。`;
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
    loadLegacyData();
  });

  return {
    loading,
    errorMessage,
    successMessage,
    user,
    authMode,
    showAuthDialog,
    showPasswordDialog,
    showProfileDialog,
    activeCaseId,
    savedCases,
    activities,
    workupResult,
    documentResult,
    documentValidation,
    evidenceText,
    documentType,
    caseForm,
    authForm,
    passwordForm,
    profileForm,
    currentTitle,
    readinessLabel,
    primaryFinding,
    nextBestAction,
    missingQuestions,
    canSave,
    hasLegacyData,
    legacyPreview,
    formatTime,
    inferCaseType,
    loadSession,
    openAuthDialog,
    closeAuthDialog,
    openProfileDialog,
    closeProfileDialog,
    openPasswordDialog,
    closePasswordDialog,
    setEvidenceText,
    setDocumentType,
    toggleAuthMode,
    submitAuth,
    logout,
    refreshWorkspaceData,
    analyzeCase,
    generateDocument,
    saveCurrentCase,
    loadCase,
    deleteCase,
    changePassword,
    updateProfile,
    importLegacyData,
    startNewCase,
  };
}
