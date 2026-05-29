<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { fetchHealth, getErrorMessage } from '@/api/client'
import { FEATURES } from '@/constants'
import { useWorkspaceStore } from '@/stores/workspace'

const router = useRouter()
const store = useWorkspaceStore()
const ready = ref(false)
const loading = ref(true)

onMounted(async () => {
  try {
    const health = await fetchHealth()
    ready.value = health.llm_configured
  } catch (error) {
    ready.value = false
    console.error(getErrorMessage(error))
  } finally {
    loading.value = false
  }
})

function start() {
  router.push('/competitions')
}
</script>

<template>
  <div class="page-shell">
    <section class="hero">
      <el-tag effect="dark" type="info" class="hero-tag">面向大学生的 C 端备赛产品</el-tag>
      <h1>3 分钟选对路径，系统化备战学科竞赛</h1>
      <p>
        覆盖教育部 84 项认定竞赛。基于赛题解析、分阶段路径与资料推荐，帮你把备赛从「盲目搜索」变成「可执行计划」。
      </p>
      <div class="hero-actions">
        <el-button type="primary" size="large" :disabled="!ready" @click="start">
          开始规划
        </el-button>
        <el-button size="large" plain @click="router.push('/result')" :disabled="!store.hasResult">
          查看上次结果
        </el-button>
      </div>
      <el-alert
        v-if="!loading && !ready"
        title="后端未配置 LLM_API_KEY，请先在项目根目录配置 .env"
        type="warning"
        show-icon
        :closable="false"
        class="hero-alert"
      />
    </section>

    <section class="feature-grid">
      <div v-for="feature in FEATURES" :key="feature.title" class="card-panel feature-card">
        <el-icon :size="28" class="feature-icon"><component :is="feature.icon" /></el-icon>
        <h3>{{ feature.title }}</h3>
        <p>{{ feature.desc }}</p>
      </div>
    </section>

    <section class="card-panel workflow-card">
      <h2>使用流程</h2>
      <ol>
        <li>从 84 项竞赛中选择目标赛事</li>
        <li>填写截止日期、每周投入时间与个人水平</li>
        <li>一键生成备战包（约 1～4 分钟）</li>
        <li>预览、下载 Markdown / JSON，按阶段执行</li>
      </ol>
    </section>
  </div>
</template>

<style scoped>
.hero-tag {
  margin-bottom: 14px;
}

.hero-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
  flex-wrap: wrap;
}

.hero-alert {
  margin-top: 18px;
  max-width: 720px;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
  margin: 24px 0;
}

.feature-card h3 {
  margin: 12px 0 8px;
  font-size: 18px;
}

.feature-card p {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.6;
  font-size: 14px;
}

.feature-icon {
  color: var(--brand-600);
}

.workflow-card h2 {
  margin: 0 0 12px;
  font-size: 20px;
}

.workflow-card ol {
  margin: 0;
  padding-left: 20px;
  color: #334155;
  line-height: 1.9;
}

@media (max-width: 900px) {
  .feature-grid {
    grid-template-columns: 1fr;
  }
}
</style>
