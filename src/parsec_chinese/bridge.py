"""Read-only public settings mirror with an explicit navigation allowlist.

Never captures screenshots, edits values, reads edit boxes or logs UI trees.
Every action reacquires and checks both process identity and UI version.
"""
from dataclasses import dataclass
from pathlib import Path
import re
from .detection import KNOWN_APP, KNOWN_UI

NAVIGATION = {"computers", "settings", "Client", "Host", "Network", "Gamepad", "Hotkeys", "Experimental", "Approved Apps"}
PRIVATE_LABELS = {"Host Name"}
NUMERIC = re.compile(r"(?:\d+(?:\.\d+)?)(?:\s*(?:Mbps|ms|FPS|Hz|kHz))?|\d+\s*[x×]\s*\d+|H\.26[45](?: \(HEVC\))?|\d+:\d+")


class BridgeError(RuntimeError):
    pass


@dataclass(frozen=True)
class SettingRow:
    label: str
    value: str = ""
    enabled: bool = True


@dataclass(frozen=True)
class Snapshot:
    rows: tuple[SettingRow, ...] = ()
    navigation: tuple[str, ...] = ()
    observed: int = 0
    translated: int = 0
    ui_version: str = ""


def safe_value(value, translations):
    value = str(value).strip()
    if value.casefold() in translations.lookup or NUMERIC.fullmatch(value):
        return value
    return ""  # A device name or arbitrary text could identify a user.


class WindowsBridge:
    def __init__(self, installation, translations):
        self.installation = installation
        self.translations = translations

    def _window(self):
        if not self.installation.live_supported:
            raise BridgeError("unsupported_version")
        import psutil
        from pywinauto import Desktop
        windows = []
        for w in Desktop(backend="uia").windows(title="Parsec"):
            try:
                if Path(psutil.Process(w.process_id()).exe()).resolve() == self.installation.executable.resolve():
                    windows.append(w)
            except (OSError, psutil.Error):
                continue
        if len(windows) != 1:
            raise BridgeError("open_parsec")
        window = windows[0]
        if window.is_minimized():
            raise BridgeError("open_parsec")
        documents = window.descendants(control_type="Document")
        if len(documents) != 1 or documents[0].element_info.automation_id != "RootWebArea":
            raise BridgeError("unsupported_ui")
        # Only known version/navigation buttons are kept; nothing is printed/logged.
        buttons = window.descendants(control_type="Button")
        names = {b.element_info.name for b in buttons}
        if f"UI {KNOWN_UI}" not in names or not any(n.startswith(f"APP {KNOWN_APP} - ") for n in names):
            raise BridgeError("unsupported_ui")
        if not {"computers", "settings"}.issubset(names):
            raise BridgeError("unsupported_ui")
        return window, buttons

    def read(self):
        window, buttons = self._window()
        navigation = tuple(n for n in sorted(NAVIGATION) if any(b.element_info.name == n and b.is_enabled() for b in buttons))
        rows = {}
        observed = 0
        # Read actual table rows only, not the username header, footer or host list.
        for table in window.descendants(control_type="Table"):
            for row in table.children():
                cells = row.children()
                if len(cells) != 2:
                    continue
                headings = cells[0].descendants()
                # Names may be arbitrary; keep only exact known public labels.
                labels = [h.element_info.name for h in headings
                          if h.element_info.name.casefold() in self.translations.lookup]
                observed += 1
                if not labels:
                    continue
                label = labels[0]
                controls = [c for c in cells[1].descendants()
                            if c.element_info.control_type in ("ComboBox", "CheckBox", "Button", "Spinner", "Edit")
                            and c.element_info.name == label]
                value = ""
                enabled = True
                if controls and label not in PRIVATE_LABELS:
                    control = controls[0]
                    enabled = control.is_enabled()
                    try:
                        kind = control.element_info.control_type
                        if kind == "ComboBox":
                            value = safe_value(control.iface_value.CurrentValue, self.translations)
                        elif kind in ("CheckBox", "Button"):
                            value = {0: "Off", 1: "On", 2: "Mixed"}.get(control.iface_toggle.CurrentToggleState, "")
                        elif kind == "Spinner":
                            value = safe_value(control.iface_range_value.CurrentValue, self.translations)
                        # Edit boxes are deliberately never read, even if labelled.
                    except Exception:
                        value = ""
                rows[label] = SettingRow(label, value, enabled)
        return Snapshot(tuple(rows.values()), navigation, observed, len(rows), KNOWN_UI)

    def navigate(self, label):
        if label not in NAVIGATION:
            raise BridgeError("navigation_refused")
        _, buttons = self._window()
        matches = [b for b in buttons if b.element_info.name == label and b.is_enabled()]
        if len(matches) != 1:
            raise BridgeError("navigation_unavailable")
        try:
            matches[0].invoke()  # No mouse coordinates, auth, or value mutation.
        except Exception as exc:
            raise BridgeError("navigation_unavailable") from exc
