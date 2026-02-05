# crud/admin_digest.py
from sqlalchemy.orm import Session

from models.admin_digest import AdminDigest


def create_admin_digest(
    db: Session,
    *,
    range_type: str,
    summary_text: str,
    top_items: list,
    stats: dict,
    generated_by: str = "system",
) -> AdminDigest:
    digest = AdminDigest(
        range_type=range_type,
        summary_text=summary_text,
        top_items=top_items,
        stats=stats,
        generated_by=generated_by,
    )
    db.add(digest)
    db.commit()
    db.refresh(digest)
    return digest


def get_latest_admin_digest(db: Session) -> AdminDigest | None:
    return db.query(AdminDigest).order_by(AdminDigest.generated_at.desc()).first()
