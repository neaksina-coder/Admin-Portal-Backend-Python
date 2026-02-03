# crud/plan.py
from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Optional, List

from models.plan import Plan
from schemas.plan import PlanCreate


def get_plan(db: Session, plan_id: int) -> Optional[Plan]:
    return db.query(Plan).filter(Plan.id == plan_id).first()


def get_plan_by_name(db: Session, plan_name: str) -> Optional[Plan]:
    return db.query(Plan).filter(Plan.plan_name == plan_name).first()


def list_plans(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    plan_name: Optional[str] = None,
) -> List[Plan]:
    query = db.query(Plan)
    if plan_name:
        query = query.filter(Plan.plan_name == plan_name)
    return query.offset(skip).limit(limit).all()


def create_plan(db: Session, plan_in: PlanCreate) -> Plan:
    if get_plan_by_name(db, plan_in.plan_name):
        raise HTTPException(status_code=400, detail="Plan name already exists")
    db_plan = Plan(
        plan_name=plan_in.plan_name,
        price=plan_in.price,
        features=plan_in.features,
    )
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan
