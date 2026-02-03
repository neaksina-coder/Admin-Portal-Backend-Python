# api/v1/plans.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api import deps
from crud import plan as crud_plan
from schemas.plan import PlanCreate, PlanResponse, PlanListResponse

router = APIRouter()


@router.post("/", response_model=PlanResponse, status_code=201)
def create_plan(
    plan_in: PlanCreate,
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    plan = crud_plan.create_plan(db, plan_in)
    return {
        "success": True,
        "status_code": 201,
        "message": "Plan created successfully",
        "data": plan,
    }


@router.get("/", response_model=PlanListResponse)
def list_plans(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    planName: str | None = Query(None),
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    plans = crud_plan.list_plans(
        db,
        skip=skip,
        limit=limit,
        plan_name=planName,
    )
    return {
        "success": True,
        "status_code": 200,
        "message": "Plans retrieved successfully",
        "total": len(plans),
        "data": plans,
    }


@router.get("/{plan_id}", response_model=PlanResponse)
def get_plan(
    plan_id: int,
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    plan = crud_plan.get_plan(db, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return {
        "success": True,
        "status_code": 200,
        "message": "Plan retrieved successfully",
        "data": plan,
    }
