#!/bin/bash

# Install dependencies
pip install -r requirements.txt

# Run the FastAPI application with sudo to bind to port 80
sudo uvicorn src.main:app --host 0.0.0.0 --port 80
