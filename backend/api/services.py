from __future__ import annotations

import os
import sys
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from generate_prep import (  # noqa: E402
    PrepGenerationOptions,
    generate_prep_package,
    load_catalog,
)

from backend.api.models import CompetitionItem, GenerateJobRequest, JobResponse, JobStatus, ProgressLog

load_dotenv(ROOT / ".env")

ARCHETYPE_LABELS = {
    "algorithm_programming": "算法编程",
    "math_modeling": "数学建模",
    "innovation_entrepreneurship": "创新创业",
    "design_creative": "设计创意",
    "medical_life": "医学生命",
    "robotics_engineering": "机器人工程",
    "business_simulation": "企业经营沙盘",
    "general_stem": "综合理工",
    "language_humanities": "语言人文",
    "electronics_embedded": "电子嵌入式",
    "physics_chemistry": "物理化学",
    "mechanical_structure": "机械结构",
    "ai_data": "人工智能与数据",
}


def archetype_label(archetype: str) -> str:
    return ARCHETYPE_LABELS.get(archetype, archetype)


def llm_configured() -> bool:
    return bool(os.getenv("LLM_API_KEY"))


def list_competitions(query: str = "") -> list[CompetitionItem]:
    q = query.strip().lower()
    items: list[CompetitionItem] = []
    for c in load_catalog():
        if q:
            haystack = " ".join(
                [
                    str(c.get("id", "")),
                    c.get("name", ""),
                    c.get("archetype", ""),
                    c.get("official_url", "") or "",
                ]
            ).lower()
            if q not in haystack:
                continue
        items.append(
            CompetitionItem(
                id=c["id"],
                name=c["name"],
                official_url=c.get("official_url") or None,
                archetype=c["archetype"],
                archetype_label=archetype_label(c["archetype"]),
            )
        )
    return items


def get_competition(competition_id: int) -> CompetitionItem | None:
    for item in list_competitions():
        if item.id == competition_id:
            return item
    return None


class JobStore:
    def __init__(self) -> None:
        self._jobs: dict[str, dict] = {}
        self._lock = threading.Lock()

    def create(self, payload: GenerateJobRequest) -> str:
        job_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        with self._lock:
            self._jobs[job_id] = {
                "job_id": job_id,
                "status": JobStatus.pending,
                "progress_stage": None,
                "progress_message": None,
                "logs": [],
                "error": None,
                "result": None,
                "markdown": None,
                "payload": payload.model_dump(),
                "created_at": now,
                "updated_at": now,
            }
        return job_id

    def to_response(self, job_id: str) -> JobResponse | None:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return None
            logs = [ProgressLog(**log) for log in job["logs"]]
            return JobResponse(
                job_id=job["job_id"],
                status=job["status"],
                progress_stage=job["progress_stage"],
                progress_message=job["progress_message"],
                logs=logs,
                error=job["error"],
                result=job["result"],
                markdown=job["markdown"],
                created_at=job["created_at"],
                updated_at=job["updated_at"],
            )

    def _update(self, job_id: str, **fields) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return
            job.update(fields)
            job["updated_at"] = datetime.now(timezone.utc)

    def append_log(self, job_id: str, stage: str, message: str) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return
            job["logs"].append(
                {
                    "stage": stage,
                    "message": message,
                    "at": datetime.now(timezone.utc),
                }
            )
            job["progress_stage"] = stage
            job["progress_message"] = message
            job["updated_at"] = datetime.now(timezone.utc)


job_store = JobStore()


def _run_job(job_id: str, payload: GenerateJobRequest) -> None:
    job_store._update(job_id, status=JobStatus.running)

    def progress(stage: str, message: str) -> None:
        job_store.append_log(job_id, stage, message)

    try:
        options = PrepGenerationOptions(
            competition_id=payload.competition_id,
            deadline=payload.deadline,
            weekly_hours=payload.weekly_hours,
            skill_level=payload.skill_level.value,
            goal=payload.goal,
            self_skills=payload.self_skills,
            rules_text=payload.rules_text,
            track=payload.track,
            no_rag=payload.no_rag,
        )
        pkg, md = generate_prep_package(options, progress=progress)
        job_store._update(
            job_id,
            status=JobStatus.completed,
            result=pkg,
            markdown=md,
            error=None,
        )
    except Exception as exc:
        job_store._update(
            job_id,
            status=JobStatus.failed,
            error=str(exc),
        )


def start_job(payload: GenerateJobRequest) -> str:
    job_id = job_store.create(payload)
    thread = threading.Thread(target=_run_job, args=(job_id, payload), daemon=True)
    thread.start()
    return job_id
