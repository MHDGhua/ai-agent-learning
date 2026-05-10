<template>
  <div class="official-home">
    <header class="official-nav">
      <RouterLink class="official-brand" to="/" aria-label="返回首页">
        <span class="official-logo">L</span>
        <span>
          <strong>L-ERAP PRO</strong>
          <small>重庆劳动法专家系统</small>
        </span>
      </RouterLink>

      <button class="official-upgrade" type="button" @click="enterWorkspace">
        <span aria-hidden="true">●</span>
        劳动法能力库已升级！切换至新版
      </button>

      <nav class="official-links" aria-label="官网导航">
        <button type="button" @click="scrollToSection('plans')">购买方案</button>
        <button type="button" @click="scrollToSection('api')">API接入</button>
        <button type="button" @click="scrollToSection('help')">帮助中心</button>
        <RouterLink :to="app.user ? '/assistant' : '/login'">
          {{ app.user ? "进入工作台" : "登录/注册" }}
        </RouterLink>
      </nav>
    </header>

    <main class="official-main">
      <section class="official-hero" aria-labelledby="home-title" aria-label="中心输入区入口">
        <p class="official-kicker">L-ERAP Legal AI</p>
        <h1 id="home-title">重庆劳动法智能体，让仲裁准备更简单</h1>
        <p class="official-subtitle">
          面向劳动者、律师和企业合规团队，把案情梳理、证据审查、赔偿计算与文书草稿整合进一个可信工作流。
        </p>

        <div class="official-actions">
          <button class="official-primary" type="button" @click="enterWorkspace">立即使用</button>
          <button class="official-play" type="button" @click="previewPrompt">
            <span aria-hidden="true">▶</span>
            查看使用示例
          </button>
        </div>
      </section>

      <section class="blueprint-stage" aria-label="法律科技能力库示意图">
        <div class="blueprint-grid">
          <div class="blueprint-emblem" aria-hidden="true">
            <span></span>
            <span></span>
            <span></span>
          </div>

          <article class="blueprint-document">
            <div class="document-toolbar">
              <strong>[ 劳动仲裁助手 ]</strong>
              <span>→</span>
            </div>
            <div class="document-lines">
              <span class="line strong"></span>
              <span class="line strong short"></span>
              <span class="line"></span>
              <span class="line"></span>
              <span class="line medium"></span>
              <span class="line tiny"></span>
            </div>
            <div class="document-section">
              <strong>快速抽取法律场景</strong>
              <span></span>
              <span></span>
            </div>
            <div class="document-section">
              <strong>争议焦点与证据缺口</strong>
              <span></span>
              <span></span>
            </div>
            <div class="document-section">
              <strong>文书草稿与复核建议</strong>
              <span></span>
              <span></span>
            </div>
          </article>

          <aside class="blueprint-book" aria-hidden="true">
            <span></span>
            <small>LAW</small>
          </aside>

          <article class="blueprint-card risk-card">
            <span></span>
            <strong>审查到 8 项高频风险</strong>
            <p>时效、管辖、证据链、请求金额</p>
          </article>

          <article class="blueprint-card statute-card">
            <span></span>
            <strong>根据《劳动合同法》</strong>
            <p>输出可复核依据与重庆本地参考</p>
          </article>

          <article class="blueprint-tag">关于劳动报酬、违法解除、加班费的争议焦点</article>
          <div class="blueprint-pen" aria-hidden="true"></div>
          <div class="blueprint-ticket" aria-hidden="true"></div>
        </div>
      </section>

      <section class="official-capabilities" aria-label="核心能力">
        <article v-for="item in capabilityCards" :key="item.title" class="capability-card">
          <span>{{ item.icon }}</span>
          <strong>{{ item.title }}</strong>
          <p>{{ item.description }}</p>
        </article>
      </section>

      <section class="official-info-grid">
        <article id="plans" class="official-info-card">
          <p class="official-kicker">Plans</p>
          <h2>个人免费整理，团队可扩展持久化案件库</h2>
          <p>当前版本支持真实账户、服务端保存、历史活动记录和案件快照，后续可接入团队席位与审阅流。</p>
        </article>
        <article id="api" class="official-info-card">
          <p class="official-kicker">API</p>
          <h2>保留 API 接入空间</h2>
          <p>后端 FastAPI 已拆分认证、工作区、仲裁分析和文书生成接口，便于接入企业内部系统。</p>
        </article>
        <article id="help" class="official-info-card">
          <p class="official-kicker">Help</p>
          <h2>先输入案情，再进入工作台复核</h2>
          <p>如果不确定怎么描述，可以从拖欠工资、违法解除、加班费、工伤待遇等示例开始。</p>
        </article>
      </section>
    </main>
  </div>
</template>

<script setup>
import { onMounted, proxyRefs } from "vue";
import { RouterLink, useRouter } from "vue-router";

import { useWorkspaceApp } from "../composables/useWorkspaceApp";

const PENDING_HOME_PROMPT_KEY = "lerap_pending_home_prompt";

const router = useRouter();
const app = proxyRefs(useWorkspaceApp());

const samplePrompt =
  "我在重庆某公司工作两年，最近被拖欠工资并被迫离职，手里有劳动合同、考勤和工资流水。";

const capabilityCards = [
  {
    icon: "顾",
    title: "劳动法顾问",
    description: "把自然语言案情转成争议焦点、仲裁请求和下一步行动建议。",
  },
  {
    icon: "审",
    title: "证据审查",
    description: "检查劳动合同、工资流水、考勤、聊天记录等证据是否能支撑请求。",
  },
  {
    icon: "搜",
    title: "重庆本地参考",
    description: "优先组织重庆劳动仲裁常见规则、类案方向与公开参考。",
  },
  {
    icon: "文",
    title: "文书生成",
    description: "生成仲裁申请书、证据清单、调解申请书并保留可编辑草稿。",
  },
  {
    icon: "算",
    title: "赔偿计算",
    description: "围绕工资、经济补偿、违法解除、年休假等请求进行金额估算。",
  },
];

function previewPrompt() {
  window.sessionStorage.setItem(PENDING_HOME_PROMPT_KEY, samplePrompt);
  void enterWorkspace();
}

async function enterWorkspace() {
  await router.push({ name: "assistant" });
}

function scrollToSection(id) {
  document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" });
}

onMounted(async () => {
  await app.loadSession();
});
</script>
