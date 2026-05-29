<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { marked } from 'marked'
import FlowSteps from '@/components/FlowSteps.vue'
import { useWorkspaceStore } from '@/stores/workspace'

const router = useRouter()
const store = useWorkspaceStore()

const pkg = computed(() => store.package)
const markdown = computed(() => store.job?.markdown ?? '')
const html = computed(() => marked.parse(markdown.value || ''))

const meta = computed(() => pkg.value?.meta)

onMounted(() => {
  if (!store.hasResult) {
    router.replace('/generate')
  }
})

function downloadText(filename: string, content: string, mime: string) {
  const blob = new Blob([content], { type: mime })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

function downloadMd() {
  if (!markdown.value || !meta.value) return
  downloadText(`prep_${meta.value.competition_id}.md`, markdown.value, 'text/markdown')
}

function downloadJson() {
  if (!store.job?.result || !meta.value) return
  downloadText(
    `prep_${meta.value.competition_id}.json`,
    JSON.stringify(store.job.result, null, 2),
    'application/json',
  )
}

function newPlan() {
  store.resetFlow()
  router.push('/competitions')
}
</script>

<template>
  <div class="page-shell">
    <FlowSteps />

    <div class="page-header">
      <h1>备战包结果</h1>
      <p>预览内容或下载 Markdown / JSON 文件，按阶段执行即可。</p>
    </div>

    <el-result
      v-if="meta"
      icon="success"
      :title="meta.competition_name"
      :sub-title="`剩余约 ${meta.weeks_remaining} 周 · 每周 ${meta.weekly_hours} 小时 · 水平 ${meta.skill_level}`"
      class="card-panel result-banner"
    >
      <template #extra>
        <div class="result-actions">
          <el-button type="primary" @click="downloadMd">下载 Markdown</el-button>
          <el-button @click="downloadJson">下载 JSON</el-button>
          <el-button plain @click="newPlan">新建规划</el-button>
        </div>
      </template>
    </el-result>

    <el-tabs type="border-card" class="result-tabs">
      <el-tab-pane label="概览">
        <div v-if="pkg?.competition_analysis" class="overview">
          <h3>赛题摘要</h3>
          <p>{{ pkg.competition_analysis.summary || '—' }}</p>
          <h3>赛制与流程</h3>
          <p>{{ pkg.competition_analysis.format || '—' }}</p>
          <template v-if="pkg.warnings?.length">
            <h3>提示</h3>
            <ul>
              <li v-for="(w, i) in pkg.warnings" :key="i">{{ w }}</li>
            </ul>
          </template>
          <h3>阶段路径</h3>
          <el-timeline>
            <el-timeline-item
              v-for="phase in pkg.prep_plan?.phases || []"
              :key="phase.phase_id"
              :timestamp="phase.week_range"
            >
              阶段 {{ phase.phase_id }}：{{ phase.title }}
            </el-timeline-item>
          </el-timeline>
        </div>
      </el-tab-pane>

      <el-tab-pane label="完整文档">
        <div class="card-panel markdown-body" v-html="html" />
      </el-tab-pane>

      <el-tab-pane label="结构化数据">
        <el-scrollbar height="520px">
          <pre class="json-view">{{ JSON.stringify(store.job?.result, null, 2) }}</pre>
        </el-scrollbar>
      </el-tab-pane>
    </el-tabs>

    <div class="action-bar">
      <el-button @click="router.push('/generate')">返回生成页</el-button>
      <el-button @click="router.push('/intake')">修改备赛信息</el-button>
    </div>
  </div>
</template>

<style scoped>
.result-banner {
  margin-bottom: 16px;
}

.result-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: center;
}

.result-tabs {
  background: #fff;
}

.overview h3 {
  margin: 18px 0 8px;
}

.overview p,
.overview li {
  color: #334155;
  line-height: 1.7;
}

.json-view {
  margin: 0;
  padding: 16px;
  background: #0f172a;
  color: #e2e8f0;
  border-radius: 8px;
  font-size: 12px;
  line-height: 1.6;
  overflow: auto;
}
</style>
