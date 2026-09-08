"""Shared pytest fixtures for OkanaganConnect tests."""
import pytest
from fastapi.testclient import TestClient
import os

# Use separate test database to avoid modifying dev.db
os.environ["OK_DB"] = "sqlite:///backend/DB/test.db"

from backend.main import app

@pytest.fixture(name="client")
def client_fixture():
    """Provide TestClient with lifespan enabled to create test database tables."""
    with TestClient(app) as client:
        yield client

