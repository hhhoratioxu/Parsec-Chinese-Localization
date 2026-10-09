"""Build our app only; no Parsec proprietary resources are bundled."""
from importlib import metadata
from pathlib import Path
import hashlib
import platform
import shutil
import subprocess
import sys
import os
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
NAME = "ParsecChineseLocalization"
VERSION = "0.1.0"


def run(command, **kwargs):
    subprocess.run(command, cwd=ROOT, check=True, **kwargs)


def licenses():
    target = ROOT / "build/third-party-licenses"
    target.mkdir(parents=True, exist_ok=True)
    for package in ("PySide6-Essentials", "shiboken6", "psutil", "pyinstaller", "altgraph", "pefile", "pywinauto", "comtypes", "pywin32"):
        try:
            dist = metadata.distribution(package)
        except metadata.PackageNotFoundError:
            continue
        for file in dist.files or []:
            if any(name in str(file).lower() for name in ("license", "copying")) and dist.locate_file(file).is_file():
                out = target / package / file.name
                out.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(dist.locate_file(file), out)
    # LGPL dynamic libraries remain replaceable in onedir bundles. Include the texts.
    for filename, url in (("LGPL-3.0.txt", "https://raw.githubusercontent.com/qt/qtbase/dev/LICENSES/LGPL-3.0-only.txt"),
                          ("GPL-3.0.txt", "https://raw.githubusercontent.com/qt/qtbase/dev/LICENSES/GPL-3.0-only.txt"),
                          ("Python-LICENSE.txt", "https://raw.githubusercontent.com/python/cpython/3.14/LICENSE")):
        with urllib.request.urlopen(url, timeout=30) as response:
            (target / filename).write_bytes(response.read())
    return target


def main():
    license_root = licenses()
    command = [sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "--onedir", "--windowed",
               "--name", NAME, "--paths", "src", "--add-data", "locales:locales",
               "--add-data", "LICENSE:.", "--add-data", "THIRD_PARTY_NOTICES.md:.",
               "--add-data", f"{license_root}:third-party-licenses", "--hidden-import", "psutil"]
    if sys.platform == "darwin":
        command += ["--osx-bundle-identifier", "org.hhhoratioxu.parsec-chinese-localization"]
    run(command + ["scripts/entry.py"])
    output = ROOT / "release"
    output.mkdir(exist_ok=True)
    if sys.platform == "win32":
        candidates = [shutil.which("ISCC.exe"), str(Path(os.environ.get("ProgramFiles(x86)", "C:/Program Files (x86)")) / "Inno Setup 6/ISCC.exe"),
                      str(Path(os.environ.get("LOCALAPPDATA", "")) / "Programs/Inno Setup 6/ISCC.exe")]
        compiler = next((x for x in candidates if x and Path(x).is_file()), None)
        if not compiler:
            raise FileNotFoundError("Install Inno Setup 6 or add ISCC.exe to PATH")
        run([compiler, "packaging/installer.iss"])
        shutil.make_archive(str(output / f"{NAME}-{VERSION}-windows-x64-portable"), "zip", ROOT / "dist", NAME)
    elif sys.platform == "darwin":
        app = ROOT / "dist" / f"{NAME}.app"
        stage = ROOT / "build/dmg-stage"
        stage.mkdir(exist_ok=True)
        shutil.copytree(app, stage / app.name, dirs_exist_ok=True)
        link = stage / "Applications"
        if not link.exists():
            link.symlink_to("/Applications", target_is_directory=True)
        dmg = output / f"{NAME}-{VERSION}-macos-{platform.machine()}.dmg"
        run(["hdiutil", "create", "-volname", "Parsec Chinese Companion", "-srcfolder", str(stage), "-ov", "-format", "UDZO", str(dmg)])
    else:
        raise RuntimeError("Release packaging is implemented for Windows and macOS")
    checksums(output)


def checksums(directory):
    entries = [f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}" for path in sorted(directory.iterdir()) if path.suffix in (".exe", ".dmg", ".zip")]
    (directory / "SHA256SUMS.txt").write_text("\n".join(entries) + "\n", encoding="utf-8")

if __name__ == "__main__":
    main()
