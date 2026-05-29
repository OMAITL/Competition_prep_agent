<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import FlowSteps from '@/components/FlowSteps.vue'
import { SKILL_LEVELS } from '@/constants'
import type { SkillLevel } from '@/types'
import { useWorkspaceStore } from '@/stores/workspace'

const router = useRouter()
const store = useWorkspaceStore()

const competition = computed(() => store.selectedCompetition)

onMounted(() => {
  if (!competition.value) {
    ElMessage.warning('请先选择比赛')
    router.replace('/competitions')
  }
})

function onSubmit() {
  if (!store.intake.deadline) {
    ElMessage.warning('请填写截止日期')
    return
  }
  store.persist()
  store.resetFlow()
  router.push('/generate')
}
</script>

<template>
  <div class="page-shell">
    <FlowSteps />

    <div class="page-header">
      <h1>备赛信息</h1>
      <p>填写生成备战包所需的约束条件，带 * 为必填项。</p>
    </div>

    <div v-if="competition" class="card-panel summary-card">
      <div class="summary-title">当前比赛</div>
      <div class="summary-name">{{ competition.name }}</div>
      <div class="summary-meta">ID {{ competition.id }} · {{ competition.archetype_label }}</div>
    </div>

    <el-form label-position="top" class="card-panel form-card" @submit.prevent="onSubmit">
      <h3>基本信息</h3>
      <div class="form-grid">
        <el-form-item label="截止日期 *">
          <el-date-picker
            v-model="store.intake.deadline"
            type="date"
            value-format="YYYY-MM-DD"
            placeholder="选择截止日期"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="每周可投入小时 *">
          <el-input-number v-model="store.intake.weekly_hours" :min="1" :max="60" style="width: 100%" />
        </el-form-item>
        <el-form-item label="当前水平 *">
          <el-select v-model="store.intake.skill_level" style="width: 100%">
            <el-option
              v-for="(label, key) in SKILL_LEVELS"
              :key="key"
              :label="label"
              :value="key as SkillLevel"
            />
          </el-select>
        </el-form-item>
      </div>

      <h3>补充信息（选填）</h3>
      <el-form-item label="备赛目标">
        <el-input v-model="store.intake.goal" placeholder="例如：完成校赛选拔并提交合格论文" />
      </el-form-item>
      <el-form-item label="自评已有技能">
        <el-input v-model="store.intake.self_skills" placeholder="例如：Python, 高等数学" />
      </el-form-item>
      <el-form-item label="赛题 / 章程原文">
        <el-input
          v-model="store.intake.rules_text"
          type="textarea"
          :rows="6"
          placeholder="粘贴官方章程或赛题说明，可提升解析准确度"
        />
      </el-form-item>

      <div class="action-bar">
        <el-button @click="router.push('/competitions')">上一步</el-button>
        <el-button type="primary" native-type="submit">保存并进入生成</el-button>
      </div>
    </el-form>
  </div>
</template>

<style scoped>
.summary-card {
  margin-bottom: 16px;
}

.summary-title {
  color: var(--text-secondary);
  font-size: 13px;
}

.summary-name {
  font-size: 20px;
  font-weight: 700;
  margin-top: 6px;
}

.summary-meta {
  color: var(--text-secondary);
  margin-top: 6px;
}

.form-card h3 {
  margin: 0 0 14px;
  font-size: 16px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

@media (max-width: 900px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
