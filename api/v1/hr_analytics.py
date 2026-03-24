# api/v1/hr_analytics.py
from datetime import date, timedelta
import csv
import io

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from api import deps
from models.hr_budget_category import HrBudgetCategory
from models.hr_budget_month import HrBudgetMonth
from models.hr_budget_plan import HrBudgetPlan
from models.hr_employee_event import HrEmployeeEvent
from models.hr_headcount_snapshot import HrHeadcountSnapshot
from models.hr_hiring_pipeline import HrHiringPipeline
from models.hr_hiring_position import HrHiringPosition
from models.hr_performance_review import HrPerformanceReview
from models.payslip import Payslip
from models.pay_period import PayPeriod
from models.business import Business
from models.user import User

router = APIRouter()


def _require_hr_admin(current_user: User = Depends(deps.require_roles(["customer_owner", "hr_admin"]))):
    return current_user


def _month_label(d: date) -> str:
    return d.strftime("%b")

def _add_months(d: date, delta: int) -> date:
    month = d.month - 1 + delta
    year = d.year + month // 12
    month = month % 12 + 1
    return date(year, month, 1)

def _csv_response(filename: str, rows: list[list[object]]) -> StreamingResponse:
    output = io.StringIO()
    writer = csv.writer(output)
    for row in rows:
        writer.writerow(row)
    output.seek(0)
    headers = {
        "Content-Disposition": f"attachment; filename=\"{filename}\"",
    }
    return StreamingResponse(output, media_type="text/csv", headers=headers)


