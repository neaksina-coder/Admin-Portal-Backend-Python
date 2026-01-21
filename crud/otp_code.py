# crud/otp_code.py
from datetime import datetime
from sqlalchemy.orm import Session

from models.otp_code import OtpCode


def create_otp_code(db: Session, user_id: int, otp_hash: str, expires_at: datetime):
    otp = OtpCode(
        user_id=user_id,
        otp_hash=otp_hash,
        expires_at=expires_at,
        attempts=0,
        used_at=None,
    )
    db.add(otp)
    db.commit()
    db.refresh(otp)
    return otp


def invalidate_active_otps(db: Session, user_id: int, used_at: datetime):
    db.query(OtpCode).filter(
        OtpCode.user_id == user_id,
        OtpCode.used_at.is_(None),
    ).update({"used_at": used_at})
    db.commit()


def get_latest_active_otp(db: Session, user_id: int):
    return (
        db.query(OtpCode)
        .filter(OtpCode.user_id == user_id, OtpCode.used_at.is_(None))
        .order_by(OtpCode.created_at.desc())
        .first()
    )


def increment_attempts(db: Session, otp_id: int):
    otp = db.query(OtpCode).filter(OtpCode.id == otp_id).first()
    if not otp:
        return None
    otp.attempts += 1
    db.add(otp)
    db.commit()
    db.refresh(otp)
    return otp


def mark_used(db: Session, otp_id: int, used_at: datetime):
    otp = db.query(OtpCode).filter(OtpCode.id == otp_id).first()
    if not otp:
        return None
    otp.used_at = used_at
    db.add(otp)
    db.commit()
    db.refresh(otp)
    return otp
