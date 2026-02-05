# api/v1/admin_digests.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api import deps
from crud import admin_digest as crud_admin_digest
from schemas.admin_digest import AdminDigestResponse


router = APIRouter()


def _serialize_digest(digest):
    if not digest:
        return None
    return {
        "range": digest.range_type,
        "summaryText": digest.summary_text,
        "topItems": digest.top_items,
        "stats": digest.stats,
        "generatedAt": digest.generated_at,
    }


@router.get("/latest", response_model=AdminDigestResponse)
def get_latest_digest(
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    digest = crud_admin_digest.get_latest_admin_digest(db)
    return {
        "success": True,
        "status_code": 200,
        "message": "Admin digest retrieved successfully",
        "data": _serialize_digest(digest),
    }
