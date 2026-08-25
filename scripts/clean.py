from __future__ import annotations

import os
import shutil
import stat
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DIRECTORIES = (
    "build",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
)


def main() -> None:
    for directory in DIRECTORIES:
        _remove(ROOT / directory)
    for root in ("src", "tests"):
        for directory in (ROOT / root).rglob("__pycache__"):
            _remove(directory)


def _remove(path: Path) -> None:
    if not path.exists():
        return
    try:
        shutil.rmtree(path, onexc=_make_writable)
    except OSError as exc:
        print(f"warning: could not remove {path}: {exc}")


def _make_writable(function: Any, path: str, excinfo: BaseException) -> None:
    try:
        os.chmod(path, stat.S_IWRITE)
    except OSError as exc:
        print(f"warning: could not change permissions for {path}: {exc}")
        return
    try:
        function(path)
    except OSError as exc:
        print(f"warning: could not remove {path}: {excinfo}; retry failed: {exc}")


if __name__ == "__main__":
    main()
