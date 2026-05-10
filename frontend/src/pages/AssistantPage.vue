<template>
  <div class="assistant-farui-shell">
    <AppSidebar
      :user="app.user"
      :loading="app.loading"
      :saved-cases="app.savedCases"
      :active-case-id="app.activeCaseId"
      :activities="app.activities"
      :has-legacy-data="app.hasLegacyData"
      :legacy-preview="app.legacyPreview"
      :format-time="app.formatTime"
      @login="app.openAuthDialog('login')"
      @logout="app.logout"
      @profile="app.openProfileDialog"
      @password="app.openPasswordDialog"
      @refresh="app.refreshWorkspaceData"
      @new-case="app.startNewCase"
      @load-case="loadCaseAndSyncRoute"
      @delete-case="app.deleteCase"
      @import-legacy="app.importLegacyData"
    />

    <main class="farui-workspace">
      <div class="workspace-topline">
        <button class="workspace-history-button" type="button" @click="scrollToSidebar">
          <span aria-hidden="true">◷</span>
          历史记录
        </button>
        <div class="workspace-quick-actions">
          <button class="ghost-link" type="button" @click="router.push({ name: 'home' })">官网首页</button>
          <button class="ghost-link" type="button" @click="startNewCase">新建会话</button>
          <button class="primary-mini" :disabled="app.loading || !app.canSave" type="button" @click="app.saveCurrentCase">
            {{ app.activeCaseId ? "更新案件" : "保存案件" }}
          </button>
        </div>
      </div>

      <section class="workspace-hero" aria-labelledby="assistant-title">
        <h1 id="assistant-title">L-ERAP PRO</h1>
        <p>安全可信的重庆劳动法助手</p>
      </section>

      <section class="workspace-composer" aria-label="中心输入区">
        <textarea
          v-model="assistantPrompt"
          maxlength="5000"
          placeholder="阅读起诉状、答辩状、代理词，整理一下庭审问答题纲"
        />
        <div class="composer-footer">
          <div class="composer-tools" aria-label="常用输入能力">
            <button
              v-for="tool in composerTools"
              :key="tool.label"
              type="button"
              :disabled="app.loading"
              @click="applyComposerTool(tool)"
            >
              <span>{{ tool.icon }}</span>
              {{ tool.label }}
            </button>
          </div>
          <div class="composer-send">
            <span>{{ promptLength }} / 5000</span>
            <button
              class="send-button"
              :disabled="app.loading || !assistantPrompt.trim()"
              type="button"
              aria-label="发送并分析"
              @click="submitPrompt"
            >
              {{ app.loading ? "…" : "↗" }}
            </button>
          </div>
        </div>
      </section>

      <p class="workspace-disclaimer">
        服务生成的所有内容均由人工智能模型生成，其生成内容的准确性和完整性无法保证，不能代表律师意见和观点。
      </p>

      <section id="case-workbench" class="workspace-dock">
        <header class="dock-head">
          <div>
            <p class="eyebrow">案件办理进度</p>
            <h2>{{ app.currentTitle }}</h2>
            <p class="muted">输入事实后，系统会整理风险、证据缺口、重庆本地参考和可复核的文书草稿。</p>
          </div>
          <span class="status-pill soft">{{ app.readinessLabel }}</span>
        </header>

        <nav class="assistant-progress" aria-label="案件办理步骤">
          <div
            v-for="step in assistantSteps"
            :key="step.label"
            class="assistant-progress-step"
            :class="{ active: step.active, done: step.done }"
          >
            <span>{{ step.index }}</span>
            <strong>{{ step.label }}</strong>
          </div>
        </nav>

        <div class="content-grid">
          <CaseFormPanel
            :loading="app.loading"
            :user="app.user"
            :workup-result="app.workupResult"
            :error-message="app.errorMessage"
            :success-message="app.successMessage"
            :case-form="app.caseForm"
            :evidence-text="app.evidenceText"
            :document-type="app.documentType"
            :case-type="app.inferCaseType()"
            @update:evidence-text="app.setEvidenceText"
            @update:document-type="app.setDocumentType"
            @analyze="app.analyzeCase"
            @generate-document="app.generateDocument"
          />

          <AnalysisPanel
            :workup-result="app.workupResult"
            :primary-finding="app.primaryFinding"
            :next-best-action="app.nextBestAction"
            :missing-questions="app.missingQuestions"
          />

          <DocumentPanel
            :document-type="app.documentType"
            :document-result="app.documentResult"
            :document-validation="app.documentValidation"
            :format-time="app.formatTime"
            :loading="app.loading"
            @save="app.saveCurrentCase"
          />
        </div>
      </section>
    </main>

    <AuthDialog
      :visible="app.showAuthDialog"
      :mode="app.authMode"
      :loading="app.loading"
      :form="app.authForm"
      @close="app.closeAuthDialog"
      @submit="app.submitAuth"
      @toggle="app.toggleAuthMode"
    />

    <PasswordDialog
      :visible="app.showPasswordDialog"
      :loading="app.loading"
      :form="app.passwordForm"
      @close="app.closePasswordDialog"
      @submit="app.changePassword"
    />

    <ProfileDialog
      :visible="app.showProfileDialog"
      :loading="app.loading"
      :form="app.profileForm"
      @close="app.closeProfileDialog"
      @submit="app.updateProfile"
    />
  </div>
