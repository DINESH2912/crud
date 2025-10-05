import pytest
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from asgi_lifespan import LifespanManager

from main import app, get_db


# -----------------------------
# Test database setup (in-memory)
# -----------------------------
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"  # For file-based DB
# For in-memory DB, use sqlite:///:memory:
# SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

from fastapi.testclient import TestClient

client = TestClient(app)

def test_create_item():
    response = client.post("/items/", json={"name": "Test", "description": "Test Desc"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test"
