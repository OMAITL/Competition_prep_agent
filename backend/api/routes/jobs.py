from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.api.models import CreateJobResponse, GenerateJobRequest, JobResponse, JobStatus
from backend.api.services import job_store, llm_configured, start_job

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=CreateJobResponse, status_code=202)
def create_job(payload: GenerateJobRequest) -> CreateJobResponse:
    if not llm_configured():
        raise HTTPException(status_code=503, detail="服务未配置 LLM_API_KEY")
    job_id = start_job(payload)
    return CreateJobResponse(job_id=job_id, status=JobStatus.pending)


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: str) -> JobResponse:
    job = job_store.to_response(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="任务不存在")
    return job
