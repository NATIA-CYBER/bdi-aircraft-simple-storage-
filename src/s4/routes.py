"""S4 routes for aircraft data with S3 storage."""
from __future__ import annotations

import json

import requests
from fastapi import APIRouter, HTTPException, Query

from src.s4.s3_utils import (
    download_file_from_s3,
    ensure_bucket_exists,
    list_files_in_s3,
    upload_file_to_s3,
)

router = APIRouter()

@router.post("/aircraft/download")
def download_data(file_limit: int = Query(default=100)) -> str:
    """Download aircraft data and store in S3."""
    base_url = "https://opensky-network.org/api/states/all"
    
    try:
        # Ensure bucket exists
        if not ensure_bucket_exists():
            raise HTTPException(
                status_code=500,
                detail="Failed to ensure S3 bucket exists"
            ) from None
        
        try:
            # Download data from API
            response = requests.get(base_url)
            response.raise_for_status()
            data = response.json()
        except (requests.RequestException, Exception) as e:
            raise HTTPException(
                status_code=500,
                detail="Failed to fetch data from OpenSky API"
            ) from e
        
        # Save raw data to S3
        file_key = f"raw/aircraft_data_{file_limit}.json"
        if not upload_file_to_s3(file_key, json.dumps(data).encode()):
            raise HTTPException(
                status_code=500,
                detail="Failed to upload data to S3"
            ) from None
        
        return "OK"
    except HTTPException:
        raise

@router.post("/aircraft/prepare")
def prepare_data() -> str:
    """Prepare downloaded data from S3."""
    try:
        # Ensure bucket exists
        if not ensure_bucket_exists():
            raise HTTPException(
                status_code=500,
                detail="Failed to ensure S3 bucket exists"
            ) from None
        
        # List files in raw directory
        raw_files = list_files_in_s3("raw/")
        if not raw_files:
            raise HTTPException(
                status_code=404,
                detail="No raw data found. Please download data first."
            ) from None
        
        # Process each file
        prepared_data = []
        for file_key in raw_files:
            raw_data = download_file_from_s3(file_key)
            if raw_data:
                data = json.loads(raw_data)
                if 'states' in data:
                    prepared_data.extend(data['states'])
        
        if not prepared_data:
            raise HTTPException(
                status_code=404,
                detail="No valid data found in raw files."
            ) from None
        
        # Save prepared data to S3
        prepared_file = "prepared/aircraft_data.json"
        if not upload_file_to_s3(prepared_file, json.dumps(prepared_data).encode()):
            raise HTTPException(
                status_code=500,
                detail="Failed to upload prepared data to S3"
            ) from None
        
        return "OK"
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="Failed to parse raw data"
        ) from None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
