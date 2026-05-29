<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { fetchCompetitions, getErrorMessage } from '@/api/client'
import FlowSteps from '@/components/FlowSteps.vue'
import type { Competition } from '@/types'
import { useWorkspaceStore } from '@/stores/workspace'

const router = useRouter()
const store = useWorkspaceStore()

const loading = ref(false)
const query = ref('')
const competitions = ref<Competition[]>([])
const selectedId = ref<number | null>(store.selectedCompetition?.id ?? null)

const selected = computed(() => competitions.value.find((c) => c.id === selectedId.value) ?? null)

async function loadCompetitions() {
  loading.value = true
  try {
    const data = await fetchCompetitions(query.value)
    competitions.value = data.items
    if (!selectedId.value && data.items.length) {
      selectedId.value = store.selectedCompetition?.id ?? data.items[0].id
    }
  } catch (error) {
    ElMessage.error(getErrorMessage(error))
  } finally {
    loading.value = false
  }
}

function onRowClick(row: Competition) {
  selectedId.value = row.id
}

function openOfficial(url: string) {
  window.open(url, '_blank')
}

function next() {
  if (!selected.value) {
    ElMessage.warning('请先选择一场比赛')
    return
  }
  store.selectCompetition(selected.value)
  router.push('/intake')
}

onMounted(loadCompetitions)
</script>

<template>
  <div class="page-shell">
    <FlowSteps />

    <div class="page-header">
      <h1>选择比赛</h1>
      <p>搜索并点击表格行选定目标竞赛，右侧可查看详情。</p>
    </div>

    <div class="content-grid">
      <div class="card-panel table-panel">
        <div class="toolbar">
          <el-input
            v-model="query"
            placeholder="搜索名称、ID、类型或官网"
            clearable
            @keyup.enter="loadCompetitions"
            @clear="loadCompetitions"
          >
            <template #append>
              <el-button @click="loadCompetitions">搜索</el-button>
            </template>
          </el-input>
        </div>

        <el-table
          v-loading="loading"
          :data="competitions"
          highlight-current-row
          height="480"
          @row-click="onRowClick"
        >
          <el-table-column prop="id" label="ID" width="70" />
          <el-table-column prop="name" label="名称" min-width="220" show-overflow-tooltip />
          <el-table-column prop="archetype_label" label="类型" width="130" />
          <el-table-column label="官网" min-width="180">
            <template #default="{ row }">
              <a v-if="row.official_url" :href="row.official_url" target="_blank" @click.stop>
                {{ row.official_url }}
              </a>
              <span v-else class="muted">—</span>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div class="card-panel detail-panel">
        <h3>已选比赛</h3>
        <template v-if="selected">
          <p class="comp-name">{{ selected.name }}</p>
          <div class="detail-row"><span>ID</span><strong>{{ selected.id }}</strong></div>
          <div class="detail-row"><span>类型</span><strong>{{ selected.archetype_label }}</strong></div>
          <div class="detail-row"><span>模板</span><strong>{{ selected.archetype }}</strong></div>
          <el-button
            v-if="selected.official_url"
            type="primary"
            plain
            class="full-btn"
            @click="openOfficial(selected.official_url)"
          >
            打开官网
          </el-button>
        </template>
        <el-empty v-else description="请从左侧列表选择比赛" />
      </div>
    </div>

    <div class="action-bar">
      <el-button @click="router.push('/')">返回首页</el-button>
      <el-button type="primary" @click="next">下一步：填写备赛信息</el-button>
    </div>
  </div>
</template>

<style scoped>
.content-grid {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: 16px;
}

.toolbar {
  margin-bottom: 14px;
}

.detail-panel h3 {
  margin: 0 0 14px;
}

.comp-name {
  font-size: 18px;
  font-weight: 700;
  margin: 0 0 16px;
  line-height: 1.5;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid var(--border);
  color: var(--text-secondary);
}

.detail-row strong {
  color: var(--text-primary);
}

.full-btn {
  width: 100%;
  margin-top: 16px;
}

.muted {
  color: var(--text-secondary);
}

@media (max-width: 900px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
}
</style>
