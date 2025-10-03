<template>
  <div class="title-bar">
    <div class="title-bar-content" data-tauri-drag-region>
      <div class="left-section">
        <div class="window-title">SwarmClone Desktop</div>
        <button
            class="control-button theme-toggle-button"
            @click="toggleTheme">
          <img
              :src="isDarkTheme ? '/sun.svg' : '/moon.svg'"
              :alt="isDarkTheme ? 'LightTheme' : 'DarkTheme'"
              :style="{ filter: isDarkTheme ? 'brightness(0) invert(1)' : 'none' }"
          />
        </button>
      </div>
      <div class="right-section">
        <button
            class="control-button minimize-btn"
            @click="minimizeWindow">
          <img src="/minimize.svg"
               alt="Minimize"
               :style="{ filter: isDarkTheme ? 'brightness(0) invert(1)' : 'none' }"
          />
        </button>
        <button
            class="control-button maximize-btn"
            @click="maximizeWindow">
          <img src="/maximize.svg"
               alt="Maximize"
               :style="{ filter: isDarkTheme ? 'brightness(0) invert(1)' : 'none' }"
          />
        </button>
        <button
            class="control-button close-btn"
            @click="closeWindow">
          <img src="/close.svg"
               alt="关闭"
               :style="{ filter: isDarkTheme ? 'brightness(0) invert(1)' : 'none' }"
          />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { getCurrentWindow } from "@tauri-apps/api/window";
import { onMounted, ref } from "vue";
import { invoke } from "@tauri-apps/api/core";
import { computed } from 'vue'

const emit = defineEmits<{
  (e: 'theme-change', isDark: boolean): void
}>()

const appWindow = getCurrentWindow();
const isDarkTheme = ref(true);

const minimizeWindow = () => {
  appWindow.minimize()
}

const maximizeWindow = () => {
  appWindow.toggleMaximize()
}

const closeWindow = () => {
  appWindow.hide()
}

onMounted(async () => {
  try {
    const savedTheme = await invoke('get_config', { key: 'theme' });
    isDarkTheme.value = savedTheme === 'dark';
    emit('theme-change', isDarkTheme.value);
  } catch (error) {
    console.warn('无法获取主题配置，使用默认深色主题');
  }
});

const toggleTheme = async () => {
  isDarkTheme.value = !isDarkTheme.value;

  // 保存主题配置到后端
  try {
    await invoke('set_config', {
      key: 'theme',
      value: isDarkTheme.value ? 'dark' : 'light'
    });

    emit('theme-change', isDarkTheme.value);
  } catch (error) {
    console.error('保存主题配置失败:', error);
  }
}

const buttonHoverColor = computed(() => {
  return isDarkTheme.value
    ? 'rgba(255, 255, 255, 0.1)'
    : 'rgba(0, 0, 0, 0.1)'
})

const buttonActiveColor = computed(() => {
  return isDarkTheme.value
    ? 'rgba(255, 255, 255, 0.2)'
    : 'rgba(0, 0, 0, 0.2)'
})

</script>

<style scoped>
.title-bar {
  height: 40px;
  display: flex;
  align-items: center;
  user-select: none;
  border-radius: 8px 8px 0 0;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  margin: 0;
  padding: 0;
}

.title-bar-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  height: 100%;
  -webkit-app-region: drag;
}

.left-section {
  height: 100%;
  display: flex;
  align-items: center;
  flex-grow: 1;
  margin-left: 20px;
  -webkit-app-region: drag;
}

.window-title {
  font-size: 14px;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  -webkit-app-region: drag;
}

.right-section {
  display: flex;
  gap: 4px;
  height: 100%;
  /* 控制按钮区域不参与拖拽 */
  -webkit-app-region: no-drag;
}

.control-button {
  width: 40px;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  border-radius: 4px;
}

.control-button img {
  width: 16px;
  height: 16px;
}

.control-button:hover {
  background-color: v-bind(buttonHoverColor);
}

.control-button:active {
  background-color: v-bind(buttonActiveColor);
}

.close-btn:hover {
  background-color: #e81123 !important;
}
</style>