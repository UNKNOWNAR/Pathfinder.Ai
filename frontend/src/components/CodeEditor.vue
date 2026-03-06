<script setup>
import { ref, watch, computed } from 'vue';
import { Codemirror } from 'vue-codemirror';
import { javascript } from '@codemirror/lang-javascript';
import { python } from '@codemirror/lang-python';
import { java } from '@codemirror/lang-java';
import { cpp } from '@codemirror/lang-cpp';

const props = defineProps({
  modelValue: { type: String, default: '' },
  language: { type: String, default: 'python' },
});
const emit = defineEmits(['update:modelValue', 'update:language']);

const code = ref(props.modelValue);

watch(() => props.modelValue, (v) => { code.value = v; });
watch(code, (v) => { emit('update:modelValue', v); });

const selectedLanguage = ref(props.language);
watch(() => props.language, (v) => { selectedLanguage.value = v; });
watch(selectedLanguage, (v) => { emit('update:language', v); });

const extensions = computed(() => {
  if (selectedLanguage.value === 'javascript') return [javascript()];
  if (selectedLanguage.value === 'java') return [java()];
  if (selectedLanguage.value === 'cpp' || selectedLanguage.value === 'c++') return [cpp()];
  return [python()];
});

const languages = [
  { id: 'python', name: 'Python' },
  { id: 'javascript', name: 'JavaScript' },
  { id: 'java', name: 'Java' },
  { id: 'cpp', name: 'C++' }
];
</script>

<template>
  <div class="code-editor-wrap">
    <div class="editor-header">
      <span class="editor-label">CODE</span>
      <select v-model="selectedLanguage" class="lang-select">
        <option v-for="lang in languages" :key="lang.id" :value="lang.id">
          {{ lang.name }}
        </option>
      </select>
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
.lang-select {
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  background: var(--ink);
  color: #fff;
  padding: 4px 10px;
  border: none;
  cursor: pointer;
  appearance: none;
  border-radius: 0;
  outline: none;
}
.lang-select:focus {
  outline: 2px solid var(--accent);
}
.lang-select option {
  background: var(--ink);
  color: #fff;
}
</style>
