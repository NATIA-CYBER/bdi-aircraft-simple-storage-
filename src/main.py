"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from src.s4.routes import router as s4_router

app = FastAPI(
    title="Simple Storage Service API",
    description="S4 Assignment - Simple Storage Service with AWS S3",
    version="0.1.0",
)

app.include_router(s4_router, prefix="/api/s4")

@app.get("/")
def root():
    """Redirect to API documentation."""
    return RedirectResponse(url="/docs")
