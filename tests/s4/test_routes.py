"""Test suite for S4 routes."""
from __future__ import annotations

import json
from unittest.mock import patch

import pytest
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
        # Mock successful initial setup
        mock_ensure.return_value = True
        mock_upload.return_value = True
        mock_download.return_value = b"test content"
        mock_list.return_value = ["raw/test.txt"]
        yield {
            "ensure": mock_ensure,
            "upload": mock_upload,
            "download": mock_download,
            "list": mock_list
        }

def test_download_endpoint_success(mock_s3):
    """Test successful download endpoint."""
    with patch("requests.get") as mock_get:
        mock_get.return_value.json.return_value = {"states": []}
        mock_get.return_value.raise_for_status.return_value = None
        response = client.post("/api/s4/aircraft/download")
        assert response.status_code == 200
        assert response.json() == "OK"

def test_download_endpoint_bucket_error(mock_s3):
    """Test download endpoint with bucket error."""
    mock_s3["ensure"].return_value = False
    response = client.post("/api/s4/aircraft/download")
    assert response.status_code == 500
    assert "Failed to ensure S3 bucket exists" in response.json()["detail"]

def test_prepare_endpoint_success(mock_s3):
    """Test successful prepare endpoint."""
    mock_s3["download"].return_value = json.dumps({"states": [[1, 2, 3]]}).encode()
    response = client.post("/api/s4/aircraft/prepare")
    assert response.status_code == 200
    assert response.json() == "OK"

def test_prepare_endpoint_bucket_error(mock_s3):
    """Test prepare endpoint with bucket error."""
    mock_s3["ensure"].return_value = False
    response = client.post("/api/s4/aircraft/prepare")
    assert response.status_code == 500
    assert "Failed to ensure S3 bucket exists" in response.json()["detail"]

def test_prepare_endpoint_no_data(mock_s3):
    """Test prepare endpoint with no data."""
    mock_s3["list"].return_value = []
    response = client.post("/api/s4/aircraft/prepare")
    assert response.status_code == 404
    assert "No raw data found" in response.json()["detail"]

def test_download_endpoint_api_error(mock_s3):
    """Test download endpoint with OpenSky API error."""
    with patch("requests.get") as mock_get:
        mock_get.side_effect = Exception("API Error")
        response = client.post("/api/s4/aircraft/download")
        assert response.status_code == 500
        assert "Failed to fetch data from OpenSky API" in response.json()["detail"]

def test_prepare_endpoint_invalid_data(mock_s3):
    """Test prepare endpoint with invalid JSON data."""
    mock_s3["download"].return_value = b"invalid json"
    response = client.post("/api/s4/aircraft/prepare")
    assert response.status_code == 500
    assert "Failed to parse raw data" in response.json()["detail"]

def test_download_endpoint_upload_error(mock_s3):
    """Test download endpoint with S3 upload error."""
    with patch("requests.get") as mock_get:
        mock_get.return_value.json.return_value = {"states": []}
        mock_get.return_value.raise_for_status.return_value = None
        mock_s3["upload"].return_value = False
        response = client.post("/api/s4/aircraft/download")
        assert response.status_code == 500
        assert "Failed to upload data to S3" in response.json()["detail"]
