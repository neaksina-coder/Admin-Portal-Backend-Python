# api/v1/ai_insights.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api import deps
from crud import ai_insight as crud_ai
from schemas.ai_insight import (
    AIInsightCreate,
    AIInsightResponse,
    AIInsightListResponse,
)

router = APIRouter()


@router.post("/", response_model=AIInsightResponse, status_code=201)
def create_ai_insight(
    insight_in: AIInsightCreate,
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    insight = crud_ai.create_ai_insight(db, insight_in)
    return {
        "success": True,
        "status_code": 201,
        "message": "AI insight created successfully",
        "data": insight,
    }


@router.get("/", response_model=AIInsightListResponse)
def list_ai_insights(
    businessId: int = Query(...),
    limit: int = Query(20, ge=1, le=100),
    type: str | None = Query(None),
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    insights = crud_ai.list_ai_insights(
        db,
        business_id=businessId,
        limit=limit,
        type=type,
    )
    return {
        "success": True,
        "status_code": 200,
        "message": "AI insights retrieved successfully",
        "total": len(insights),
        "data": insights,
    }


@router.get("/{insight_id}", response_model=AIInsightResponse)
def get_ai_insight(
    insight_id: int,
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    insight = crud_ai.get_ai_insight(db, insight_id)
    if not insight:
        raise HTTPException(status_code=404, detail="AI insight not found")
    return {
        "success": True,
        "status_code": 200,
        "message": "AI insight retrieved successfully",
        "data": insight,
    }
