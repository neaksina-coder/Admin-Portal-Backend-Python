# api/v1/audit_logs.py
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api import deps
from crud import audit_log as crud_audit_log
from schemas.audit_log import AuditLogListResponse

router = APIRouter()


def _serialize_audit_log(log):
    return {
        "id": log.id,
        "businessId": log.business_id,
        "actorUserId": log.actor_user_id,
        "action": log.action,
        "targetType": log.target_type,
        "targetId": log.target_id,
        "metadata": log.metadata_json,
        "created_at": log.created_at,
    }


@router.get("/", response_model=AuditLogListResponse)
def list_audit_logs(
    businessId: int | None = Query(None),
    actorUserId: int | None = Query(None),
    action: str | None = Query(None),
    startDate: datetime | None = Query(None),
    endDate: datetime | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    logs = crud_audit_log.list_audit_logs(
        db,
        business_id=businessId,
        actor_user_id=actorUserId,
        action=action,
        start_date=startDate,
        end_date=endDate,
        skip=skip,
        limit=limit,
    )
    return {
        "success": True,
        "status_code": 200,
        "message": "Audit logs retrieved successfully",
        "total": len(logs),
        "data": [_serialize_audit_log(log) for log in logs],
    }
