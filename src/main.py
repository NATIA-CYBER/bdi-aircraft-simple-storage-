"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from src.s4.routes import router as s4_router

app = FastAPI(
    title="Aircraft API with S3",
    description="S4 Assignment - Aircraft API with AWS S3 Integration",
    version="0.1.0",
)

app.include_router(s4_router, prefix="/api/s4")

@app.get("/")
def root():
    """Redirect to API documentation."""
    return RedirectResponse(url="/docs")
