# api/v1/hr_employees.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from api import deps
from crud import user as crud_user
from models.user import User
from schemas.employee_directory import (
    EmployeeCreateRequest,
    EmployeeDetailResponse,
    EmployeeListResponse,
    EmployeeUpdateRequest,
)
from schemas.employee_registration import (
    EmployeeApprovalResponse,
    PendingEmployeeListResponse,
    PendingEmployeeItem,
)

router = APIRouter()


def _require_hr_admin(current_user: User = Depends(deps.require_roles(["customer_owner", "hr_admin"]))):
    return current_user


@router.get("/pending", response_model=PendingEmployeeListResponse)
def list_pending_employees(
    businessId: int = Query(...),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(_require_hr_admin),
):
    if not current_user.is_superuser and current_user.business_id != businessId:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    pending = (
        db.query(User)
        .filter(
            User.business_id == businessId,
            User.role == "employee",
            User.is_active == False,  # noqa: E712
        )
        .order_by(User.created_at.desc())
        .all()
    )

    data = [
        PendingEmployeeItem(
            id=user.id,
            fullName=user.full_name or user.username,
            email=user.email,
            phone=user.contact,
            employeeId=user.employee_id,
            department=user.department,
            status=user.status,
        )
        for user in pending
    ]

    return {
        "success": True,
        "status_code": status.HTTP_200_OK,
        "message": "Pending employees retrieved successfully",
        "total": len(data),
        "data": data,
    }


@router.post("/{user_id}/approve", response_model=EmployeeApprovalResponse)
def approve_employee(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(_require_hr_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.role != "employee":
        raise HTTPException(status_code=400, detail="User is not an employee")

    if not current_user.is_superuser and current_user.business_id != user.business_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    user.is_active = True
    user.status = "active"
    db.add(user)
    db.commit()

    return {
        "success": True,
        "status_code": status.HTTP_200_OK,
        "message": "Employee approved successfully",
    }


@router.get("/", response_model=EmployeeListResponse)
def list_employees(
    businessId: int = Query(...),
    q: str | None = Query(None),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(_require_hr_admin),
):
    if not current_user.is_superuser and current_user.business_id != businessId:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    query = db.query(User).filter(
        User.business_id == businessId,
        User.role == "employee",
    )
    if q:
        like = f"%{q}%"
        query = query.filter(
            (User.full_name.ilike(like))
            | (User.email.ilike(like))
            | (User.username.ilike(like))
            | (User.employee_id.ilike(like))
            | (User.department.ilike(like))
        )

    employees = query.order_by(User.created_at.desc()).all()
    data = [
        {
            "id": user.id,
            "fullName": user.full_name or user.username,
            "email": user.email,
            "phone": user.contact,
            "employeeId": user.employee_id,
            "department": user.department,
            "status": user.status,
            "isActive": user.is_active,
        }
        for user in employees
    ]

    return {
        "success": True,
        "status_code": status.HTTP_200_OK,
        "message": "Employees retrieved successfully",
        "total": len(data),
        "data": data,
    }


@router.get("/{user_id}", response_model=EmployeeDetailResponse)
def get_employee(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user or user.role != "employee":
        raise HTTPException(status_code=404, detail="Employee not found")

    if current_user.is_superuser:
        pass
    elif current_user.role in {"customer_owner", "hr_admin"}:
        if current_user.business_id != user.business_id:
            raise HTTPException(status_code=403, detail="Not enough permissions")
    elif current_user.role == "employee":
        if current_user.id != user.id:
            raise HTTPException(status_code=403, detail="Not enough permissions")
    else:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return {
        "success": True,
        "status_code": status.HTTP_200_OK,
        "message": "Employee retrieved successfully",
        "data": {
            "id": user.id,
            "fullName": user.full_name or user.username,
            "email": user.email,
            "phone": user.contact,
            "employeeId": user.employee_id,
            "department": user.department,
            "status": user.status,
            "isActive": user.is_active,
            "businessId": user.business_id,
        },
    }


@router.post("/", response_model=EmployeeDetailResponse, status_code=status.HTTP_201_CREATED)
def create_employee(
    payload: EmployeeCreateRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(_require_hr_admin),
):
    business_id = payload.business_id
    if not current_user.is_superuser and current_user.business_id != business_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    existing = crud_user.get_user_by_email(db, email=payload.email)
    if existing:
        raise HTTPException(status_code=409, detail="Email already exists")

    user = crud_user.create_user_with_details(
        db,
        email=payload.email,
        password=payload.password,
        full_name=payload.full_name,
        role="employee",
        is_superuser=False,
        is_active=True,
        status="active",
        contact=payload.phone,
        employee_id=payload.employee_id,
        department=payload.department,
        business_id=business_id,
    )

    return {
        "success": True,
        "status_code": status.HTTP_201_CREATED,
        "message": "Employee created successfully",
        "data": {
            "id": user.id,
            "fullName": user.full_name or user.username,
            "email": user.email,
            "phone": user.contact,
            "employeeId": user.employee_id,
            "department": user.department,
            "status": user.status,
            "isActive": user.is_active,
            "businessId": user.business_id,
        },
    }


@router.put("/{user_id}", response_model=EmployeeDetailResponse)
def update_employee(
    user_id: int,
    payload: EmployeeUpdateRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(_require_hr_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user or user.role != "employee":
        raise HTTPException(status_code=404, detail="Employee not found")

    if not current_user.is_superuser and current_user.business_id != user.business_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    updates = payload.dict(exclude_unset=True, by_alias=False)
    if "full_name" in updates:
        user.full_name = updates["full_name"]
    if "email" in updates and updates["email"] != user.email:
        existing = crud_user.get_user_by_email(db, email=updates["email"])
        if existing and existing.id != user.id:
            raise HTTPException(status_code=409, detail="Email already exists")
        user.email = updates["email"]
    if "phone" in updates:
        user.contact = updates["phone"]
    if "employee_id" in updates:
        user.employee_id = updates["employee_id"]
    if "department" in updates:
        user.department = updates["department"]
    if "status" in updates:
        user.status = updates["status"]
    if "is_active" in updates:
        user.is_active = updates["is_active"]

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "success": True,
        "status_code": status.HTTP_200_OK,
        "message": "Employee updated successfully",
        "data": {
            "id": user.id,
            "fullName": user.full_name or user.username,
            "email": user.email,
            "phone": user.contact,
            "employeeId": user.employee_id,
            "department": user.department,
            "status": user.status,
            "isActive": user.is_active,
            "businessId": user.business_id,
        },
    }


@router.post("/{user_id}/deactivate", response_model=EmployeeApprovalResponse)
def deactivate_employee(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(_require_hr_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user or user.role != "employee":
        raise HTTPException(status_code=404, detail="Employee not found")

    if not current_user.is_superuser and current_user.business_id != user.business_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    user.is_active = False
    user.status = "inactive"
    db.add(user)
    db.commit()

    return {
        "success": True,
        "status_code": status.HTTP_200_OK,
        "message": "Employee deactivated successfully",
    }
