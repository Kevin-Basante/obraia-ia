"""Shared test setup: a client with a known token and a replaceable analyzer."""

import pytest
from fastapi.testclient import TestClient

from app.analyzers.factory import get_analyzer
from app.analyzers.fake import FakeAnalyzer
from app.config import Settings, get_settings
from app.main import app

TOKEN = "test-token"
PDF_BYTES = b"%PDF-1.7\nfake blueprint"


def make_settings(**overrides) -> Settings:
    values = {
        "analyzer": "fake",
        "gemini_api_key": "",
        "gemini_model": "gemini-test",
        "service_token": TOKEN,
        "max_file_mb": 1,
        "gemini_fallback_model": "",
        "gemini_retries": 0,
    }
    values.update(overrides)
    return Settings(**values)


@pytest.fixture
def settings() -> Settings:
    return make_settings()


@pytest.fixture
def analyzer():
    return FakeAnalyzer()


@pytest.fixture
def client(settings, analyzer):
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_analyzer] = lambda: analyzer
    yield TestClient(app)
    app.dependency_overrides.clear()


def auth() -> dict:
    return {"X-Service-Token": TOKEN}
