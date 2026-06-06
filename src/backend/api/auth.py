from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.middleware.auth import create_token, require_farmer
from src.database.connection import get_db
from src.database.models import Farmer

router = APIRouter()


class LoginRequest(BaseModel):
    phone: str = Field(..., pattern=r"^\+213\d{9}$")
    otp: str = "000000"


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    farmer_id: str
    name: str
    is_new: bool = False


class RegisterRequest(BaseModel):
    phone: str = Field(..., pattern=r"^\+213\d{9}$")
    name: str = Field(..., min_length=2, max_length=100)
    wilaya: str = Field(..., min_length=2, max_length=50)
    commune: str | None = None


@router.post("/auth/login", response_model=LoginResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Farmer).where(Farmer.phone == req.phone))
    farmer = result.scalar_one_or_none()
    if not farmer:
        return LoginResponse(
            access_token="",
            farmer_id="",
            name="",
            is_new=True,
        )
    token = create_token(farmer.id, farmer.role.value)
    return LoginResponse(access_token=token, farmer_id=farmer.id, name=farmer.name)


@router.post("/auth/register", response_model=LoginResponse)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Farmer).where(Farmer.phone == req.phone))
    if result.scalar_one_or_none():
        raise HTTPException(409, "❌ هذا الرقم مسجل بالفعل")

    farmer = Farmer(
        name=req.name,
        phone=req.phone,
        wilaya=req.wilaya,
        commune=req.commune,
        is_verified=True,
    )
    db.add(farmer)
    await db.flush()
    token = create_token(farmer.id, farmer.role.value)
    return LoginResponse(access_token=token, farmer_id=farmer.id, name=farmer.name, is_new=True)


@router.get("/auth/me")
async def get_me(farmer: Farmer = Depends(require_farmer)):
    return {
        "id": farmer.id,
        "name": farmer.name,
        "phone": farmer.phone,
        "wilaya": farmer.wilaya,
        "commune": farmer.commune,
        "role": farmer.role.value,
        "rating_avg": float(farmer.rating_avg),
        "total_transactions": farmer.total_transactions,
        "is_verified": farmer.is_verified,
        "credit_score": farmer.credit_score,
        "land_hectares": float(farmer.land_hectares) if farmer.land_hectares else None,
        "crops": farmer.crops,
    }
