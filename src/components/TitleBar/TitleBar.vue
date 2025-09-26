<script setup lang="ts">
import "./TitleBar.less"
import { Window } from '@tauri-apps/api/window'
import { useThemeVars } from 'naive-ui'
import { debug } from '@tauri-apps/plugin-log'

const themeVars = useThemeVars()
const window = Window.getCurrent()

const minimize = () => {
  debug('Window Minimized!')
  window.minimize()
}

const maximize =  () => {
  debug('Window Maximized!')
  window.toggleMaximize()
}

const close = () => {
  debug('Window Closed!')
  window.close()
}
</script>

<template>
<div class="title_bar" :style="{ background: `linear-gradient(90deg, ${themeVars.infoColor})` }">
  <div class="title_bar_text" data-tauri-drag-region>
    SwarmClone Desktop
  </div>
  <div class="title_bar_buttons">
    <n-button round class="title_bar_button" id="minimize_button" @click="minimize">
      <img src="/titlebar/minimize.svg" alt="Minimize">
    </n-button>
    <n-button round class="title_bar_button" id="maximize_button" @click="maximize">
      <img src="/titlebar/maximize.svg" alt="Maximize">
    </n-button>
    <n-button round class="title_bar_button" id="close_button" @click="close">
      <img src="/titlebar/close.svg" alt="Close">
    </n-button>
  </div>
</div>
</template>
