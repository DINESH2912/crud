import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_create_item():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/items/", json={"name": "Test", "description": "Test desc"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test"
    assert "id" in data

@pytest.mark.asyncio
async def test_read_items():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/items/")
    assert response.status_code == 200
