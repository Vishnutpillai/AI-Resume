from fastapi import FastAPI

from app.api.recommendations import router as recommendations_router
from app.api.analysis import router as analysis_router
from app.api.export import router as export_router
from app.api.health import router as health_router
from app.api.job import router as job_router
from app.api.optimization import router as optimization_router
from app.api.resume import router as resume_router
from app.api.routes import router as api_router
from app.core.config import settings
from app.core.logging import setup_logging


setup_logging()


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description=(
        "AI-powered Resume and Job Matching System "
        "with RAG and multi-agent intelligence."
    ),
)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "Intelligent Resume Job Matcher API",
        "version": "1.0.0",
        "environment": settings.app_env,
    }


app.include_router(health_router)
app.include_router(api_router)
app.include_router(resume_router)
app.include_router(job_router)
app.include_router(analysis_router)
app.include_router(optimization_router)
app.include_router(export_router)
app.include_router(recommendations_router)