<template>
  <div class="site-shell">
    <header class="site-header">
      <RouterLink class="site-brand" to="/">
        <span class="site-logo">L</span>
        <span>
          <strong>L-ERAP PRO</strong>
          <small>法睿风格首页 · 重庆劳动仲裁</small>
        </span>
      </RouterLink>
      <div class="site-header-actions">
        <button class="site-history-button" type="button" @click="scrollToSection('history')">历史</button>
        <button class="button secondary" type="button" @click="enterWorkspace">进入工作区</button>
      </div>
    </header>

    <main class="site-main">
      <aside class="site-rail" aria-label="快速入口">
        <div class="site-rail-head">
          <p class="section-kicker">Quick Access</p>
          <h2>左侧导航</h2>
        </div>
        <button
          v-for="item in siteRailItems"
          :key="item.title"
          type="button"
          class="site-rail-item"
          @click="handleRailItem(item)"
        >
          <span class="rail-icon">{{ item.icon }}</span>
          <span class="rail-copy">
            <strong>{{ item.title }}</strong>
            <small>{{ item.description }}</small>
          </span>
        </button>
      </aside>

      <section class="site-center">
        <div class="site-hero">
          <p class="section-kicker">Farui-style legal home</p>
          <h1>把案情、类案和文书放进同一个输入框</h1>
          <p>
            浅色留白、左侧导航、中心输入、顶部历史入口。先输入问题，再进入工作区继续整理事实、证据和文书。
          </p>
        </div>

        <section class="site-prompt-card" aria-label="中心输入区">
          <div class="site-prompt-head">
            <div>
              <p class="section-kicker">AI Prompt</p>
              <h2>输入案情、问题或文书要求</h2>
            </div>
            <button class="site-history-button compact" type="button" @click="scrollToSection('history')">
              历史
            </button>
          </div>
          <textarea
            v-model="sitePrompt"
            class="site-prompt"
            placeholder="例如：我在重庆某公司工作两年，最近被拖欠工资并被迫离职，手里有劳动合同、考勤和工资流水。"
          />
          <div class="site-prompt-actions">
            <button class="button primary" type="button" @click="submitHomePrompt">开始分析</button>
            <button class="button secondary" type="button" @click="enterWorkspace">进入工作区</button>
          </div>
          <div class="site-prompt-chips" aria-label="常用提示词">
            <button v-for="prompt in promptPresets" :key="prompt" type="button" @click="applyPrompt(prompt)">
              {{ prompt }}
            </button>
          </div>
        </section>

        <section class="site-signals" aria-label="能力卡片">
          <article v-for="card in siteSignals" :key="card.title" class="site-signal-card">
            <span class="signal-icon">{{ card.icon }}</span>
            <strong>{{ card.title }}</strong>
            <p>{{ card.description }}</p>
          </article>
        </section>
      </section>

      <aside class="site-history" aria-label="历史与入口" id="history">
        <section class="history-panel">
          <div class="site-section-head">
            <div>
              <p class="section-kicker">History</p>
              <h2>最近案件</h2>
            </div>
            <span>{{ recentCases.length }}</span>
          </div>
          <div v-if="recentCases.length" class="history-list">
            <button
              v-for="item in recentCases"
              :key="item.id"
              type="button"
              class="history-item"
              @click="openSavedCase(item.id)"
            >
              <strong>{{ getCaseTitle(item) }}</strong>
              <span>{{ getCaseMeta(item) }}</span>
              <small>{{ getCaseTime(item) || "刚刚" }}</small>
            </button>
          </div>
          <div v-else class="empty-box">
            登录后可在这里看到最近保存的案件，点击后可直接回到工作区继续处理。
          </div>
        </section>

        <section class="history-panel">
          <div class="site-section-head">
            <div>
              <p class="section-kicker">Activity</p>
              <h2>最近动作</h2>
            </div>
            <span>{{ recentActivities.length }}</span>
          </div>
          <div v-if="recentActivities.length" class="history-list compact">
            <div v-for="item in recentActivities" :key="item.id || item.created_at || item.title" class="activity-tile">
              <strong>{{ getActivityTitle(item) }}</strong>
              <span>{{ getActivityMeta(item) }}</span>
            </div>
          </div>
          <div v-else class="empty-box">
            当前没有可展示的历史动作。进入工作区并完成分析或保存后，这里会自动出现记录。
          </div>
        </section>
      </aside>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, proxyRefs, ref } from "vue";
