from pathlib import Path
from pydantic import BaseModel
import os


class Settings(BaseModel):
    app_env: str = os.getenv("APP_ENV", "dev")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    data_dir: Path = Path(os.getenv("DATA_DIR", "./data"))
    enable_approval: bool = os.getenv("ENABLE_APPROVAL", "true").lower() == "true"
    enable_judge: bool = os.getenv("ENABLE_JUDGE", "true").lower() == "true"
    sqlite_db_path: Path = Path(os.getenv("SQLITE_DB_PATH", "./support_desk.db"))
    model_provider: str = os.getenv("MODEL_PROVIDER", "openai")
    model_name: str = os.getenv("MODEL_NAME", "gpt-4.1-mini")
    model_temperature: float = float(os.getenv("MODEL_TEMPERATURE", "0"))
    max_llm_turns: int = int(os.getenv("MAX_LLM_TURNS", "3"))
    max_tool_calls: int = int(os.getenv("MAX_TOOL_CALLS", "3"))


settings = Settings()
