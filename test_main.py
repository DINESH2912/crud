import pytest
from httpx import AsyncClient
from main import app
from asgi_lifespan import LifespanManager  # pip install asgi-lifespan

@pytest.mark.asyncio
async def test_create_item():
    # Wrap app in LifespanManager
    async with LifespanManager(app):
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/items/",
                json={"name": "Test Item", "description": "Test Description"}
            )
    assert response.status_code == 200  # or 201 if you change endpoint
    data = response.json()
    assert data["name"] == "Test Item"
    assert "id" in data

@pytest.mark.asyncio
async def test_read_items():
    async with LifespanManager(app):
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/items/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
