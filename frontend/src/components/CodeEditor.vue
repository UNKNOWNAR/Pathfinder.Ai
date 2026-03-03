<script setup>
import { ref, watch } from 'vue';
import { Codemirror } from 'vue-codemirror';
import { javascript } from '@codemirror/lang-javascript';
import { python } from '@codemirror/lang-python';

const props = defineProps({
  modelValue: { type: String, default: '' },
  language: { type: String, default: 'python' },
});
const emit = defineEmits(['update:modelValue']);

const code = ref(props.modelValue);

watch(() => props.modelValue, (v) => { code.value = v; });
watch(code, (v) => { emit('update:modelValue', v); });

const langExtension = props.language === 'javascript' ? javascript() : python();
const extensions = [langExtension];
</script>

<template>
  <div class="code-editor-wrap">
    <div class="editor-header">
      <span class="editor-label">CODE</span>
      <span class="editor-lang">{{ language.toUpperCase() }}</span>
    </div>
    <Codemirror
      v-model="code"
      :extensions="extensions"
      :style="{ fontSize: '14px' }"
      placeholder="Write your code here..."
      :tab-size="4"
    />
  </div>
</template>

<style scoped>
.code-editor-wrap {
  border: 2px solid var(--ink);
  box-shadow: 3px 3px 0 var(--ink);
  background: #fff;
  overflow: hidden;
}
.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 14px;
  border-bottom: 2px solid var(--ink);
  background: #f5f5f5;
}
.editor-label {
  font-size: 10px;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  opacity: 0.6;
}
.editor-lang {
  font-size: 10px;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  background: var(--ink);
  color: #fff;
  padding: 2px 8px;
}
</style>
