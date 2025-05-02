# S4 - Aircraft API with S3 Storage

Implementation of `/api/s4/aircraft/download` and `/api/s4/aircraft/prepare` endpoints with AWS S3 integration.

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

- `POST /api/s4/aircraft/download`: Download aircraft data to S3
- `POST /api/s4/aircraft/prepare`: Prepare downloaded data

## Testing

Run tests:
```bash
poetry run pytest
```

## Deployment

1. Launch EC2 instance
2. Configure security groups for HTTP access
3. Deploy API
4. Access via http://[EC2-IP]/docs
