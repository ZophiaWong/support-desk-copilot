import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import data_access
from app.config import settings


@pytest.fixture(autouse=True)
def use_real_data_dir() -> Path:
    original_data_dir = settings.data_dir
    original_db_path = settings.sqlite_db_path
    original_enable_judge = settings.enable_judge
    original_max_llm_turns = settings.max_llm_turns
    original_max_tool_calls = settings.max_tool_calls
    original_model_provider = settings.model_provider
    settings.data_dir = ROOT / "data"
    settings.sqlite_db_path = ROOT / "test_support_desk.db"
    settings.enable_judge = True
    settings.max_llm_turns = 3
    settings.max_tool_calls = 3
    settings.model_provider = "openai"
    data_access.reset_state()
    from app.persistence import SQLiteStore

    SQLiteStore(settings.sqlite_db_path).reset()
    yield settings.data_dir
    SQLiteStore(settings.sqlite_db_path).reset()
    settings.data_dir = original_data_dir
    settings.sqlite_db_path = original_db_path
    settings.enable_judge = original_enable_judge
    settings.max_llm_turns = original_max_llm_turns
    settings.max_tool_calls = original_max_tool_calls
    settings.model_provider = original_model_provider
