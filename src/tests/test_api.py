from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_health_endpoint(client):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] in ("healthy", "degraded")


@pytest.mark.asyncio
async def test_create_product(client, auth_headers):
    payload = {
        "farmer_phone": "+213555999999",
        "name": "طماطم",
        "category": "خضار",
        "quantity": 5,
        "unit": "قنطار",
        "price": 2000,
        "wilaya": "البويرة",
    }
    response = await client.post("/api/v1/marketplace/products", json=payload, headers=auth_headers)
    if response.status_code == 404:
        pytest.skip("Farmer not found (expected without DB setup)")
    assert response.status_code in (200, 404)


@pytest.mark.asyncio
async def test_list_products(client):
    response = await client.get("/api/v1/marketplace/products")
    assert response.status_code == 200
    data = response.json()
    assert "products" in data


@pytest.mark.asyncio
async def test_ussd_callback(client):
    payload = {"sessionId": "test-123", "serviceCode": "*233#", "phoneNumber": "+213555123456", "text": ""}
    response = await client.post("/api/v1/ussd/callback", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "response" in data


@pytest.mark.asyncio
async def test_advisory_query(client):
    payload = {"farmer_phone": "+213555123456", "query": "طماطم عندها mildiou شنو العلاج؟"}
    response = await client.post("/api/v1/advisory/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
