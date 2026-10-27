"""Tests never connect to a developer's configured production database."""

import pytest

import cloud_storage as cloud


@pytest.fixture(autouse=True)
def offline_backend(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setattr(cloud, "_POSTGRES_URL", None)
