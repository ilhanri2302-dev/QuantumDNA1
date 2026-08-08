"""Shared pytest fixtures for the QuantumDNA backend tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Make the backend modules importable from the tests directory.
BACKEND_DIR = Path(__file__).resolve().parent.parent

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


@pytest.fixture
def sample_target() -> Path:
    """The repository's demonstration target."""

    return BACKEND_DIR.parent / "sample-target"


@pytest.fixture
def temp_target(tmp_path: Path) -> Path:
    """A disposable directory that can be populated per test."""

    return tmp_path


@pytest.fixture
def api_client():
    """FastAPI TestClient against the real application."""

    from fastapi.testclient import TestClient

    from main import app

    with TestClient(app) as client:
        yield client
