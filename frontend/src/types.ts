export type SkillLevel = 'beginner' | 'intermediate' | 'experienced'

export interface Competition {
  id: number
  name: string
  official_url: string | null
  archetype: string
  archetype_label: string
}

export interface CompetitionListResponse {
  total: number
  items: Competition[]
}

export interface IntakeForm {
  competition_id: number
  deadline: string
  weekly_hours: number
  skill_level: SkillLevel
  goal: string
  self_skills: string
  rules_text: string
}

export type JobStatus = 'pending' | 'running' | 'completed' | 'failed'

export interface ProgressLog {
  stage: string
  message: string
  at: string
}

export interface JobResponse {
  job_id: string
  status: JobStatus
  progress_stage: string | null
  progress_message: string | null
  logs: ProgressLog[]
  error: string | null
  result: Record<string, unknown> | null
  markdown: string | null
  created_at: string
  updated_at: string
}

export interface CreateJobResponse {
  job_id: string
  status: JobStatus
}

export interface HealthResponse {
  status: string
  llm_configured: boolean
}

export interface PrepPackage {
  meta: {
    competition_name: string
    competition_id: number
    deadline: string
    weeks_remaining: number
    weekly_hours: number
    skill_level: string
  }
  warnings?: string[]
  competition_analysis?: {
    summary?: string
    format?: string
    scoring?: string[]
    deliverables?: string[]
  }
  prep_plan?: {
    phases?: Array<{
      phase_id: number
      title: string
      week_range: string
      goals?: string[]
      acceptance_criteria?: string[]
    }>
  }
  resources?: Array<{
    title: string
    url?: string
    priority?: string
    reason?: string
    verified?: boolean
  }>
  submission_checklist?: Array<{
    item: string
    due_phase_id: number
    tips?: string
  }>
}
