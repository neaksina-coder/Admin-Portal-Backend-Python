# api/v1/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from api import deps
from crud import user as crud_user
from models.user_lookups import UserRole, UserPlan, UserStatus
from schemas.user import (
    User,
    UserRoleUpdate,
    UserManagementCreate,
    UserManagementUpdate,
    UserListResponse,
    UserDetail,
    UserDeleteResponse,
)

router = APIRouter()

USER_FILTERS_RESPONSE = {
    "roles": [
        {"label": "User", "value": "user"},
        {"label": "Admin", "value": "admin"},
        {"label": "Superuser", "value": "superuser"},
    ],
    "plans": [
        {"label": "Basic", "value": "basic"},
        {"label": "Company", "value": "company"},
        {"label": "Enterprise", "value": "enterprise"},
        {"label": "Team", "value": "team"},
    ],
    "statuses": [
        {"label": "Active", "value": "active"},
        {"label": "Inactive", "value": "inactive"},
        {"label": "Pending", "value": "pending"},
    ],
}


def _serialize_user_list_item(user):
    return {
        "id": user.id,
        "fullName": user.full_name or user.username,
        "email": user.email,
        "role": user.role,
        "plan": user.plan,
        "billing": user.billing,
        "status": user.status,
    }


def _serialize_user_detail(user):
    data = _serialize_user_list_item(user)
    data["profile"] = {
        "company": user.company,
        "country": user.country,
        "contact": user.contact,
    }
    return data


@router.get("/", response_model=UserListResponse)
def list_users(
    q: Optional[str] = None,
    role: Optional[str] = None,
    plan: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    itemsPerPage: int = 10,
    sortBy: Optional[str] = None,
    orderBy: str = "asc",
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_roles(["admin"])),
):
    if page < 1 or itemsPerPage < 1:
        raise HTTPException(status_code=400, detail="Invalid pagination values")
    if orderBy.lower() not in {"asc", "desc"}:
        raise HTTPException(status_code=400, detail="Invalid orderBy value")
    if role and role not in {"user", "admin", "superuser"}:
        raise HTTPException(status_code=400, detail="Invalid role filter")
    if not current_user.is_superuser and role and role != "user":
        raise HTTPException(status_code=403, detail="Not enough permissions")

    try:
        users, total = crud_user.get_users_filtered(
            db,
            q=q,
            role=role,
            plan=plan,
            status=status,
            page=page,
            items_per_page=itemsPerPage,
            sort_by=sortBy,
            order_by=orderBy,
            current_user=current_user,
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid sortBy value")

    return {
        "users": [_serialize_user_list_item(user) for user in users],
        "totalUsers": total,
        "page": page,
    }


@router.get("/filters")
def get_user_filters(
    db: Session = Depends(deps.get_db),
    _: User = Depends(deps.require_roles(["admin"])),
):
    roles = (
        db.query(UserRole)
        .order_by(UserRole.sort_order.asc(), UserRole.label.asc())
        .all()
    )
    plans = (
        db.query(UserPlan)
        .order_by(UserPlan.sort_order.asc(), UserPlan.label.asc())
        .all()
    )
    statuses = (
        db.query(UserStatus)
        .order_by(UserStatus.sort_order.asc(), UserStatus.label.asc())
        .all()
    )

    return {
        "roles": [
            {"label": role.label, "value": role.value} for role in roles
        ]
        if roles
        else USER_FILTERS_RESPONSE["roles"],
        "plans": [
            {"label": plan.label, "value": plan.value} for plan in plans
        ]
        if plans
        else USER_FILTERS_RESPONSE["plans"],
        "statuses": [
            {"label": status.label, "value": status.value} for status in statuses
        ]
        if statuses
        else USER_FILTERS_RESPONSE["statuses"],
    }


@router.get("/{user_id}", response_model=UserDetail)
def get_user_detail(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_roles(["admin"])),
):
    user = crud_user.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not current_user.is_superuser:
        if user.is_superuser or user.role != "user":
            raise HTTPException(status_code=403, detail="Not enough permissions")
    return _serialize_user_detail(user)


