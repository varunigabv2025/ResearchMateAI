"""
Pytest configuration and fixtures.
"""
import os
import sys

# CRITICAL: Mock sentence_transformers module BEFORE it's imported by any app code
import numpy as np
from unittest.mock import MagicMock


def create_mock_sentence_transformer(*args, **kwargs):
    """Create a mock SentenceTransformer that returns 1024-dim vectors."""
    mock_model = MagicMock()
    mock_model.device = kwargs.get('device', 'cpu')
    
    def mock_encode(text, **encode_kwargs):
        if isinstance(text, list):
            return np.array([[0.1 + i * 0.01] * 1024 for i in range(len(text))])
        else:
            return np.array([0.1] * 1024)
    
    mock_model.encode = MagicMock(side_effect=mock_encode)
    mock_model.prompts = {"query": "test query prompt"}
    return mock_model


# Create a fake sentence_transformers module
class MockSentenceTransformersModule:
    SentenceTransformer = create_mock_sentence_transformer


# Install the fake module BEFORE any imports
sys.modules['sentence_transformers'] = MockSentenceTransformersModule()


import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db


# Use in-memory SQLite for testing
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db_session():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    """Create a test client with overridden database dependency."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
