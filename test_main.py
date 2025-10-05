import pytest
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from asgi_lifespan import LifespanManager

from main import app, get_db
from database import Base
from models import Item

# -----------------------------
# Test database setup (in-memory)
# -----------------------------
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"  # For file-based DB
# For in-memory DB, use sqlite:///:memory:
# SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override get_db dependency to use test DB
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create all tables in the test DB
Base.metadata.create_all(bind=engine)

# -----------------------------
# Pytest async tests
# -----------------------------
@pytest.mark.asyncio
async def test_create_item():
    async with LifespanManager(app):
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/items/", json={"name": "Test Item", "description": "Test Desc"})
    assert response.status_code == 200
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
    assert len(data) >= 1  # At least one item exists from create test

@pytest.mark.asyncio
async def test_read_one_item():
    async with LifespanManager(app):
        async with AsyncClient(app=app, base_url="http://test") as client:
            # First create an item
            create_resp = await client.post("/items/", json={"name": "Single Item", "description": "Single Desc"})
            item_id = create_resp.json()["id"]

            # Then read the same item
            read_resp = await client.get(f"/items/{item_id}")
    assert read_resp.status_code == 200
    data = read_resp.json()
    assert data["id"] == item_id
    assert data["name"] == "Single Item"

@pytest.mark.asyncio
async def test_update_item():
    async with LifespanManager(app):
        async with AsyncClient(app=app, base_url="http://test") as client:
            create_resp = await client.post("/items/", json={"name": "Old Name", "description": "Old Desc"})
            item_id = create_resp.json()["id"]

            update_resp = await client.put(f"/items/{item_id}", json={"name": "New Name", "description": "New Desc"})
    assert update_resp.status_code == 200
    data = update_resp.json()
    assert data["name"] == "New Name"
    assert data["description"] == "New Desc"

@pytest.mark.asyncio
async def test_delete_item():
    async with LifespanManager(app):
        async with AsyncClient(app=app, base_url="http://test") as client:
            create_resp = await client.post("/items/", json={"name": "Delete Item", "description": "Delete Desc"})
            item_id = create_resp.json()["id"]

            delete_resp = await client.delete(f"/items/{item_id}")
    assert delete_resp.status_code == 200
    assert delete_resp.json() == {"message": "Item deleted successfully"}
