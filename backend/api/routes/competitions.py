from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from backend.api.models import CompetitionItem, CompetitionListResponse
from backend.api.services import get_competition, list_competitions

router = APIRouter(prefix="/competitions", tags=["competitions"])


@router.get("", response_model=CompetitionListResponse)
def get_competitions(q: str = Query(default="", description="搜索关键词")) -> CompetitionListResponse:
    items = list_competitions(q)
    return CompetitionListResponse(total=len(items), items=items)


@router.get("/{competition_id}", response_model=CompetitionItem)
def get_competition_detail(competition_id: int) -> CompetitionItem:
    item = get_competition(competition_id)
    if not item:
        raise HTTPException(status_code=404, detail="比赛不存在")
    return item
