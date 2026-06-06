from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.schemas import USSDRequest, USSDResponse
from src.backend.services.ussd_service import handle_ussd
from src.database.connection import get_db

router = APIRouter()


@router.post("/callback", response_model=USSDResponse)
async def ussd_callback(body: USSDRequest, db: AsyncSession = Depends(get_db)):
    response_text = await handle_ussd(
        session_id=body.sessionId,
        phone=body.phoneNumber,
        text=body.text,
        db=db,
    )
    return USSDResponse(response=response_text, sessionId=body.sessionId)
