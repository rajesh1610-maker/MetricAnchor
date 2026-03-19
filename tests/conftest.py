"""Top-level test configuration for full-stack integration tests."""

import os

import pytest

# Point at the running API (docker-compose or local dev server)
API_BASE_URL = os.getenv("TEST_API_URL", "http://localhost:8000")


@pytest.fixture(scope="session")
def api_url():
    return API_BASE_URL
