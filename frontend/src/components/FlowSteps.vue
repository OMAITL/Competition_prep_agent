<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { FLOW_STEPS } from '@/constants'

const route = useRoute()

const activeIndex = computed(() => {
  const idx = FLOW_STEPS.findIndex((step) => step.path === route.path)
  return idx >= 0 ? idx : 0
})
</script>

<template>
  <div class="flow-steps card-panel">
    <el-steps :active="activeIndex" align-center finish-status="success">
      <el-step v-for="step in FLOW_STEPS" :key="step.key" :title="step.title" />
    </el-steps>
  </div>
</template>

<style scoped>
.flow-steps {
  margin-bottom: 20px;
}
</style>
