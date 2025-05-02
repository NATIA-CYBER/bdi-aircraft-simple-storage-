"""Test suite for S3 utilities."""
from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

import pytest
from botocore.exceptions import ClientError

from src.s4.s3_utils import (
    download_file_from_s3,
    ensure_bucket_exists,
    list_files_in_s3,
    upload_file_to_s3,
)


@pytest.fixture
def mock_s3_client():
    """Mock S3 client."""
    with patch("src.s4.s3_utils.get_s3_client") as mock_get_client:
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        yield mock_client

def test_ensure_bucket_exists_success(mock_s3_client):
    """Test successful bucket existence check."""
    mock_s3_client.head_bucket.return_value = True
    assert ensure_bucket_exists() is True
    mock_s3_client.head_bucket.assert_called_once()

def test_ensure_bucket_create_success(mock_s3_client):
    """Test successful bucket creation."""
    mock_s3_client.head_bucket.side_effect = ClientError(
        {"Error": {"Code": "404"}}, "head_bucket"
    )
    assert ensure_bucket_exists() is True
    mock_s3_client.create_bucket.assert_called_once()

def test_ensure_bucket_create_failure(mock_s3_client):
    """Test failed bucket creation."""
    mock_s3_client.head_bucket.side_effect = ClientError(
        {"Error": {"Code": "404"}}, "head_bucket"
    )
    mock_s3_client.create_bucket.side_effect = ClientError(
        {"Error": {"Code": "500"}}, "create_bucket"
    )
    assert ensure_bucket_exists() is False

def test_upload_file_success(mock_s3_client):
    """Test successful file upload."""
    assert upload_file_to_s3("test.json", b"data") is True
    mock_s3_client.put_object.assert_called_once()

def test_upload_file_failure(mock_s3_client):
    """Test failed file upload."""
    mock_s3_client.put_object.side_effect = ClientError(
        {"Error": {"Code": "500"}}, "put_object"
    )
    assert upload_file_to_s3("test.json", b"data") is False

def test_download_file_success(mock_s3_client):
    """Test successful file download."""
    mock_body = MagicMock()
    mock_body.read.return_value = b"data"
    mock_s3_client.get_object.return_value = {"Body": mock_body}
    assert download_file_from_s3("test.json") == b"data"

def test_download_file_failure(mock_s3_client):
    """Test failed file download."""
    mock_s3_client.get_object.side_effect = ClientError(
        {"Error": {"Code": "500"}}, "get_object"
    )
    assert download_file_from_s3("test.json") is None

def test_list_files_success(mock_s3_client):
    """Test successful file listing."""
    mock_s3_client.list_objects_v2.return_value = {
        "Contents": [{"Key": "test1.json"}, {"Key": "test2.json"}]
    }
    assert list_files_in_s3() == ["test1.json", "test2.json"]

def test_list_files_empty(mock_s3_client):
    """Test empty file listing."""
    mock_s3_client.list_objects_v2.return_value = {}
    assert list_files_in_s3() == []

def test_list_files_failure(mock_s3_client):
    """Test failed file listing."""
    mock_s3_client.list_objects_v2.side_effect = ClientError(
        {"Error": {"Code": "500"}}, "list_objects_v2"
    )
    assert list_files_in_s3() == []

def test_invalid_bucket_name():
    """Test invalid bucket name validation."""
    with patch.dict(os.environ, {"BDI_S3_BUCKET": "invalid-name"}):
        with pytest.raises(ValueError) as exc:
            from importlib import reload
            
            from src.s4 import s3_utils
            reload(s3_utils)
        assert "must start with 'bdi-aircraft'" in str(exc.value)
