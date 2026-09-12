from fastapi import APIRouter


router = APIRouter(
    prefix="/api/v1",
)


@router.get("/")
def api_root() -> dict[str, str]:
    return {
        "message": "Intelligent Resume Job Matcher API",
        "version": "1.0.0",
    }