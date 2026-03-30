from pathlib import Path
from pydantic import BaseModel
import os


class Settings(BaseModel):
    app_env: str = os.getenv("APP_ENV", "dev")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    data_dir: Path = Path(os.getenv("DATA_DIR", "./data"))
    enable_approval: bool = os.getenv("ENABLE_APPROVAL", "true").lower() == "true"


settings = Settings()
