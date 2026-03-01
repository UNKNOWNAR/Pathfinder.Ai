<template>
  <router-view />
</template>

<style>
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

:root {
  --ink:     #111111;
  --bg:      #DEDEDE;
  --surface: #FFFFFF;
  --accent:  #2d8cf0;
  --admin-accent: #ff4757;
  --border:  2px solid var(--ink);
  --shadow:  4px 4px 0 var(--ink);
}

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  min-height: 100vh;
  width: 100%;
  background: var(--bg);
  color: var(--ink);
}

#app {
  width: 100%;
  min-height: 100vh;
}

/* Global Neo-Brutalist Classes */
.page {
  min-height: 100vh;
}

.box {
  background: var(--surface);
  border: var(--border);
  box-shadow: var(--shadow);
}

.brutal-btn {
  padding: 8px 16px;
  background: var(--surface);
  border: var(--border);
  box-shadow: 3px 3px 0 var(--ink);
  font-weight: 900;
  font-size: 13px;
  cursor: pointer;
  transition: transform 0.1s, box-shadow 0.1s;
}

.brutal-btn:active {
  box-shadow: 1px 1px 0 var(--ink);
  transform: translate(2px, 2px);
}

.primary-btn {
  width: 100%;
  padding: 16px;
  background: var(--accent);
  color: white;
  border: var(--border);
  box-shadow: var(--shadow);
  font-weight: 900;
  font-size: 16px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  cursor: pointer;
  transition: box-shadow 0.1s, transform 0.1s;
}

.primary-btn:hover { background: #1b6fc2; }
.primary-btn:active {
  box-shadow: 1px 1px 0 var(--ink);
  transform: translate(3px, 3px);
}
.primary-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
  box-shadow: var(--shadow);
}

.brutal-input {
  padding: 14px;
  border: var(--border);
  background: #f8f8f8;
  font-family: inherit;
  font-size: 15px;
  outline: none;
  transition: background 0.1s, box-shadow 0.1s;
}

.brutal-input:focus {
  background: var(--surface);
  box-shadow: 2px 2px 0 var(--ink);
}

.brutal-textarea {
  resize: vertical;
  min-height: 120px;
}

.status-msg {
  padding: 16px;
  font-weight: 800;
  border: var(--border);
  box-shadow: 2px 2px 0 var(--ink);
  text-align: center;
  background: var(--surface);
}

.error-msg { background: #ff7675; }
.success-msg { background: #55efc4; }

.section-title {
  font-size: 18px;
  font-weight: 900;
  text-transform: uppercase;
  text-decoration: underline;
  text-underline-offset: 4px;
  text-decoration-thickness: 2px;
}
</style>