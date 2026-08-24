from __future__ import annotations

import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
BUILD = ROOT / "build"
ZIP = BUILD / "email_service.zip"


def main() -> None:
    BUILD.mkdir(exist_ok=True)
    if ZIP.exists():
        ZIP.unlink()
    with zipfile.ZipFile(ZIP, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(SRC.rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts:
                archive.write(path, path.relative_to(SRC))
    shutil.copyfile(ZIP, BUILD / "form_intake.zip")
    shutil.copyfile(ZIP, BUILD / "email_worker.zip")
    shutil.copyfile(ZIP, BUILD / "email_events.zip")


if __name__ == "__main__":
    main()
