from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Tavi"
    debug: bool = False
    database_path: str = "sqlite:///memory.db"
    log_level: str = "INFO"

    model_config = {"env_file": ".env"}

settings = Settings()
