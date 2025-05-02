"""S4 routes for Simple Storage Service."""
from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import Response

from src.s4.s3_utils import (
    download_file_from_s3,
    ensure_bucket_exists,
    upload_file_to_s3,
)

router = APIRouter()

@router.post("/storage/upload")
async def upload_file(file: UploadFile = File(...)) -> dict:
    """Upload a file to S3."""
    try:
        # Ensure bucket exists
        if not ensure_bucket_exists():
            raise HTTPException(
                status_code=500,
                detail="Failed to ensure S3 bucket exists"
            ) from None
        
        # Read file content
        file_content = await file.read()
        
        # Upload to S3
        if not upload_file_to_s3(file.filename, file_content):
            raise HTTPException(
                status_code=500,
                detail="Failed to upload file to S3"
            ) from None
        
        return {"message": "File uploaded successfully", "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

@router.get("/storage/download/{file_key}")
def download_file(file_key: str) -> Response:
    """Download a file from S3."""
    try:
        # Ensure bucket exists
        if not ensure_bucket_exists():
            raise HTTPException(
                status_code=500,
                detail="Failed to ensure S3 bucket exists"
            ) from None
        
        # Download from S3
        file_content = download_file_from_s3(file_key)
        if not file_content:
            raise HTTPException(
                status_code=404,
                detail=f"File {file_key} not found"
            ) from None
        
        return Response(
            content=file_content,
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f"attachment; filename={file_key}"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