</template>

<script setup>
import { computed, nextTick, proxyRefs, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

import AnalysisPanel from "../components/AnalysisPanel.vue";
import AppSidebar from "../components/AppSidebar.vue";
import AuthDialog from "../components/AuthDialog.vue";
import CaseFormPanel from "../components/CaseFormPanel.vue";
import DocumentPanel from "../components/DocumentPanel.vue";
import PasswordDialog from "../components/PasswordDialog.vue";
import ProfileDialog from "../components/ProfileDialog.vue";
import { useWorkspaceApp } from "../composables/useWorkspaceApp";

const PENDING_HOME_PROMPT_KEY = "lerap_pending_home_prompt";

const route = useRoute();
const router = useRouter();
const app = proxyRefs(useWorkspaceApp());
let bootstrapped = false;

const composerTools = [
  {
    icon: "⌕",
    label: "文件",
    prompt: "请根据我提供的劳动合同、工资流水、考勤记录和聊天记录，整理证据目录与证明目的。",
  },
  {
    icon: "⌾",
    label: "知识",
    prompt: "请结合重庆劳动仲裁常见规则，说明本案可能涉及的法律依据和举证重点。",
  },
  {
    icon: "⚡",
    label: "技能",
    prompt: "请把本案拆成案件分析、赔偿计算、文书生成三个办理步骤。",
  },
  {
    icon: "¥",
    label: "赔偿",
    prompt: "请估算拖欠工资、经济补偿或违法解除赔偿，并说明计算公式。",
  },
];

const assistantPrompt = computed({
  get() {
    return app.caseForm.facts || "";
  },
  set(value) {
    app.caseForm.facts = value;
  },
});

const promptLength = computed(() => assistantPrompt.value.length);

const assistantSteps = computed(() => [
  {
    index: "01",
    label: "案件分析",
    done: Boolean(app.workupResult),
    active: !app.workupResult,
  },
  {
    index: "02",
    label: "赔偿计算",
    done: Boolean(app.workupResult),
    active: false,
  },
  {
    index: "03",
    label: "文书生成",
    done: Boolean(app.documentResult),
    active: Boolean(app.workupResult) && !app.documentResult,
  },
  {
    index: "04",
    label: "完成",
    done: Boolean(app.documentResult && app.activeCaseId),
    active: Boolean(app.documentResult && !app.activeCaseId),
  },
]);

function normalizeCaseId(value) {
  if (Array.isArray(value)) {
    return value[0] || "";
  }
  return value || "";
}

function applyPendingHomePrompt() {
  const prompt = window.sessionStorage.getItem(PENDING_HOME_PROMPT_KEY);
  if (!prompt) {
    return;
  }
  app.caseForm.facts = prompt;
  window.sessionStorage.removeItem(PENDING_HOME_PROMPT_KEY);
}

function applyComposerTool(tool) {
  const current = assistantPrompt.value.trim();
  assistantPrompt.value = current ? `${current}\n\n${tool.prompt}` : tool.prompt;
}

async function submitPrompt() {
  if (!assistantPrompt.value.trim()) {
    return;
  }
  await app.analyzeCase();
  await nextTick();
  scrollToWorkbench();
}

function scrollToWorkbench() {
  document.getElementById("case-workbench")?.scrollIntoView({ behavior: "smooth", block: "start" });
}

function scrollToSidebar() {
  document.getElementById("workspace-history")?.scrollIntoView({ behavior: "smooth", block: "start" });
}

async function hydrateFromRoute() {
  if (!bootstrapped) {
    await app.loadSession();
    applyPendingHomePrompt();
    bootstrapped = true;
  }

  const caseId = normalizeCaseId(route.query.caseId);
  if (caseId && String(app.activeCaseId || "") !== String(caseId)) {
    await app.loadCase(caseId);
  }
}

async function loadCaseAndSyncRoute(caseId) {
  await router.replace({ name: "assistant", query: { caseId } });
  await app.loadCase(caseId);
}

function startNewCase() {
  app.startNewCase();
  void router.replace({ name: "assistant" });
}

watch(
  () => route.query.caseId,
  () => {
    void hydrateFromRoute();
  },
  { immediate: true }
);
</script>
