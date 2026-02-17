<template>
  <div id="root-app">
    <router-view />
  </div>
</template>

<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600;700&family=IBM+Plex+Sans:wght@400;600;700&display=swap');

:root {
  --bg: #0b0f14;
  --panel-bg: #0f141c;
  --panel-border: #1f2a3a;
  --text-strong: #e6edf3;
  --text-muted: #a7b1c2;
  --text-subtle: #7e8a9a;
  --accent-normal: #00c853;
  --accent-warning: #ff9100;
  --accent-critical: #ff1744;
  --accent-info: #00b0ff;
  --font-sans: 'IBM Plex Sans', system-ui, sans-serif;
  --font-mono: 'IBM Plex Mono', ui-monospace, SFMono-Regular, Menlo, monospace;
}

html,
body {
  margin: 0;
  padding: 0;
  background: var(--bg);
  color: var(--text-strong);
  font-family: var(--font-sans);
  min-height: 100%;
}

#root-app {
  min-height: 100vh;
}

.control-room {
  font-size: 110%;
}

.control-room .dashboard {
  gap: 20px;
}

.control-room .kpi-value {
  font-size: 32px;
}

.control-room .panel-shell {
  padding: 18px;
}

* {
  box-sizing: border-box;
}
</style>
