import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from main import app  # your FastAPI instance

@pytest.mark.asyncio
async def test_create_item():
    async with AsyncClient(app=app, base_url="http://test") as ac:  # ❌ old
        response = await ac.post("/items/", json={"name": "Test", "description": "Test desc"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test"
    assert "id" in data
