<template>
  <div class="app-shell">
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

    <main class="main-shell">
      <header class="topbar">
        <div>
          <p class="eyebrow">案件助手</p>
          <h2>{{ app.currentTitle }}</h2>
          <p class="muted">输入事实后，系统会整理风险、证据缺口、重庆本地参考和可复核的文书草稿。</p>
        </div>
        <div class="topbar-actions">
          <span class="status-pill soft">{{ app.readinessLabel }}</span>
          <button class="button secondary" :disabled="app.loading" @click="router.push({ name: 'home' })">
            官网
          </button>
          <button class="button secondary" :disabled="app.loading" @click="startNewCase">重置</button>
          <button class="button primary" :disabled="app.loading || !app.canSave" @click="app.saveCurrentCase">
            {{ app.activeCaseId ? "更新案件" : "保存案件" }}
          </button>
        </div>
      </header>

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
import { proxyRefs, watch } from "vue";
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
