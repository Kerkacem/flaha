from __future__ import annotations

from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.ai.advisory_service import process_advisory_query
from src.backend.schemas import AdvisoryRequest, AdvisoryResponse
from src.database.connection import get_db

router = APIRouter()


@router.post("/query", response_model=AdvisoryResponse)
async def advisory_query(body: AdvisoryRequest, db: AsyncSession = Depends(get_db)):
    result = await process_advisory_query(
        farmer_phone=body.farmer_phone,
        query=body.query,
        image_url=body.image_url,
        db=db,
    )
    return AdvisoryResponse(**result)


@router.post("/diagnose")
async def diagnose_image(file: UploadFile, farmer_phone: str, db: AsyncSession = Depends(get_db)):
    from src.backend.schemas import AdvisoryRequest
    body = AdvisoryRequest(farmer_phone=farmer_phone, query="تشخيص المرض من الصورة")
    result = await process_advisory_query(
        farmer_phone=body.farmer_phone,
        query=body.query,
        image_url=body.image_url,
        image_bytes=await file.read(),
        db=db,
    )
    return AdvisoryResponse(**result)
