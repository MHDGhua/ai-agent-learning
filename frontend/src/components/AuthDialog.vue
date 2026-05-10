<template>
  <div v-if="visible" class="overlay" @click.self="$emit('close')">
    <div class="dialog">
      <div class="section-head">
        <h2>{{ mode === "register" ? "注册并登录" : "登录账户" }}</h2>
        <button class="icon-button" @click="$emit('close')">×</button>
      </div>

      <div class="form-grid">
        <label v-if="mode === 'register'" class="field span-2">
          <span>姓名</span>
          <input v-model="form.full_name" type="text" placeholder="案件申请人姓名" />
        </label>

        <label v-if="mode === 'register'" class="field">
          <span>身份</span>
          <input v-model="form.role" type="text" placeholder="案件申请人" />
        </label>

        <label class="field" :class="{ 'span-2': mode === 'login' }">
          <span>邮箱</span>
          <input v-model="form.email" type="email" placeholder="name@example.com" />
        </label>

        <label class="field span-2">
          <span>密码</span>
          <input v-model="form.password" type="password" placeholder="至少 8 位，包含大小写字母和数字" />
        </label>
      </div>

      <div class="button-row top-gap">
        <button class="button primary" :disabled="loading" @click="$emit('submit')">
          {{ loading ? "处理中..." : mode === "register" ? "创建账户" : "登录" }}
        </button>
        <button class="button secondary" @click="$emit('toggle')">
          {{ mode === "register" ? "切换到登录" : "没有账户？去注册" }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  visible: { type: Boolean, default: false },
  mode: { type: String, default: "login" },
  loading: { type: Boolean, default: false },
  form: { type: Object, required: true },
});

defineEmits(["close", "submit", "toggle"]);
</script>
