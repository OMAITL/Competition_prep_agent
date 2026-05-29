import { defineStore } from 'pinia'
import type { Competition, IntakeForm, JobResponse, PrepPackage, SkillLevel } from '@/types'

const STORAGE_KEY = 'competition-prep-workspace'

function defaultDeadline(): string {
  const d = new Date()
  d.setDate(d.getDate() + 120)
  return d.toISOString().slice(0, 10)
}

function loadState(): Partial<WorkspaceState> {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? (JSON.parse(raw) as Partial<WorkspaceState>) : {}
  } catch {
    return {}
  }
}

interface WorkspaceState {
  selectedCompetition: Competition | null
  intake: IntakeForm
  jobId: string | null
  job: JobResponse | null
}

export const useWorkspaceStore = defineStore('workspace', {
  state: (): WorkspaceState => {
    const saved = loadState()
    return {
      selectedCompetition: saved.selectedCompetition ?? null,
      intake: saved.intake ?? {
        competition_id: 5,
        deadline: defaultDeadline(),
        weekly_hours: 10,
        skill_level: 'intermediate' as SkillLevel,
        goal: '',
        self_skills: '',
        rules_text: '',
      },
      jobId: saved.jobId ?? null,
      job: saved.job ?? null,
    }
  },
  getters: {
    hasCompetition: (state) => Boolean(state.selectedCompetition),
    hasResult: (state) => Boolean(state.job?.status === 'completed' && state.job.markdown),
    package: (state): PrepPackage | null => (state.job?.result as PrepPackage | null) ?? null,
  },
  actions: {
    persist() {
      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({
          selectedCompetition: this.selectedCompetition,
          intake: this.intake,
          jobId: this.jobId,
          job: this.job,
        }),
      )
    },
    selectCompetition(competition: Competition) {
      this.selectedCompetition = competition
      this.intake.competition_id = competition.id
      this.persist()
    },
    updateIntake(payload: Partial<IntakeForm>) {
      this.intake = { ...this.intake, ...payload }
      this.persist()
    },
    setJob(jobId: string, job: JobResponse | null = null) {
      this.jobId = jobId
      this.job = job
      this.persist()
    },
    updateJob(job: JobResponse) {
      this.job = job
      this.persist()
    },
    resetFlow() {
      this.jobId = null
      this.job = null
      this.persist()
    },
    resetAll() {
      this.selectedCompetition = null
      this.intake = {
        competition_id: 5,
        deadline: defaultDeadline(),
        weekly_hours: 10,
        skill_level: 'intermediate',
        goal: '',
        self_skills: '',
        rules_text: '',
      }
      this.jobId = null
      this.job = null
      this.persist()
    },
  },
})
