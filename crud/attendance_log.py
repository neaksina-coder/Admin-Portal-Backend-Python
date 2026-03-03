# crud/attendance_log.py
from datetime import datetime, date
from typing import List, Optional

from sqlalchemy.orm import Session

from models.attendance_log import AttendanceLog


def get_attendance_log(db: Session, log_id: int) -> Optional[AttendanceLog]:
    return db.query(AttendanceLog).filter(AttendanceLog.id == log_id).first()


def get_open_log_for_day(
    db: Session, *, business_id: int, user_id: int, work_date: date
) -> Optional[AttendanceLog]:
    return (
        db.query(AttendanceLog)
        .filter(
            AttendanceLog.business_id == business_id,
            AttendanceLog.user_id == user_id,
            AttendanceLog.work_date == work_date,
            AttendanceLog.check_out_at.is_(None),
        )
        .first()
    )


def list_attendance_logs(
    db: Session,
    *,
    business_id: int,
    user_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[AttendanceLog]:
    query = db.query(AttendanceLog).filter(AttendanceLog.business_id == business_id)
    if user_id:
        query = query.filter(AttendanceLog.user_id == user_id)
    if start_date:
        query = query.filter(AttendanceLog.work_date >= start_date)
    if end_date:
        query = query.filter(AttendanceLog.work_date <= end_date)
    return (
        query.order_by(AttendanceLog.work_date.desc(), AttendanceLog.check_in_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_check_in(
    db: Session,
    *,
    business_id: int,
    user_id: int,
    work_date: date,
    check_in_at: datetime,
    note: Optional[str] = None,
) -> AttendanceLog:
    log = AttendanceLog(
        business_id=business_id,
        user_id=user_id,
        work_date=work_date,
        check_in_at=check_in_at,
        status="present",
        note=note,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def check_out(
    db: Session,
    log: AttendanceLog,
    *,
    check_out_at: datetime,
    note: Optional[str] = None,
) -> AttendanceLog:
    log.check_out_at = check_out_at
    if note:
        log.note = note
    db.commit()
    db.refresh(log)
    return log


def update_attendance(
    db: Session, log: AttendanceLog, updates: dict
) -> AttendanceLog:
    for key, value in updates.items():
        setattr(log, key, value)
    db.commit()
    db.refresh(log)
    return log
