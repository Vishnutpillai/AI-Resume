import logging

from fastapi import FastAPI

from app.core.config import settings
from app.core.logging import setup_logging


setup_logging()

logger = logging.getLogger("resume_matcher")


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="AI-powered Resume and Job Matching System",
)


@app.get("/")
def root():
    return {
        "message": "Intelligent Resume Job Matcher API",
        "version": "0.1.0",
        "environment": settings.app_env,
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": settings.app_name,
    }