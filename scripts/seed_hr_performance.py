import argparse
import os
import sys
import random
from datetime import date

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from db.session import SessionLocal
from db import base  # noqa: F401
from models.hr_performance_review import HrPerformanceReview
from models.user import User
from utils.security import get_password_hash


DEPARTMENTS = ["Engineering", "Sales", "HR", "Finance", "Operations"]
TRENDS = ["up", "down", "flat"]


def _month_start(d: date) -> date:
    return date(d.year, d.month, 1)


def _random_score():
    return round(random.uniform(55, 96), 1)


def seed_performance(db, business_id: int, review_period: date, create_users: bool, replace: bool):
    existing = (
        db.query(HrPerformanceReview)
        .filter(
            HrPerformanceReview.business_id == business_id,
            HrPerformanceReview.review_period == review_period,
        )
        .count()
    )
    if existing and not replace:
        print(f"[skip] {existing} reviews already exist for business {business_id} in {review_period}.")
        return

    if replace:
        db.query(HrPerformanceReview).filter(
            HrPerformanceReview.business_id == business_id,
            HrPerformanceReview.review_period == review_period,
        ).delete()
        db.commit()

    employees = (
        db.query(User)
        .filter(User.business_id == business_id, User.role == "employee")
        .all()
    )

    if not employees and create_users:
        for i in range(1, 6):
            username = f"employee{i}_b{business_id}"
            email = f"{username}@example.com"
            employee = User(
                username=username,
                full_name=f"Employee {i}",
                email=email,
                hashed_password=get_password_hash("Password123!"),
                role="employee",
                is_active=True,
                department=random.choice(DEPARTMENTS),
                business_id=business_id,
            )
            db.add(employee)
        db.commit()
        employees = (
            db.query(User)
            .filter(User.business_id == business_id, User.role == "employee")
            .all()
        )

    if not employees:
        print("[error] No employees found. Create employees first or run with --create-users.")
        return

    for emp in employees:
        score = _random_score()
        review = HrPerformanceReview(
            business_id=business_id,
            user_id=emp.id,
            review_period=review_period,
            score=score,
            goals_achieved=random.randint(1, 8),
            rating=max(1, min(5, int(round(score / 20)))),
            trend=random.choice(TRENDS),
            metric_quality=random.uniform(60, 95),
            metric_speed=random.uniform(60, 95),
            metric_collaboration=random.uniform(60, 95),
            metric_initiative=random.uniform(60, 95),
            metric_reliability=random.uniform(60, 95),
        )
        db.add(review)

    db.commit()
    print(f"[ok] Seeded performance reviews for {len(employees)} employees in {review_period}.")


def main():
    parser = argparse.ArgumentParser(description="Seed HR performance reviews.")
    parser.add_argument("--business-id", type=int, required=True)
    parser.add_argument("--period", type=str, default=None, help="YYYY-MM-01 or YYYY-MM")
    parser.add_argument("--create-users", action="store_true", help="Create demo employees if none exist.")
    parser.add_argument("--replace", action="store_true", help="Replace existing reviews for this period.")
    args = parser.parse_args()

    if args.period:
        parts = args.period.split("-")
        year = int(parts[0])
        month = int(parts[1])
        review_period = date(year, month, 1)
    else:
        review_period = _month_start(date.today())

    db = SessionLocal()
    try:
        seed_performance(
            db=db,
            business_id=args.business_id,
            review_period=review_period,
            create_users=args.create_users,
            replace=args.replace,
        )
    finally:
        db.close()


if __name__ == "__main__":
    main()
