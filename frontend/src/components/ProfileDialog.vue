<template>
  <div v-if="visible" class="overlay" @click.self="$emit('close')">
    <div class="dialog">
      <div class="section-head">
        <h2>修改资料</h2>
        <button class="icon-button" @click="$emit('close')">×</button>
      </div>

      <div class="form-grid">
        <label class="field span-2">
          <span>姓名</span>
          <input v-model="form.full_name" type="text" placeholder="案件申请人姓名" />
        </label>
        <label class="field span-2">
          <span>身份标签</span>
          <input v-model="form.role" type="text" placeholder="案件申请人" />
        </label>
      </div>

      <div class="button-row top-gap">
        <button class="button primary" :disabled="loading" @click="$emit('submit')">保存资料</button>
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
