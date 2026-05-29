import type { SkillLevel } from '@/types'

export const SKILL_LEVELS: Record<SkillLevel, string> = {
  beginner: '入门',
  intermediate: '中级',
  experienced: '有经验',
}

export const FLOW_STEPS = [
  { key: 'competitions', title: '选择比赛', path: '/competitions' },
  { key: 'intake', title: '备赛信息', path: '/intake' },
  { key: 'generate', title: '生成备战包', path: '/generate' },
  { key: 'result', title: '查看结果', path: '/result' },
] as const

export const FEATURES = [
  {
    title: '赛题智能解析',
    desc: '结合知识库与章程原文，提炼赛制、评分与技能要求。',
    icon: 'Document',
  },
  {
    title: '分阶段路径',
    desc: '按截止日期与每周投入，生成可执行的备赛里程碑。',
    icon: 'TrendCharts',
  },
  {
    title: '资料精准推荐',
    desc: '官方与 curated 资料优先，减少无效搜索时间。',
    icon: 'Collection',
  },
] as const
