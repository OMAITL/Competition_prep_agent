<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fetchHealth } from '@/api/client'
import { useWorkspaceStore } from '@/stores/workspace'

const route = useRoute()
const router = useRouter()
const store = useWorkspaceStore()
const llmReady = ref(true)

const navItems = [
  { label: '首页', path: '/' },
  { label: '选择比赛', path: '/competitions' },
  { label: '备赛信息', path: '/intake' },
  { label: '生成', path: '/generate' },
  { label: '结果', path: '/result' },
]

const activePath = computed(() => route.path)

onMounted(async () => {
  try {
    const health = await fetchHealth()
    llmReady.value = health.llm_configured
  } catch {
    llmReady.value = false
  }
})

function go(path: string) {
  router.push(path)
}

function restart() {
  store.resetAll()
  router.push('/')
}
</script>

<template>
  <div class="app-layout">
    <header class="topbar">
      <div class="topbar-inner">
        <div class="brand" @click="go('/')">
          <div class="brand-mark">CP</div>
          <div>
            <div class="brand-title">竞赛备战规划</div>
            <div class="brand-sub">84 项教育部认定学科竞赛</div>
          </div>
        </div>

        <nav class="nav">
          <button
            v-for="item in navItems"
            :key="item.path"
            class="nav-item"
            :class="{ active: activePath === item.path }"
            @click="go(item.path)"
          >
            {{ item.label }}
          </button>
        </nav>

        <div class="topbar-actions">
          <el-tag :type="llmReady ? 'success' : 'danger'" effect="plain" size="small">
            {{ llmReady ? '服务就绪' : '未配置 API' }}
          </el-tag>
          <el-button size="small" @click="restart">重新开始</el-button>
        </div>
      </div>
    </header>

    <main class="main-content">
      <router-view />
    </main>

    <footer class="footer">
      <p>本方案仅供参考，请以官方赛题与章程为准。</p>
    </footer>
  </div>
</template>

<style scoped>
.app-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.topbar {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--border);
}

.topbar-inner {
  max-width: 1180px;
  margin: 0 auto;
  padding: 14px 20px;
  display: flex;
  align-items: center;
  gap: 20px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  min-width: 220px;
}

.brand-mark {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: linear-gradient(135deg, #1e3a5f, #2563eb);
  color: #fff;
  display: grid;
  place-items: center;
  font-weight: 700;
}

.brand-title {
  font-weight: 700;
  font-size: 15px;
}

.brand-sub {
  color: var(--text-secondary);
  font-size: 12px;
}

.nav {
  display: flex;
  gap: 6px;
  flex: 1;
  justify-content: center;
}

.nav-item {
  border: none;
  background: transparent;
  padding: 8px 14px;
  border-radius: 999px;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 14px;
}

.nav-item.active,
.nav-item:hover {
  background: var(--brand-50);
  color: var(--brand-700);
}

.topbar-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.main-content {
  flex: 1;
}

.footer {
  border-top: 1px solid var(--border);
  background: #fff;
  text-align: center;
  color: var(--text-secondary);
  font-size: 13px;
  padding: 18px 20px;
}

.footer p {
  margin: 0;
}

@media (max-width: 900px) {
  .topbar-inner {
    flex-wrap: wrap;
  }

  .nav {
    order: 3;
    width: 100%;
    overflow-x: auto;
    justify-content: flex-start;
  }

  .brand {
    min-width: auto;
  }
}
</style>
