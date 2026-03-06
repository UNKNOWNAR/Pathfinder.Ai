<script setup>
import { ref, onUnmounted } from 'vue';

const props = defineProps({
  modelValue: { type: String, default: '' },
});
const emit = defineEmits(['update:modelValue']);

const isListening = ref(false);
const supported = ref(!!window.SpeechRecognition || !!window.webkitSpeechRecognition);
const errorMsg = ref('');

let recognition = null;

function start() {
  if (!supported.value) {
    errorMsg.value = 'Speech recognition is not supported in this browser.';
    return;
  }
  errorMsg.value = '';

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  recognition = new SpeechRecognition();
  recognition.continuous = true;
  recognition.interimResults = true;
  recognition.lang = 'en-US';

  let finalTranscript = props.modelValue || '';

  recognition.onresult = (event) => {
    let interim = '';
    for (let i = event.resultIndex; i < event.results.length; i++) {
      if (event.results[i].isFinal) {
        finalTranscript += event.results[i][0].transcript + ' ';
      } else {
        interim += event.results[i][0].transcript;
      }
    }
    emit('update:modelValue', finalTranscript + interim);
  };

  recognition.onerror = (event) => {
    if (event.error !== 'aborted') {
      if (event.error === 'network') {
        errorMsg.value = 'Speech recognition network error. Please type your answer below instead.';
      } else {
        errorMsg.value = `Speech error: ${event.error}`;
      }
    }
    isListening.value = false;
  };

  recognition.onend = () => {
    isListening.value = false;
  };

  recognition.start();
  isListening.value = true;
}

function stop() {
  if (recognition) {
    recognition.stop();
    recognition = null;
  }
  isListening.value = false;
}

function toggle() {
  if (isListening.value) {
    stop();
  } else {
    start();
  }
}

onUnmounted(() => stop());
</script>

<template>
  <div class="voice-input">
    <button class="voice-btn" :class="{ recording: isListening }" @click="toggle" :disabled="!supported">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
        <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
        <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
        <line x1="12" y1="19" x2="12" y2="23"/>
        <line x1="8" y1="23" x2="16" y2="23"/>
      </svg>
      {{ isListening ? 'STOP' : 'SPEAK' }}
    </button>
    <span v-if="isListening" class="pulse-dot"></span>
    <p v-if="errorMsg" class="voice-error">{{ errorMsg }}</p>
    <div class="transcript-box">
      <span class="transcript-label">TRANSCRIPT / TEXT INPUT</span>
      <textarea
        class="transcript-text"
        :value="modelValue"
        @input="$emit('update:modelValue', $event.target.value)"
        placeholder="Use microphone or type your answer..."
      ></textarea>
    </div>
  </div>
</template>

<style scoped>
.voice-input {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.voice-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: var(--surface);
  border: 2px solid var(--ink);
  box-shadow: 3px 3px 0 var(--ink);
  font-weight: 800;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  cursor: pointer;
  color: var(--ink);
  transition: box-shadow 0.1s, transform 0.1s;
  align-self: flex-start;
}
.voice-btn:hover { background: #f5f5f5; }
.voice-btn:active { box-shadow: 1px 1px 0 var(--ink); transform: translate(2px, 2px); }
.voice-btn.recording {
  background: #ef4444;
  color: #fff;
  animation: pulse-bg 1.2s ease-in-out infinite;
}
@keyframes pulse-bg {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.75; }
}
.pulse-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #ef4444;
  animation: pulse-bg 1s infinite;
  align-self: flex-start;
}
.voice-error {
  font-size: 12px;
  font-weight: 700;
  color: #ef4444;
}
.transcript-box {
  border: 2px solid var(--ink);
  box-shadow: 3px 3px 0 var(--ink);
  padding: 14px 18px;
  background: #fafafa;
}
.transcript-label {
  font-size: 10px;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  opacity: 0.5;
  display: block;
  margin-bottom: 6px;
}
.transcript-text {
  font-size: 14px;
  font-weight: 600;
  line-height: 1.6;
  width: 100%;
  min-height: 100px;
  resize: vertical;
  background: transparent;
  border: none;
  outline: none;
  font-family: inherit;
}
</style>