def _build_analytics(db: Session, business_id: int) -> dict:
    today = date.today()

    # ---- Payroll analytics ----
    last_period = (
        db.query(PayPeriod)
        .filter(PayPeriod.business_id == business_id)
        .order_by(PayPeriod.period_end.desc())
        .first()
    )

    last_period_payslips = []
    if last_period:
        last_period_payslips = (
            db.query(Payslip, User)
            .join(User, User.id == Payslip.user_id)
            .filter(
                Payslip.business_id == business_id,
                Payslip.pay_period_id == last_period.id,
            )
            .all()
        )

    gross_pay = sum(float(p.gross_pay) for p, _ in last_period_payslips) if last_period_payslips else 0.0
    net_pay = sum(float(p.net_pay) for p, _ in last_period_payslips) if last_period_payslips else 0.0
    deductions = sum(float(p.deductions) for p, _ in last_period_payslips) if last_period_payslips else 0.0
    employees_paid = len({p.user_id for p, _ in last_period_payslips}) if last_period_payslips else 0

    # Trend: last 6 pay periods
    periods = (
        db.query(PayPeriod)
        .filter(PayPeriod.business_id == business_id)
        .order_by(PayPeriod.period_end.desc())
        .limit(6)
        .all()
    )
    periods = list(reversed(periods))
    trend_labels = [_month_label(p.period_end) for p in periods]
    trend_gross = []
    trend_net = []
    for p in periods:
        sums = (
            db.query(
                func.coalesce(func.sum(Payslip.gross_pay), 0),
                func.coalesce(func.sum(Payslip.net_pay), 0),
            )
            .filter(Payslip.business_id == business_id, Payslip.pay_period_id == p.id)
            .first()
        )
        trend_gross.append(float(sums[0] or 0))
        trend_net.append(float(sums[1] or 0))

    # Payroll split by department (last period)
    payroll_split = (
        db.query(
            func.coalesce(User.department, "Unassigned").label("dept"),
            func.coalesce(func.sum(Payslip.net_pay), 0).label("total"),
        )
        .join(User, User.id == Payslip.user_id)
        .filter(
            Payslip.business_id == business_id,
            Payslip.pay_period_id == (last_period.id if last_period else -1),
        )
        .group_by("dept")
        .order_by(func.coalesce(func.sum(Payslip.net_pay), 0).desc())
        .all()
    )
    split_labels = [row.dept for row in payroll_split]
    split_series = [float(row.total) for row in payroll_split]

    breakdown_rows = [
        {
            "employeeId": user.id,
            "name": user.full_name or user.username,
            "department": user.department or "Unassigned",
            "grossPay": float(p.gross_pay),
            "deductions": float(p.deductions),
            "netPay": float(p.net_pay),
            "status": p.status,
        }
        for p, user in last_period_payslips
    ]

    # ---- Performance ----
    latest_period = (
        db.query(func.max(HrPerformanceReview.review_period))
        .filter(HrPerformanceReview.business_id == business_id)
        .scalar()
    )

    performance_rows = []
    if latest_period:
        performance_rows = (
            db.query(HrPerformanceReview, User)
            .join(User, User.id == HrPerformanceReview.user_id)
            .filter(
                HrPerformanceReview.business_id == business_id,
                HrPerformanceReview.review_period == latest_period,
            )
            .all()
        )

    avg_score = (
        float(
            db.query(func.coalesce(func.avg(HrPerformanceReview.score), 0))
            .filter(
                HrPerformanceReview.business_id == business_id,
                HrPerformanceReview.review_period == latest_period,
            )
            .scalar()
            or 0
        )
        if latest_period
        else 0
    )
    goals_achieved = (
        int(
            db.query(func.coalesce(func.sum(HrPerformanceReview.goals_achieved), 0))
            .filter(
                HrPerformanceReview.business_id == business_id,
                HrPerformanceReview.review_period == latest_period,
            )
            .scalar()
            or 0
        )
        if latest_period
        else 0
    )
    reviews_completed = int(
        db.query(func.count(HrPerformanceReview.id))
        .filter(
            HrPerformanceReview.business_id == business_id,
            HrPerformanceReview.review_period >= (today - timedelta(days=365)),
        )
        .scalar()
        or 0
    )
    under_performers = (
        int(
            db.query(func.count(HrPerformanceReview.id))
            .filter(
                HrPerformanceReview.business_id == business_id,
                HrPerformanceReview.review_period == latest_period,
                HrPerformanceReview.score < 60,
            )
            .scalar()
            or 0
        )
        if latest_period
        else 0
    )

    # Score bands
    band_counts = {"0-60": 0, "60-75": 0, "75-85": 0, "85-100": 0}
    for review, _user in performance_rows:
        s = float(review.score or 0)
        if s < 60:
            band_counts["0-60"] += 1
        elif s < 75:
            band_counts["60-75"] += 1
        elif s < 85:
            band_counts["75-85"] += 1
        else:
            band_counts["85-100"] += 1

    # Radar by department (avg metrics)
    radar_rows = (
        db.query(
            func.coalesce(User.department, "Unassigned").label("dept"),
            func.avg(HrPerformanceReview.metric_quality).label("quality"),
            func.avg(HrPerformanceReview.metric_speed).label("speed"),
            func.avg(HrPerformanceReview.metric_collaboration).label("collaboration"),
            func.avg(HrPerformanceReview.metric_initiative).label("initiative"),
            func.avg(HrPerformanceReview.metric_reliability).label("reliability"),
            func.count(HrPerformanceReview.id).label("count"),
        )
        .join(User, User.id == HrPerformanceReview.user_id)
        .filter(
            HrPerformanceReview.business_id == business_id,
            HrPerformanceReview.review_period == latest_period,
        )
        .group_by("dept")
        .order_by(func.count(HrPerformanceReview.id).desc())
        .limit(5)
        .all()
    )

    radar_series = [
        {
            "name": row.dept,
            "data": [
                float(row.quality or 0),
                float(row.speed or 0),
                float(row.collaboration or 0),
                float(row.initiative or 0),
                float(row.reliability or 0),
            ],
        }
        for row in radar_rows
    ]

    performance_table = [
        {
            "employeeId": user.id,
            "name": user.full_name or user.username,
            "department": user.department or "Unassigned",
            "score": float(review.score),
            "goalsAchieved": int(review.goals_achieved),
            "rating": int(review.rating),
            "trend": review.trend,
        }
        for review, user in performance_rows
    ]

    # ---- Budget & cost forecasting ----
    current_year = today.year
    budget_plan = (
        db.query(HrBudgetPlan)
        .filter(HrBudgetPlan.business_id == business_id, HrBudgetPlan.year == current_year)
        .first()
    )
    annual_budget = float(budget_plan.annual_budget) if budget_plan else 0.0

    budget_months = (
        db.query(HrBudgetMonth)
        .filter(HrBudgetMonth.business_id == business_id, HrBudgetMonth.year == current_year)
        .all()
    )
    month_map = {bm.month: bm for bm in budget_months}
    budget_series = []
    actual_series = []
    forecast_series = []
    for m in range(1, 13):
        bm = month_map.get(m)
        budget_series.append(float(bm.budget) if bm else 0.0)
        actual_series.append(float(bm.actual) if bm else 0.0)
        forecast_series.append(float(bm.forecast) if bm else 0.0)

    spent_ytd = sum(actual_series[: today.month])
    forecasted_spend = sum(forecast_series)
    remaining = max(annual_budget - spent_ytd, 0.0)

    categories = (
        db.query(HrBudgetCategory)
        .filter(HrBudgetCategory.business_id == business_id, HrBudgetCategory.year == current_year)
        .order_by(HrBudgetCategory.spent.desc())
        .all()
    )
    category_rows = []
    for cat in categories:
        allocated = float(cat.allocated or 0)
        spent = float(cat.spent or 0)
        used_pct = round((spent / allocated) * 100, 2) if allocated else 0
        category_rows.append(
            {
                "name": cat.name,
                "allocated": allocated,
                "spent": spent,
                "usedPct": used_pct,
            }
        )

    q2_forecast = sum(forecast_series[3:6])
    q3_forecast = sum(forecast_series[6:9])
    q4_forecast = sum(forecast_series[9:12])

    # ---- Headcount & hiring ----
    total_headcount = (
        db.query(User)
        .filter(User.business_id == business_id, User.role == "employee", User.is_active == True)  # noqa: E712
        .count()
    )

    since_30 = today - timedelta(days=30)
    new_hires = (
        db.query(HrEmployeeEvent)
        .filter(
            HrEmployeeEvent.business_id == business_id,
            HrEmployeeEvent.event_type == "hire",
            HrEmployeeEvent.event_date >= since_30,
        )
        .count()
    )
    attrition = (
        db.query(HrEmployeeEvent)
        .filter(
            HrEmployeeEvent.business_id == business_id,
            HrEmployeeEvent.event_type == "termination",
            HrEmployeeEvent.event_date >= since_30,
        )
        .count()
    )
    open_positions = (
        db.query(HrHiringPosition)
        .filter(HrHiringPosition.business_id == business_id, HrHiringPosition.status == "open")
        .count()
    )

    # Headcount growth: last 15 months
    months = []
    headcount_series = []
    snap_start = date(today.year, today.month, 1)
    for i in range(14, -1, -1):
        months.append(_add_months(snap_start, -i))
    snapshot_map = {
        s.snapshot_month: s.headcount
        for s in db.query(HrHeadcountSnapshot)
        .filter(
            HrHeadcountSnapshot.business_id == business_id,
            HrHeadcountSnapshot.snapshot_month >= months[0],
            HrHeadcountSnapshot.snapshot_month <= months[-1],
        )
        .all()
    }
    for m in months:
        headcount_series.append(int(snapshot_map.get(m, 0)))

    dept_counts = (
        db.query(func.coalesce(User.department, "Unassigned").label("dept"), func.count(User.id))
        .filter(User.business_id == business_id, User.role == "employee", User.is_active == True)  # noqa: E712
        .group_by("dept")
        .order_by(func.count(User.id).desc())
        .all()
    )
    dept_labels = [row[0] for row in dept_counts]
    dept_series = [int(row[1]) for row in dept_counts]

    pipeline_rows = (
        db.query(HrHiringPipeline)
        .filter(HrHiringPipeline.business_id == business_id)
        .order_by(func.coalesce(HrHiringPipeline.sort_order, 999), HrHiringPipeline.stage.asc())
        .all()
    )
    pipeline_data = [
        {
            "stage": row.stage,
            "applicants": int(row.applicants),
            "priority": row.priority or "Medium",
        }
        for row in pipeline_rows
    ]

    return {
        "success": True,
        "status_code": status.HTTP_200_OK,
        "message": "HR analytics summary",
        "data": {
            "payroll": {
                "kpis": {
                    "netPay": net_pay,
                    "grossPay": gross_pay,
                    "deductions": deductions,
                    "employeesPaid": employees_paid,
                },
                "trend": {
                    "labels": trend_labels,
                    "series": [
                        {"name": "Gross Pay", "data": trend_gross},
                        {"name": "Net Pay", "data": trend_net},
                    ],
                },
                "split": {
                    "labels": split_labels,
                    "series": split_series,
                },
                "breakdown": breakdown_rows,
            },
            "performance": {
                "kpis": {
                    "avgScore": round(avg_score, 2),
                    "goalsAchieved": goals_achieved,
                    "reviewsCompleted": reviews_completed,
                    "underPerformers": under_performers,
                },
                "scoreBands": {
                    "labels": list(band_counts.keys()),
                    "series": list(band_counts.values()),
                },
                "radar": {
                    "labels": ["Quality", "Speed", "Collaboration", "Initiative", "Reliability"],
                    "series": radar_series,
                },
                "individuals": performance_table,
            },
            "budget": {
                "kpis": {
                    "annualBudget": annual_budget,
                    "spentYtd": spent_ytd,
                    "forecastedSpend": forecasted_spend,
                    "remaining": remaining,
                },
                "line": {
                    "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
                    "series": [
                        {"name": "Budget", "data": budget_series},
                        {"name": "Actual", "data": actual_series},
                        {"name": "Forecast", "data": forecast_series},
                    ],
                },
                "categories": category_rows,
                "quarterlyForecast": [
                    {"label": "Q2 Forecast", "value": q2_forecast, "note": "Apr-Jun"},
                    {"label": "Q3 Forecast", "value": q3_forecast, "note": "Jul-Sep"},
                    {"label": "Q4 Forecast", "value": q4_forecast, "note": "Oct-Dec"},
                ],
            },
            "headcount": {
                "kpis": {
                    "totalHeadcount": total_headcount,
                    "newHires": new_hires,
                    "attrition": attrition,
                    "openPositions": open_positions,
                },
                "growth": {
                    "labels": [_month_label(m) for m in months],
                    "series": [{"name": "Headcount", "data": headcount_series}],
                },
                "departmentSplit": {
                    "labels": dept_labels,
                    "series": dept_series,
                },
                "pipeline": pipeline_data,
            },
        },
    }


