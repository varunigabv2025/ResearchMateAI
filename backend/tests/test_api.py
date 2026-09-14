"""
Tests for API endpoints.
"""
import pytest
from fastapi import status


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "healthy"
    assert "app_name" in data
    assert "version" in data


def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "app" in data
    assert "version" in data
    assert "message" in data
    assert "docs" in data


def test_list_papers_empty(client):
    """Test listing papers when database is empty."""
    response = client.get("/api/papers/")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "papers" in data
    assert "total" in data
    assert data["total"] == 0
    assert len(data["papers"]) == 0


def test_get_nonexistent_paper(client):
    """Test getting a paper that doesn't exist."""
    fake_uuid = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/api/papers/{fake_uuid}")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert "detail" in data


def test_upload_non_pdf_file(client):
    """Test uploading a non-PDF file."""
    files = {"file": ("test.txt", b"This is not a PDF", "text/plain")}
    response = client.post("/api/papers/upload", files=files)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert "detail" in data
    assert "PDF" in data["detail"]


def test_upload_invalid_pdf(client):
    """Test uploading an invalid PDF file."""
    # Create fake PDF content (not a valid PDF)
    files = {"file": ("test.pdf", b"This is not a real PDF content", "application/pdf")}
    response = client.post("/api/papers/upload", files=files)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert "detail" in data


def test_delete_nonexistent_paper(client):
    """Test deleting a paper that doesn't exist."""
    fake_uuid = "00000000-0000-0000-0000-000000000000"
    response = client.delete(f"/api/papers/{fake_uuid}")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_list_papers_pagination(client):
    """Test pagination parameters."""
    response = client.get("/api/papers/?skip=0&limit=10")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "papers" in data
    assert "total" in data
