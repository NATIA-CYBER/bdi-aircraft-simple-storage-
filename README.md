# S4 - Simple Storage Service

Implementation of a Simple Storage Service using FastAPI and AWS S3. This service allows users to upload and download files using AWS S3 as the storage backend.

## Setup

1. Install dependencies:
```bash
poetry install
```

2. Set environment variables:
```bash
export BDI_S3_BUCKET=bdi-aircraft-simple-storage
```

3. Configure AWS credentials:
```bash
aws configure
```

## Running the API

Start the API server:
```bash
poetry run uvicorn src.main:app --reload
```

The API will be available at http://localhost:8000

## API Endpoints

### Upload File
- **Endpoint**: `POST /api/s4/storage/upload`
- **Description**: Upload a file to S3
- **Request**: Multipart form data with file
- **Response**: JSON with upload status and filename

### Download File
- **Endpoint**: `GET /api/s4/storage/download/{file_key}`
- **Description**: Download a file from S3
- **Parameters**: `file_key` - Name of the file to download
- **Response**: File content as attachment

## Testing

Run tests:
```bash
poetry run pytest
```

Run linting:
```bash
poetry run ruff check .
```

## Screenshots

Screenshots of the API in action can be found in the `screenshots` folder:
- `swagger-ui.png`: API documentation
- `download-endpoint.png`: Successful file download
- `prepare-endpoint.png`: Successful file upload