import { RouterLink, useRouter } from "vue-router";

import { useWorkspaceApp } from "../composables/useWorkspaceApp";

const PENDING_HOME_PROMPT_KEY = "lerap_pending_home_prompt";

const router = useRouter();
const app = proxyRefs(useWorkspaceApp());
const sitePrompt = ref("");

const promptPresets = [
  "拖欠工资怎么举证",
  "被辞退怎么申请仲裁",
  "加班费怎么计算",
  "工伤待遇怎么主张",
];

const siteRailItems = [
  {
    icon: "问",
    title: "案情输入",
    description: "把问题写成一句自然语言。",
    prompt: "我在重庆某公司工作，最近被拖欠工资，想申请劳动仲裁。",
  },
  {
    icon: "析",
    title: "风险分析",
    description: "看时效、管辖和证据缺口。",
    prompt: "请帮我分析劳动仲裁的时效、证据缺口和胜诉风险。",
  },
  {
    icon: "文",
    title: "文书草稿",
    description: "生成申请书、清单和补正文案。",
    prompt: "请生成劳动仲裁申请书和证据清单草稿。",
  },
  {
    icon: "案",
    title: "案件工作区",
    description: "进入完整工作台继续处理。",
    action: "workspace",
  },
  {
    icon: "历",
    title: "历史记录",
    description: "快速定位最近的案件。",
    action: "history",
  },
];

const siteSignals = [
  {
    icon: "01",
    title: "类案检索",
    description: "把争议焦点压缩成清晰问题，方便后续进入工作区查证和归纳。",
  },
  {
    icon: "02",
    title: "风险分析",
    description: "输出时效、管辖、证据缺口和下一步动作，避免只看单方结论。",
  },
  {
    icon: "03",
    title: "文书生成",
    description: "生成仲裁申请书、证据清单与补充说明，并保留到工作区继续编辑。",
  },
];

const recentCases = computed(() => (Array.isArray(app.savedCases) ? app.savedCases.slice(0, 3) : []));
const recentActivities = computed(() => (Array.isArray(app.activities) ? app.activities.slice(0, 4) : []));

function getCaseTitle(item) {
  return item?.title?.trim() || "未命名案件";
}

function getCaseMeta(item) {
  return item?.case_type || item?.readiness || "劳动争议";
}

function getCaseTime(item) {
  return app.formatTime(
    item?.updated_at || item?.updatedAt || item?.created_at || item?.createdAt || item?.last_modified_at || ""
  );
}

function getActivityTitle(item) {
  return item?.title || item?.action || item?.name || "案件动作";
}

function getActivityMeta(item) {
  return item?.description || item?.detail || app.formatTime(item?.created_at || item?.createdAt || "");
}

function applyPrompt(prompt) {
  sitePrompt.value = prompt;
}

function handleRailItem(item) {
  if (item.action === "workspace") {
    void enterWorkspace();
    return;
  }
  if (item.action === "history") {
    scrollToSection("history");
    return;
  }
  applyPrompt(item.prompt);
}

function persistPromptForWorkspace() {
  const prompt = sitePrompt.value.trim();
  if (!prompt) {
    return;
  }
  window.sessionStorage.setItem(PENDING_HOME_PROMPT_KEY, prompt);
}

async function submitHomePrompt() {
  persistPromptForWorkspace();
  await enterWorkspace();
}

async function enterWorkspace() {
  persistPromptForWorkspace();
  await router.push({ name: "assistant" });
}

async function openSavedCase(caseId) {
  await router.push({ name: "assistant", query: { caseId } });
}

function syncPromptFromWorkspace() {
  if (app.caseForm.facts) {
    sitePrompt.value = app.caseForm.facts;
  }
}

function scrollToSection(id) {
  document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" });
}

onMounted(async () => {
  await app.loadSession();
  syncPromptFromWorkspace();
});
</script>