@router.post("/", response_model=UserDetail, status_code=status.HTTP_201_CREATED)
def create_user(
    user_in: UserManagementCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_roles(["admin"])),
):
    if not current_user.is_superuser and user_in.role != "user":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    existing = crud_user.get_user_by_email(db, email=user_in.email)
    if existing:
        raise HTTPException(status_code=409, detail="Email already exists")
    is_superuser = user_in.role == "superuser"
    user = crud_user.create_user_with_details(
        db,
        email=user_in.email,
        password=user_in.password,
        full_name=user_in.full_name,
        role=user_in.role,
        is_superuser=is_superuser,
        plan=user_in.plan,
        billing=user_in.billing,
        status=user_in.status,
        company=None,
        country=None,
        contact=None,
    )
    return _serialize_user_detail(user)


@router.put("/{user_id}", response_model=UserDetail)
def update_user(
    user_id: int,
    user_in: UserManagementUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_roles(["admin"])),
):
    user = crud_user.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not current_user.is_superuser:
        if user.is_superuser or user.role != "user":
            raise HTTPException(status_code=403, detail="Not enough permissions")
        if user_in.role and user_in.role != "user":
            raise HTTPException(status_code=403, detail="Not enough permissions")

    updates = user_in.dict(exclude_unset=True, by_alias=False)
    if "role" in updates and updates["role"] is not None:
        updates["is_superuser"] = updates["role"] == "superuser"
    updated = crud_user.update_user_details(db, user_id=user_id, updates=updates)
    return _serialize_user_detail(updated)


@router.delete("/{user_id}", response_model=UserDeleteResponse)
def delete_user(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_roles(["admin"])),
):
    user = crud_user.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not current_user.is_superuser:
        if user.is_superuser or user.role != "user":
            raise HTTPException(status_code=403, detail="Not enough permissions")
    crud_user.delete_user(db, user_id=user_id)
    return {"success": True}


@router.post("/admins", response_model=UserDetail, status_code=status.HTTP_201_CREATED)
def create_admin(
    user_in: UserManagementCreate,
    db: Session = Depends(deps.get_db),
    _: User = Depends(deps.require_superuser),
):
    if user_in.role != "admin":
        raise HTTPException(status_code=400, detail="Role must be admin")
    existing = crud_user.get_user_by_email(db, email=user_in.email)
    if existing:
        raise HTTPException(status_code=409, detail="Email already exists")
    user = crud_user.create_user_with_details(
        db,
        email=user_in.email,
        password=user_in.password,
        full_name=user_in.full_name,
        role="admin",
        is_superuser=False,
        plan=user_in.plan,
        billing=user_in.billing,
        status=user_in.status,
        company=None,
        country=None,
        contact=None,
    )
    return _serialize_user_detail(user)


@router.put("/{user_id}/role", response_model=UserDetail)
def update_user_role(
    user_id: int,
    role_in: UserRoleUpdate,
    db: Session = Depends(deps.get_db),
    _: User = Depends(deps.require_superuser),
):
    if role_in.role == "superuser":
        role = "superuser"
        is_superuser = True
    elif role_in.role == "admin":
        role = "admin"
        is_superuser = False
    else:
        role = "user"
        is_superuser = False
    user = crud_user.update_user_role(
        db, user_id=user_id, role=role, is_superuser=is_superuser
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return _serialize_user_detail(user)


@router.post("/superusers", response_model=UserDetail, status_code=status.HTTP_201_CREATED)
def create_superuser(
    user_in: UserManagementCreate,
    db: Session = Depends(deps.get_db),
    _: User = Depends(deps.require_superuser),
):
    if user_in.role != "superuser":
        raise HTTPException(status_code=400, detail="Role must be superuser")
    existing = crud_user.get_user_by_email(db, email=user_in.email)
    if existing:
        raise HTTPException(status_code=409, detail="Email already exists")
    user = crud_user.create_user_with_details(
        db,
        email=user_in.email,
        password=user_in.password,
        full_name=user_in.full_name,
        role="superuser",
        is_superuser=True,
        plan=user_in.plan,
        billing=user_in.billing,
        status=user_in.status,
        company=None,
        country=None,
        contact=None,
    )
    return _serialize_user_detail(user)
