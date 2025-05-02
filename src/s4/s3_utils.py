"""S3 utilities for storing and retrieving aircraft data."""
import os

import boto3
from botocore.exceptions import ClientError

# Get bucket name from environment variable
BUCKET_NAME = os.getenv("BDI_S3_BUCKET")
if not BUCKET_NAME:
    raise ValueError("BDI_S3_BUCKET environment variable must be set")

if not BUCKET_NAME.startswith("bdi-aircraft"):
    raise ValueError("S3 bucket name must start with 'bdi-aircraft'")

def get_s3_client():
    """Get an S3 client."""
    return boto3.client('s3')

def ensure_bucket_exists() -> bool:
    """Ensure the S3 bucket exists, create if it doesn't."""
    s3 = get_s3_client()
    try:
        s3.head_bucket(Bucket=BUCKET_NAME)
        return True
    except ClientError:
        try:
            s3.create_bucket(Bucket=BUCKET_NAME)
            return True
        except ClientError as e:
            print(f"Error creating bucket: {e}")
            return False

def upload_file_to_s3(file_key: str, file_data: bytes) -> bool:
    """Upload a file to S3."""
    s3 = get_s3_client()
    try:
        s3.put_object(Bucket=BUCKET_NAME, Key=file_key, Body=file_data)
        return True
    except ClientError as e:
        print(f"Error uploading file: {e}")
        return False

def download_file_from_s3(file_key: str) -> bytes:
    """Download a file from S3."""
    s3 = get_s3_client()
    try:
        response = s3.get_object(Bucket=BUCKET_NAME, Key=file_key)
        return response['Body'].read()
    except ClientError as e:
        print(f"Error downloading file: {e}")
        return None

def list_files_in_s3(prefix: str = "") -> list:
    """List files in the S3 bucket with given prefix."""
    s3 = get_s3_client()
    try:
        response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=prefix)
        return [obj['Key'] for obj in response.get('Contents', [])]
    except ClientError as e:
        print(f"Error listing files: {e}")
        return []
