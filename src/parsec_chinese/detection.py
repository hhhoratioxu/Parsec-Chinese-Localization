from dataclasses import dataclass
from pathlib import Path
import json
import os
import plistlib
import re
import subprocess
import sys

KNOWN_APP = "150-105c"
KNOWN_UI = "150-33661022248"


@dataclass(frozen=True)
class Installation:
    executable: Path | None = None
    version: str = "unknown"
    signature_valid: bool = False
    platform: str = sys.platform
    error: str = ""

    @property
    def installed(self):
        return self.executable is not None and self.executable.is_file()

    @property
    def live_supported(self):
        return self.installed and self.platform == "win32" and self.signature_valid and self.version == KNOWN_APP


def active_version(root):
    """Read only the library filename, never account or configuration data."""
    try:
        path = Path(root) / "appdata.json"
        if path.stat().st_size > 65536 or path.is_symlink():
            return "unknown"
        name = json.loads(path.read_text(encoding="utf-8")).get("so_name", "")
        if not isinstance(name, str):
            return "unknown"
        match = re.fullmatch(r"parsecd-(\d+-\d+[a-z]?)\.dll", name)
        return match.group(1) if match else "unknown"
    except (OSError, ValueError, AttributeError):
        return "unknown"


def windows_signature(executable):
    # No interpolation into command text; paths arrive through an environment variable.
    env = dict(os.environ, PCL_VERIFY_PATH=str(executable))
    script = "$s = Get-AuthenticodeSignature -LiteralPath $env:PCL_VERIFY_PATH; if ($s.Status -eq 'Valid' -and $s.SignerCertificate.Subject -match 'O=Unity Technologies SF|O=Parsec') { 'VALID' }"
    try:
        r = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script], env=env,
                           capture_output=True, text=True, timeout=12, creationflags=subprocess.CREATE_NO_WINDOW)
        return r.returncode == 0 and r.stdout.strip() == "VALID"
    except (OSError, subprocess.TimeoutExpired):
        return False


def detect():
    if sys.platform == "win32":
        import psutil
        paths = []
        for p in psutil.process_iter(["name", "exe"]):
            if (p.info["name"] or "").lower() == "parsecd.exe" and p.info["exe"]:
                paths.append(Path(p.info["exe"]))
        paths.extend([Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "Parsec/parsecd.exe",
                      Path(os.environ.get("LOCALAPPDATA", "")) / "Parsec/parsecd.exe"])
        for path in dict.fromkeys(paths):
            if not path.is_file():
                continue
            try:
                import pefile
                with pefile.PE(str(path), fast_load=False) as pe:
                    products = [entry.entries.get(b"ProductName", b"").decode(errors="replace")
                                for file_info in getattr(pe, "FileInfo", []) for info in file_info
                                for entry in getattr(info, "StringTable", [])]
                if "Parsec" not in products:
                    continue
                # Shared asset directory takes priority if present. Loader and service use it.
                roots = [Path(os.environ.get("PROGRAMDATA", "C:/ProgramData")) / "Parsec",
                         Path(os.environ.get("APPDATA", "")) / "Parsec", path.parent]
                version = next((v for root in roots if (v := active_version(root)) != "unknown"), "unknown")
                return Installation(path.resolve(), version, windows_signature(path), "win32")
            except (OSError, ValueError, pefile.PEFormatError):
                return Installation(path, error="invalid_executable")
    elif sys.platform == "darwin":
        for bundle in (Path("/Applications/Parsec.app"), Path.home() / "Applications/Parsec.app"):
            try:
                info = plistlib.loads((bundle / "Contents/Info.plist").read_bytes())
                name = info.get("CFBundleExecutable", "")
                if not name or Path(name).name != name or info.get("CFBundleIdentifier") not in ("com.parsecgaming.parsec", "com.parsec.app"):
                    continue
                executable = bundle / "Contents/MacOS" / name
                if executable.is_file():
                    return Installation(executable, info.get("CFBundleShortVersionString", "unknown"), False, "darwin")
            except (OSError, ValueError, plistlib.InvalidFileException):
                continue
    return Installation(platform=sys.platform)


def launch(installation):
    if not installation.installed:
        raise FileNotFoundError("Parsec is not installed")
    if installation.platform == "win32":
        if not installation.signature_valid:
            raise ValueError("Unverified executable refused")
        subprocess.Popen([str(installation.executable)], creationflags=subprocess.CREATE_NO_WINDOW)
    elif installation.platform == "darwin":
        subprocess.Popen(["open", str(installation.executable.parents[2])])
    else:
        raise ValueError("Unsupported platform")
