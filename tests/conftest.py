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
    settings.data_dir = ROOT / "data"
    data_access.reset_state()
    return settings.data_dir
