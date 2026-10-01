# ============================================================
# KLARIXA KROADSCONTROL (KST)
# Tests de endpoints básicos
# WIPO / NNN / NDA — EinsRos Global Cortex Ultd
# ============================================================

import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_root(client):
    """GET / debe responder con status online."""
    r = client.get("/")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "online"
    assert data["protocol"] == "WIPO/NNN/NDA"
    assert "EinsRos" in data["titular"]


def test_health(client):
    """GET /health debe responder healthy."""
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "healthy"
    assert "components" in data


def test_version(client):
    """GET /version debe incluir WIPO ID."""
    r = client.get("/version")
    assert r.status_code == 200
    data = r.json()
    assert data["app"] == "KROADSCONTROL"
    assert "wipo_id" in data
    assert data["hackathon"] == "AMD Developer Hackathon: ACT III"