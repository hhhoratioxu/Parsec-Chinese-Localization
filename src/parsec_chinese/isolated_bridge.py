"""Bounded UIA calls. A stalled provider cannot trap the companion's GUI."""
from dataclasses import asdict
from pathlib import Path
import json
import subprocess
import sys
import tempfile
from .bridge import WindowsBridge, BridgeError, Snapshot, SettingRow, NAVIGATION, safe_value
from .detection import detect
from .translations import Translations


class IsolatedBridge:
    def __init__(self, installation, translations, timeout=18):
        self.installation, self.translations, self.timeout = installation, translations, timeout

    def _call(self, operation, label=""):
        if not self.installation.live_supported:
            raise BridgeError("unsupported_version")
        if operation == "navigate" and label not in NAVIGATION:
            raise BridgeError("navigation_refused")
        with tempfile.TemporaryDirectory(prefix="pcl-bridge-") as temp:
            output = Path(temp) / "result.json"
            command = [sys.executable] if getattr(sys, "frozen", False) else [sys.executable, "-m", "parsec_chinese"]
            command += ["--bridge-worker", operation, "--bridge-output", str(output)]
            if label:
                command += ["--label", label]
            kwargs = {"creationflags": subprocess.CREATE_NO_WINDOW} if sys.platform == "win32" else {}
            try:
                # No stdout pipes: COM-spawned descendants can retain inherited pipe
                # handles and otherwise trap communicate() even after a timeout.
                subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                               timeout=self.timeout, check=True, **kwargs)
                if not output.is_file() or output.stat().st_size > 65536:
                    raise BridgeError("unsupported_ui")
                result = json.loads(output.read_text(encoding="utf-8"))
            except subprocess.TimeoutExpired as exc:
                # subprocess.run kills only our helper, never the Parsec process.
                raise BridgeError("provider_timeout") from exc
            except (OSError, ValueError, subprocess.CalledProcessError) as exc:
                raise BridgeError("unsupported_ui") from exc
            if "error" in result:
                raise BridgeError(result["error"])
            return result.get("snapshot")

    def read(self):
        data = self._call("read")
        rows = tuple(SettingRow(r["label"], safe_value(r["value"], self.translations), r["enabled"])
                     for r in data["rows"] if r["label"].casefold() in self.translations.lookup)
        navigation = tuple(n for n in data["navigation"] if n in NAVIGATION)
        return Snapshot(rows, navigation, data["observed"], len(rows), data["ui_version"])

    def navigate(self, label):
        self._call("navigate", label)


def worker(operation, output, label=""):
    path = Path(output)
    # Worker IPC cannot be redirected onto an official resource or arbitrary file.
    parent = path.parent
    if path.name != "result.json" or not parent.name.startswith("pcl-bridge-") or parent.parent.resolve() != Path(tempfile.gettempdir()).resolve():
        return 2
    if parent.is_symlink() or path.is_symlink() or path.exists():
        return 2
    try:
        bridge = WindowsBridge(detect(), Translations())
        if operation == "read":
            result = {"snapshot": asdict(bridge.read())}
        else:
            bridge.navigate(label)
            result = {"snapshot": None}
    except BridgeError as exc:
        result = {"error": str(exc)}
    except Exception:
        result = {"error": "unsupported_ui"}
    with path.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, ensure_ascii=False)
    return 0
