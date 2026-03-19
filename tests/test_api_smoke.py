"""
Full-stack smoke test — requires a running API (make up, or uvicorn locally).
Run with: pytest tests/ -v
"""

import httpx
import pytest


def test_api_health(api_url):
    """API health endpoint responds with status ok."""
    response = httpx.get(f"{api_url}/api/health", timeout=10)
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_datasets_endpoint_exists(api_url):
    response = httpx.get(f"{api_url}/api/datasets", timeout=10)
    assert response.status_code == 200


def test_questions_endpoint_exists(api_url):
    response = httpx.get(f"{api_url}/api/questions", timeout=10)
    assert response.status_code == 200


def test_semantic_models_endpoint_exists(api_url):
    response = httpx.get(f"{api_url}/api/semantic_models", timeout=10)
    assert response.status_code == 200


def test_openapi_schema_accessible(api_url):
    response = httpx.get(f"{api_url}/api/openapi.json", timeout=10)
    assert response.status_code == 200
    assert response.json()["info"]["title"] == "MetricAnchor API"