@router.get("/", status_code=status.HTTP_200_OK)
def hr_analytics(
    businessId: int = Query(...),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(_require_hr_admin),
):
    if not current_user.is_superuser and current_user.business_id != businessId:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return _build_analytics(db, businessId)


@router.get("/export", status_code=status.HTTP_200_OK)
def export_hr_analytics(
    businessId: int = Query(...),
    report: str = Query(..., min_length=3),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(_require_hr_admin),
):
    if not current_user.is_superuser and current_user.business_id != businessId:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    analytics = _build_analytics(db, businessId)["data"]
    business = db.query(Business).filter(Business.id == businessId).first()
    business_name = business.name if business else f"Business {businessId}"
    today = date.today().isoformat()

    rows: list[list[object]] = [
        ["Company", business_name],
        ["Generated", today],
        ["Report", report],
        [],
    ]

    if report == "payroll_breakdown":
        rows.append(["Employee", "Department", "Gross Pay", "Deductions", "Net Pay", "Status"])
        for row in analytics["payroll"]["breakdown"]:
            rows.append([
                row.get("name"),
                row.get("department"),
                row.get("grossPay"),
                row.get("deductions"),
                row.get("netPay"),
                row.get("status"),
            ])
    elif report == "payroll_trend":
        rows.append(["Month", "Gross Pay", "Net Pay"])
        labels = analytics["payroll"]["trend"]["labels"]
        gross = analytics["payroll"]["trend"]["series"][0]["data"] if analytics["payroll"]["trend"]["series"] else []
        net = analytics["payroll"]["trend"]["series"][1]["data"] if len(analytics["payroll"]["trend"]["series"]) > 1 else []
        for i, label in enumerate(labels):
            rows.append([label, gross[i] if i < len(gross) else 0, net[i] if i < len(net) else 0])
    elif report == "performance_individuals":
        rows.append(["Employee", "Department", "Score", "Goals Achieved", "Rating", "Trend"])
        for row in analytics["performance"]["individuals"]:
            rows.append([
                row.get("name"),
                row.get("department"),
                row.get("score"),
                row.get("goalsAchieved"),
                row.get("rating"),
                row.get("trend"),
            ])
    elif report == "budget_categories":
        rows.append(["Category", "Allocated", "Spent", "Used %"])
        for row in analytics["budget"]["categories"]:
            rows.append([
                row.get("name"),
                row.get("allocated"),
                row.get("spent"),
                row.get("usedPct"),
            ])
    elif report == "budget_line":
        rows.append(["Month", "Budget", "Actual", "Forecast"])
        labels = analytics["budget"]["line"]["labels"]
        series = analytics["budget"]["line"]["series"]
        budget = series[0]["data"] if len(series) > 0 else []
        actual = series[1]["data"] if len(series) > 1 else []
        forecast = series[2]["data"] if len(series) > 2 else []
        for i, label in enumerate(labels):
            rows.append([
                label,
                budget[i] if i < len(budget) else 0,
                actual[i] if i < len(actual) else 0,
                forecast[i] if i < len(forecast) else 0,
            ])
    elif report == "headcount_growth":
        rows.append(["Month", "Headcount"])
        labels = analytics["headcount"]["growth"]["labels"]
        data = analytics["headcount"]["growth"]["series"][0]["data"] if analytics["headcount"]["growth"]["series"] else []
        for i, label in enumerate(labels):
            rows.append([label, data[i] if i < len(data) else 0])
    elif report == "hiring_pipeline":
        rows.append(["Stage", "Applicants", "Priority"])
        for row in analytics["headcount"]["pipeline"]:
            rows.append([
                row.get("stage"),
                row.get("applicants"),
                row.get("priority"),
            ])
    else:
        raise HTTPException(status_code=400, detail="Invalid report type")

    filename = f"hr-{report}-{today}.csv"
    return _csv_response(filename, rows)


