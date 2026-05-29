from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class SkillLevel(str, Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    experienced = "experienced"


class CompetitionItem(BaseModel):
    id: int
    name: str
    official_url: str | None = None
    archetype: str
    archetype_label: str


class CompetitionListResponse(BaseModel):
    total: int
    items: list[CompetitionItem]


class GenerateJobRequest(BaseModel):
    competition_id: int = Field(ge=1)
    deadline: str = Field(description="YYYY-MM-DD")
    weekly_hours: int = Field(ge=1, le=60, default=10)
    skill_level: SkillLevel = SkillLevel.intermediate
    goal: str = ""
    self_skills: str = ""
    rules_text: str = ""
    track: str = ""
    no_rag: bool = False


class JobStatus(str, Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"


class ProgressLog(BaseModel):
    stage: str
    message: str
    at: datetime


class JobResponse(BaseModel):
    job_id: str
    status: JobStatus
    progress_stage: str | None = None
    progress_message: str | None = None
    logs: list[ProgressLog] = Field(default_factory=list)
    error: str | None = None
    result: dict[str, Any] | None = None
    markdown: str | None = None
    created_at: datetime
    updated_at: datetime


class CreateJobResponse(BaseModel):
    job_id: str
    status: JobStatus


class HealthResponse(BaseModel):
    status: str
    llm_configured: bool
