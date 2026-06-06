from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.backend.main import app
from src.database.models import Base


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def auth_headers(client):
    """يسجل فلاحاً عبر API ويرجع headers مع التوكن"""
    resp = await client.post("/api/v1/auth/register", json={
        "phone": "+213555999999",
        "name": "فلاح اختبار",
        "wilaya": "البويرة",
    })
    data = resp.json()
    return {"Authorization": f"Bearer {data['access_token']}"}


@pytest.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session

    await engine.dispose()
