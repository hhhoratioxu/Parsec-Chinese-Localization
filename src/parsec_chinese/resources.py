from pathlib import Path
import sys


def resource_dir() -> Path:
    for root in (Path(getattr(sys, "_MEIPASS", "")), Path(__file__).resolve().parents[2], Path(sys.prefix)):
        if (root / "locales" / "en.json").is_file():
            return root / "locales"
    raise FileNotFoundError("Translation resources are missing; reinstall the companion.")
