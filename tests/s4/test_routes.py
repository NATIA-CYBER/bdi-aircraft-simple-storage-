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
        mock_download.return_value = json.dumps({"states": [["ICAO1", "data"]]}).encode()
        mock_list.return_value = ["raw/test.json"]
        yield {
            "ensure": mock_ensure,
            "upload": mock_upload,
            "download": mock_download,
            "list": mock_list
        }

@pytest.fixture
def mock_requests():
    """Mock requests for API calls."""
    with patch("src.s4.routes.requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = {"states": [["ICAO1", "data"]]}
        mock_get.return_value = mock_response
        yield mock_get

def test_download_success(mock_s3, mock_requests):
    """Test successful data download."""
    response = client.post("/api/s4/aircraft/download")
    assert response.status_code == 200
    assert response.json() == "OK"
    mock_s3["ensure"].assert_called_once()
    mock_s3["upload"].assert_called_once()

def test_download_with_limit(mock_s3, mock_requests):
    """Test download with custom file limit."""
    response = client.post("/api/s4/aircraft/download?file_limit=50")
    assert response.status_code == 200
    assert response.json() == "OK"

def test_download_bucket_error(mock_s3, mock_requests):
    """Test download when bucket creation fails."""
    mock_s3["ensure"].return_value = False
    response = client.post("/api/s4/aircraft/download")
    assert response.status_code == 500
    assert "Failed to ensure S3 bucket exists" in response.json()["detail"]

def test_download_api_error(mock_s3, mock_requests):
    """Test download when API request fails."""
    mock_requests.side_effect = requests.RequestException("API Error")
    response = client.post("/api/s4/aircraft/download")
    assert response.status_code == 500
    assert "Failed to fetch data from API" in response.json()["detail"]

def test_prepare_success(mock_s3):
    """Test successful data preparation."""
    response = client.post("/api/s4/aircraft/prepare")
    assert response.status_code == 200
    assert response.json() == "OK"
    mock_s3["list"].assert_called_once()
    mock_s3["download"].assert_called_once()
    mock_s3["upload"].assert_called_once()

def test_prepare_no_raw_data(mock_s3):
    """Test prepare when no raw data exists."""
    mock_s3["list"].return_value = []
    response = client.post("/api/s4/aircraft/prepare")
    assert response.status_code == 404
    assert "No raw data found" in response.json()["detail"]

def test_prepare_invalid_data(mock_s3):
    """Test prepare with invalid raw data."""
    mock_s3["download"].return_value = json.dumps({"invalid": "data"}).encode()
    response = client.post("/api/s4/aircraft/prepare")
    assert response.status_code == 404
    assert "No valid data found" in response.json()["detail"]

def test_prepare_upload_error(mock_s3):
    """Test prepare when upload fails."""
    mock_s3["upload"].return_value = False
    response = client.post("/api/s4/aircraft/prepare")
    assert response.status_code == 500
    assert "Failed to upload prepared data" in response.json()["detail"]
