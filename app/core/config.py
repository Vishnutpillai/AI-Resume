from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Intelligent Resume Job Matcher"
    app_env: str = "development"
    debug: bool = True

    database_url: str = (
        "postgresql://postgres:password@localhost:5432/resume_matcher"
    )

    vector_db: str = "faiss"

    embedding_model: str = (
        "sentence-transformers/all-MiniLM-L6-v2"
    )

    llm_provider: str = "ollama"
    llm_model: str = "qwen3:4b"

    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()