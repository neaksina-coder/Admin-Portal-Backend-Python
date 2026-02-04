# api/v1/promos.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api import deps
from crud import audit_log as crud_audit_log
from crud import promo_code as crud_promo
from schemas.promo_code import (
    PromoCodeCreate,
    PromoCodeUpdate,
    PromoCodeResponse,
    PromoCodeListResponse,
    PromoApplyRequest,
    PromoApplyResponse,
)

router = APIRouter()


@router.post("/", response_model=PromoCodeResponse, status_code=201)
def create_promo(
    promo_in: PromoCodeCreate,
    db: Session = Depends(deps.get_db),
    current_user=Depends(deps.require_roles(["admin"])),
):
    promo = crud_promo.create_promo(db, promo_in)
    crud_audit_log.create_audit_log(
        db,
        action="promo_created",
        actor_user_id=current_user.id,
        business_id=promo.business_id,
        target_type="promo_code",
        target_id=promo.id,
        metadata_json={"code": promo.code, "discountType": promo.discount_type},
    )
    db.commit()
    return {
        "success": True,
        "status_code": 201,
        "message": "Promo code created successfully",
        "data": promo,
    }


@router.get("/", response_model=PromoCodeListResponse)
def list_promos(
    businessId: int = Query(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    promos = crud_promo.list_promos(db, business_id=businessId, skip=skip, limit=limit)
    return {
        "success": True,
        "status_code": 200,
        "message": "Promo codes retrieved successfully",
        "total": len(promos),
        "data": promos,
    }


@router.get("/{promo_id}", response_model=PromoCodeResponse)
def get_promo(
    promo_id: int,
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    promo = crud_promo.get_promo(db, promo_id)
    if not promo:
        raise HTTPException(status_code=404, detail="Promo code not found")
    return {
        "success": True,
        "status_code": 200,
        "message": "Promo code retrieved successfully",
        "data": promo,
    }


@router.put("/{promo_id}", response_model=PromoCodeResponse)
def update_promo(
    promo_id: int,
    promo_in: PromoCodeUpdate,
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    promo = crud_promo.update_promo(db, promo_id, promo_in)
    if not promo:
        raise HTTPException(status_code=404, detail="Promo code not found")
    return {
        "success": True,
        "status_code": 200,
        "message": "Promo code updated successfully",
        "data": promo,
    }


@router.delete("/{promo_id}")
def delete_promo(
    promo_id: int,
    db: Session = Depends(deps.get_db),
    current_user=Depends(deps.require_roles(["admin"])),
):
    promo = crud_promo.delete_promo(db, promo_id)
    if not promo:
        raise HTTPException(status_code=404, detail="Promo code not found")
    crud_audit_log.create_audit_log(
        db,
        action="promo_deleted",
        actor_user_id=current_user.id,
        business_id=promo.business_id,
        target_type="promo_code",
        target_id=promo.id,
        metadata_json={"code": promo.code},
    )
    db.commit()
    return {"success": True, "message": "Promo code deleted successfully"}


@router.post("/apply", response_model=PromoApplyResponse)
def apply_promo(
    payload: PromoApplyRequest,
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    promo, result = crud_promo.validate_and_apply(
        db, payload.business_id, payload.code, payload.amount
    )
    if not promo:
        raise HTTPException(status_code=400, detail=result)
    return {
        "success": True,
        "status_code": 200,
        "message": "Promo code applied",
        "data": result,
    }