@router.get("/drilldown", status_code=status.HTTP_200_OK)
def hr_analytics_drilldown(
    businessId: int = Query(...),
    metric: str = Query(..., min_length=3),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(_require_hr_admin),
):
    if not current_user.is_superuser and current_user.business_id != businessId:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    today = date.today()
    metric = metric.lower()

    if metric in {"net_pay", "gross_pay"}:
        periods = (
            db.query(PayPeriod)
            .filter(PayPeriod.business_id == businessId)
            .order_by(PayPeriod.period_end.desc())
            .limit(2)
            .all()
        )
        periods = list(reversed(periods))
        if not periods:
            return {"success": True, "data": {"metric": metric, "labels": [], "totals": {}, "departments": [], "employees": []}}

        labels = [_month_label(p.period_end) for p in periods]
        period_ids = [p.id for p in periods]

        totals = {}
        for p in periods:
            total = (
                db.query(func.coalesce(func.sum(Payslip.net_pay if metric == "net_pay" else Payslip.gross_pay), 0))
                .filter(Payslip.business_id == businessId, Payslip.pay_period_id == p.id)
                .scalar()
                or 0
            )
            totals[p.id] = float(total)

        dept_rows = (
            db.query(
                func.coalesce(User.department, "Unassigned").label("dept"),
                Payslip.pay_period_id.label("period_id"),
                func.coalesce(func.sum(Payslip.net_pay if metric == "net_pay" else Payslip.gross_pay), 0).label("total"),
            )
            .join(User, User.id == Payslip.user_id)
            .filter(Payslip.business_id == businessId, Payslip.pay_period_id.in_(period_ids))
            .group_by("dept", "period_id")
            .all()
        )
        dept_map = {}
        for row in dept_rows:
            dept_map.setdefault(row.dept, {})[row.period_id] = float(row.total)
        departments = [
            {
                "department": dept,
                "previous": dept_map.get(dept, {}).get(period_ids[0], 0.0) if len(period_ids) > 1 else 0.0,
                "current": dept_map.get(dept, {}).get(period_ids[-1], 0.0),
            }
            for dept in dept_map.keys()
        ]

        employee_rows = (
            db.query(
                User.id,
                User.full_name,
                User.username,
                User.department,
                Payslip.pay_period_id.label("period_id"),
                func.coalesce(func.sum(Payslip.net_pay if metric == "net_pay" else Payslip.gross_pay), 0).label("total"),
            )
            .join(User, User.id == Payslip.user_id)
            .filter(Payslip.business_id == businessId, Payslip.pay_period_id.in_(period_ids))
            .group_by(User.id, User.full_name, User.username, User.department, "period_id")
            .all()
        )
        emp_map = {}
        for row in employee_rows:
            name = row.full_name or row.username
            emp_map.setdefault(row.id, {"name": name, "department": row.department or "Unassigned", "values": {}})
            emp_map[row.id]["values"][row.period_id] = float(row.total)
        employees = [
            {
                "employeeId": emp_id,
                "name": data["name"],
                "department": data["department"],
                "previous": data["values"].get(period_ids[0], 0.0) if len(period_ids) > 1 else 0.0,
                "current": data["values"].get(period_ids[-1], 0.0),
            }
            for emp_id, data in emp_map.items()
        ]

        return {
            "success": True,
            "data": {
                "metric": metric,
                "labels": labels,
                "totals": {
                    "previous": totals.get(period_ids[0], 0.0) if len(period_ids) > 1 else 0.0,
                    "current": totals.get(period_ids[-1], 0.0),
                },
                "departments": departments,
                "employees": employees,
            },
        }

    if metric == "headcount":
        months = [
            _add_months(date(today.year, today.month, 1), -1),
            date(today.year, today.month, 1),
        ]
        snaps = (
            db.query(HrHeadcountSnapshot)
            .filter(HrHeadcountSnapshot.business_id == businessId, HrHeadcountSnapshot.snapshot_month.in_(months))
            .all()
        )
        snap_map = {s.snapshot_month: int(s.headcount) for s in snaps}
        departments = (
            db.query(func.coalesce(User.department, "Unassigned").label("dept"), func.count(User.id))
            .filter(User.business_id == businessId, User.role == "employee", User.is_active == True)  # noqa: E712
            .group_by("dept")
            .order_by(func.count(User.id).desc())
            .all()
        )
        return {
            "success": True,
            "data": {
                "metric": metric,
                "labels": [_month_label(m) for m in months],
                "totals": {
                    "previous": snap_map.get(months[0], 0),
                    "current": snap_map.get(months[1], 0),
                },
                "departments": [
                    {"department": row[0], "previous": 0, "current": int(row[1])}
                    for row in departments
                ],
                "employees": [],
            },
        }

    if metric == "budget_spent":
        current_year = today.year
        prev_month = today.month - 1 or 12
        prev_year = current_year if today.month > 1 else current_year - 1
        month_rows = (
            db.query(HrBudgetMonth)
            .filter(
                HrBudgetMonth.business_id == businessId,
                ((HrBudgetMonth.year == current_year) & (HrBudgetMonth.month == today.month))
                | ((HrBudgetMonth.year == prev_year) & (HrBudgetMonth.month == prev_month))
            )
            .all()
        )
        actual_map = {(row.year, row.month): float(row.actual) for row in month_rows}

        categories = (
            db.query(HrBudgetCategory)
            .filter(HrBudgetCategory.business_id == businessId, HrBudgetCategory.year == current_year)
            .order_by(HrBudgetCategory.spent.desc())
            .all()
        )
        return {
            "success": True,
            "data": {
                "metric": metric,
                "labels": [_month_label(date(prev_year, prev_month, 1)), _month_label(date(current_year, today.month, 1))],
                "totals": {
                    "previous": actual_map.get((prev_year, prev_month), 0.0),
                    "current": actual_map.get((current_year, today.month), 0.0),
                },
                "departments": [],
                "employees": [],
                "categories": [
                    {
                        "name": cat.name,
                        "allocated": float(cat.allocated or 0),
                        "spent": float(cat.spent or 0),
                        "usedPct": round((float(cat.spent or 0) / float(cat.allocated or 0) * 100), 2) if cat.allocated else 0,
                    }
                    for cat in categories
                ],
            },
        }

    raise HTTPException(status_code=400, detail="Invalid metric")
