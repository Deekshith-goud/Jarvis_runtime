import sys
import uuid
from pathlib import Path

import pytest

repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))


@pytest.fixture(scope="session", autouse=True)
def add_repo_to_path():
    return str(repo_root)


@pytest.fixture
def isolated_cwd(monkeypatch):
    sandbox = repo_root / "tests" / ".tmp" / uuid.uuid4().hex
    sandbox.mkdir(parents=True, exist_ok=True)
    monkeypatch.chdir(sandbox)
    return sandbox


@pytest.fixture
def no_user_config(monkeypatch):
    import core.entity_registry as entity_registry

    monkeypatch.setattr(entity_registry, "CONFIG_FILE", "__missing_config__.json", raising=True)
    return entity_registry
