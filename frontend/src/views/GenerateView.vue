<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { createJob, fetchJob, getErrorMessage } from '@/api/client'
import FlowSteps from '@/components/FlowSteps.vue'
import { SKILL_LEVELS } from '@/constants'
import type { JobResponse } from '@/types'
import { useWorkspaceStore } from '@/stores/workspace'

const router = useRouter()
const store = useWorkspaceStore()

const starting = ref(false)
const polling = ref(false)
let timer: number | undefined

const competition = computed(() => store.selectedCompetition)
const intake = computed(() => store.intake)
const job = computed(() => store.job)

const statusTag = computed(() => {
  const status = job.value?.status
  if (status === 'completed') return { type: 'success' as const, text: '已完成' }
  if (status === 'failed') return { type: 'danger' as const, text: '失败' }
  if (status === 'running') return { type: 'warning' as const, text: '生成中' }
  return { type: 'info' as const, text: '待开始' }
})

async function pollJob(jobId: string) {
  polling.value = true
  try {
    const data = await fetchJob(jobId)
    store.updateJob(data)
    if (data.status === 'completed') {
      polling.value = false
      ElMessage.success('备战包生成完成')
      router.push('/result')
      return
    }
    if (data.status === 'failed') {
      polling.value = false
      ElMessage.error(data.error || '生成失败')
      return
    }
    timer = window.setTimeout(() => pollJob(jobId), 2000)
  } catch (error) {
    polling.value = false
    ElMessage.error(getErrorMessage(error))
  }
}

async function startGenerate() {
  if (!competition.value) {
    router.replace('/competitions')
    return
  }
  starting.value = true
  try {
    const created = await createJob(intake.value)
    store.setJob(created.job_id, {
      job_id: created.job_id,
      status: created.status,
      progress_stage: null,
      progress_message: null,
      logs: [],
      error: null,
      result: null,
      markdown: null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    } as JobResponse)
    await pollJob(created.job_id)
  } catch (error) {
    ElMessage.error(getErrorMessage(error))
  } finally {
    starting.value = false
  }
}

onMounted(() => {
  if (!competition.value) {
    router.replace('/competitions')
    return
  }
  if (store.jobId && store.job && ['pending', 'running'].includes(store.job.status)) {
    pollJob(store.jobId)
  }
})

onUnmounted(() => {
  if (timer) window.clearTimeout(timer)
})
</script>

<template>
  <div class="page-shell">
    <FlowSteps />

    <div class="page-header">
      <h1>生成备战包</h1>
      <p>系统将执行 RAG 检索与 Prompt 1→2→3，预计 1～4 分钟。</p>
    </div>

    <div class="card-panel">
      <div class="status-row">
        <h3>任务状态</h3>
        <el-tag :type="statusTag.type">{{ statusTag.text }}</el-tag>
      </div>

      <div class="metric-grid">
        <div class="metric-item">
          <div class="label">比赛</div>
          <div class="value">{{ competition?.name }}</div>
        </div>
        <div class="metric-item">
          <div class="label">截止日期</div>
          <div class="value">{{ intake.deadline }}</div>
        </div>
        <div class="metric-item">
          <div class="label">每周小时</div>
          <div class="value">{{ intake.weekly_hours }} h</div>
        </div>
        <div class="metric-item">
          <div class="label">水平</div>
          <div class="value">{{ SKILL_LEVELS[intake.skill_level] }}</div>
        </div>
      </div>

      <div class="generate-actions">
        <el-button
          type="primary"
          size="large"
          :loading="starting || polling"
          :disabled="polling"
          @click="startGenerate"
        >
          {{ polling ? '生成中…' : '开始生成' }}
        </el-button>
      </div>

      <el-timeline v-if="job?.logs?.length" class="timeline">
        <el-timeline-item
          v-for="(log, index) in job.logs"
          :key="`${log.stage}-${index}`"
          :timestamp="new Date(log.at).toLocaleTimeString()"
        >
          <strong>{{ log.stage }}</strong> — {{ log.message }}
        </el-timeline-item>
      </el-timeline>

      <el-alert
        v-if="job?.error"
        :title="job.error"
        type="error"
        show-icon
        :closable="false"
        class="error-alert"
      />
    </div>

    <div class="action-bar">
      <el-button @click="router.push('/intake')">返回修改信息</el-button>
      <el-button v-if="store.hasResult" @click="router.push('/result')">查看结果</el-button>
    </div>
  </div>
</template>

<style scoped>
.status-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.status-row h3 {
  margin: 0;
}

.generate-actions {
  margin: 20px 0;
}

.timeline {
  margin-top: 12px;
}

.error-alert {
  margin-top: 16px;
}
</style>
