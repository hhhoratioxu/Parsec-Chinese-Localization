"""Own preferences only. No API accepts a Parsec resource target."""
from contextlib import contextmanager
from dataclasses import dataclass, asdict
from pathlib import Path
import json
import os
import sys
import tempfile
from .translations import LANGUAGES


def data_dir():
    if sys.platform == "win32":
        return Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData/Local")) / "ParsecChineseLocalization"
    if sys.platform == "darwin":
        return Path.home() / "Library/Application Support/ParsecChineseLocalization"
    return Path.home() / ".local/share/ParsecChineseLocalization"


@dataclass(frozen=True)
class Preferences:
    schema: int = 1
    language: str = "zh-CN"
    theme: str = "system"

    def __post_init__(self):
        if self.schema != 1 or self.language not in LANGUAGES or self.theme not in ("system", "light", "dark"):
            raise ValueError("Invalid preferences")


class StateStore:
    def __init__(self, root=None):
        self.root = Path(root) if root is not None else data_dir()

    def _safe(self, name):
        # Reject symlinks/junctions, including ancestors, instead of following redirects.
        for path in (self.root, *self.root.parents, self.root / name):
            if path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction()):
                raise ValueError("Redirected preference path refused")
        self.root.mkdir(parents=True, exist_ok=True)
        return self.root / name

    @contextmanager
    def _lock(self):
        lock = self._safe("preferences.lock")
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        try:
            yield
        finally:
            os.close(fd)
            lock.unlink()

    def load(self):
        path = self._safe("preferences.json")
        return self._decode(path.read_bytes()) if path.exists() else Preferences()

    @staticmethod
    def _decode(data):
        return Preferences(**json.loads(data.decode("utf-8")))

    def _atomic(self, name, data):
        target = self._safe(name)
        self._decode(data)
        fd, tmp = tempfile.mkstemp(prefix=".preferences-", dir=self.root)
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            self._safe(name)
            os.replace(tmp, target)
        finally:
            Path(tmp).unlink(missing_ok=True)

    def save(self, preferences):
        new = json.dumps(asdict(preferences), ensure_ascii=False, indent=2).encode("utf-8")
        with self._lock():
            path = self._safe("preferences.json")
            old = path.read_bytes() if path.exists() else json.dumps(asdict(Preferences())).encode()
            self._decode(old)  # Corruption must not silently destroy a backup.
            if path.exists() and self._decode(old) == preferences:
                return False
            self._atomic("preferences.backup.json", old)
            self._atomic("preferences.json", new)  # Failure leaves the original intact.
            return True

    def restore_backup(self):
        with self._lock():
            backup = self._safe("preferences.backup.json").read_bytes()
            self._atomic("preferences.json", backup)
            return self._decode(backup)

    def clear(self):
        # Only our fixed filenames are removed; never recurse or touch Parsec.
        for name in ("preferences.json", "preferences.backup.json", "events.log"):
            self._safe(name).unlink(missing_ok=True)

    def log(self, event):
        allowed = {"language_changed", "theme_changed", "read_succeeded", "operation_failed", "update_checked"}
        if event not in allowed:
            raise ValueError("Only fixed event names may be logged")
        path = self._safe("events.log")
        if path.exists() and path.stat().st_size > 65536:
            path.write_text("", encoding="utf-8")
        with path.open("a", encoding="utf-8") as stream:
            stream.write(event + "\n")
