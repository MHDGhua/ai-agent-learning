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
      @load-case="app.loadCase"
      @delete-case="app.deleteCase"
      @import-legacy="app.importLegacyData"
    />

    <main class="main-shell">
      <header class="topbar">
        <div>
          <p class="eyebrow">当前会话</p>
          <h2>{{ app.currentTitle }}</h2>
          <p class="muted">
            API 基址：
            <code>{{ app.apiBaseHint }}</code>
          </p>
        </div>
        <div class="topbar-actions">
          <span class="status-pill soft">{{ app.readinessLabel }}</span>
          <button class="button secondary" :disabled="app.loading" @click="app.startNewCase">重置</button>
          <button class="button primary" :disabled="app.loading || !app.canSave" @click="app.saveCurrentCase">
            {{ app.activeCaseId ? "更新保存" : "保存到服务端" }}
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
import AnalysisPanel from "./components/AnalysisPanel.vue";
import AppSidebar from "./components/AppSidebar.vue";
import AuthDialog from "./components/AuthDialog.vue";
import CaseFormPanel from "./components/CaseFormPanel.vue";
import DocumentPanel from "./components/DocumentPanel.vue";
import PasswordDialog from "./components/PasswordDialog.vue";
import ProfileDialog from "./components/ProfileDialog.vue";
import { useWorkspaceApp } from "./composables/useWorkspaceApp";

const app = useWorkspaceApp();
</script>
