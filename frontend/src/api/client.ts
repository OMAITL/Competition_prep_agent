import axios from 'axios'
import type {
  Competition,
  CompetitionListResponse,
  CreateJobResponse,
  HealthResponse,
  IntakeForm,
  JobResponse,
} from '@/types'

const http = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

export async function fetchHealth(): Promise<HealthResponse> {
  const { data } = await http.get<HealthResponse>('/health')
  return data
}

export async function fetchCompetitions(q = ''): Promise<CompetitionListResponse> {
  const { data } = await http.get<CompetitionListResponse>('/competitions', { params: { q } })
  return data
}

export async function fetchCompetition(id: number): Promise<Competition> {
  const { data } = await http.get<Competition>(`/competitions/${id}`)
  return data
}

export async function createJob(payload: IntakeForm): Promise<CreateJobResponse> {
  const { data } = await http.post<CreateJobResponse>('/jobs', payload, { timeout: 15000 })
  return data
}

export async function fetchJob(jobId: string): Promise<JobResponse> {
  const { data } = await http.get<JobResponse>(`/jobs/${jobId}`)
  return data
}

export function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail
    if (typeof detail === 'string') return detail
    if (Array.isArray(detail)) return detail.map((d) => d.msg).join('；')
    return error.message
  }
  if (error instanceof Error) return error.message
  return '请求失败，请稍后重试'
}
