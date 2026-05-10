<template>
  <div v-if="visible" class="overlay" @click.self="$emit('close')">
    <div class="dialog">
      <div class="section-head">
        <h2>修改密码</h2>
        <button class="icon-button" @click="$emit('close')">×</button>
      </div>

      <div class="form-grid">
        <label class="field span-2">
          <span>当前密码</span>
          <input v-model="form.current_password" type="password" placeholder="输入当前密码" />
        </label>
        <label class="field span-2">
          <span>新密码</span>
          <input v-model="form.new_password" type="password" placeholder="至少 8 位，包含大小写字母和数字" />
        </label>
      </div>

      <div class="button-row top-gap">
        <button class="button primary" :disabled="loading" @click="$emit('submit')">
          {{ loading ? "保存中..." : "保存新密码" }}
        </button>
        <button class="button secondary" @click="$emit('close')">取消</button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  visible: { type: Boolean, default: false },
  loading: { type: Boolean, default: false },
  form: { type: Object, required: true },
});

defineEmits(["close", "submit"]);
</script>
