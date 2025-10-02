<template>
  <n-config-provider :theme="theme">
    <div class="container">
      <TitleBar @theme-change="handleThemeChange"/>
      <div class="content">
        111
        <n-button type="info">Default</n-button>
      </div>
    </div>
    <n-global-style />
  </n-config-provider>
</template>

<script setup lang="ts">
import TitleBar from "./componets/TitleBar.vue";
import { GlobalTheme, darkTheme } from "naive-ui";
import { ref, onMounted } from "vue";
import { invoke } from '@tauri-apps/api/core';

const theme = ref<GlobalTheme | null>(null);

const handleThemeChange = (isDark: boolean) => {
  theme.value = isDark ? darkTheme : null;
};

onMounted(async () => {
  try {
  // 从配置加载主题
    const savedTheme = await invoke('get_config', { key: 'theme' });
    theme.value = savedTheme === 'dark' ? darkTheme : null;
  } catch (error) {
    console.warn('无法获取主题配置，使用默认主题');
  }
});
</script>

<style scoped>
.container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  border-radius: 8px;
  overflow: hidden;
  background: transparent;
  margin: 0;
  padding: 0;
}

.content {
  flex: 1;
  padding: 20px;
  overflow: auto;
}
</style>
