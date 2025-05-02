"""Test suite for S4 routes."""
from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest
import requests
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)

@pytest.fixture
def mock_s3():
    """Mock S3 utilities."""
    with patch("src.s4.routes.ensure_bucket_exists") as mock_ensure, \
         patch("src.s4.routes.upload_file_to_s3") as mock_upload, \
         patch("src.s4.routes.download_file_from_s3") as mock_download, \
         patch("src.s4.routes.list_files_in_s3") as mock_list:
        mock_ensure.return_value = True
        mock_upload.return_value = True
        response = client.post(
            "/api/s4/storage/upload",
            files={"file": ("test.txt", b"test content")}
        )
        assert response.status_code == 200
        assert response.json() == {
            "message": "File uploaded successfully",
            "filename": "test.txt"
        }

def test_upload_bucket_error(mock_s3):
    mock_s3.return_value = False
    response = client.post(
        "/api/s4/storage/upload",
        files={"file": ("test.txt", b"test content")}
    )
    assert response.status_code == 500
    assert "Failed to ensure S3 bucket exists" in response.json()["detail"]

def test_upload_s3_error(mock_s3):
    with patch("src.s4.routes.upload_file_to_s3") as mock_upload:
        mock_upload.return_value = False
        response = client.post(
            "/api/s4/storage/upload",
            files={"file": ("test.txt", b"test content")}
        )
        assert response.status_code == 500
        assert "Failed to upload file to S3" in response.json()["detail"]

def test_download_success(mock_s3):
    with patch("src.s4.routes.download_file_from_s3") as mock_download:
        mock_download.return_value = b"test content"
        response = client.get("/api/s4/storage/download/test.txt")
        assert response.status_code == 200
        assert response.content == b"test content"
        assert response.headers["content-type"] == "application/octet-stream"
        assert "attachment; filename=test.txt" in response.headers["content-disposition"]

def test_download_bucket_error(mock_s3):
    mock_s3.return_value = False
    response = client.get("/api/s4/storage/download/test.txt")
    assert response.status_code == 500
    assert "Failed to ensure S3 bucket exists" in response.json()["detail"]

def test_download_not_found(mock_s3):
    with patch("src.s4.routes.download_file_from_s3") as mock_download:
        mock_download.return_value = None
        response = client.get("/api/s4/storage/download/test.txt")
        assert response.status_code == 404
        assert "File test.txt not found" in response.json()["detail"]
