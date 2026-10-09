# Third-party components

This project is MIT licensed. Dependencies retain their own licenses; no Parsec proprietary program or assets are distributed.

- Qt / PySide6 / Shiboken6: LGPL-3.0 (applicable components). We use dynamically linked QtCore, QtGui, QtWidgets and QtTest. The onedir bundle leaves libraries replaceable. Source: https://code.qt.io/cgit/pyside/pyside-setup.git/ and https://code.qt.io/cgit/qt/qtbase.git/ . Exact package version: 6.12.0. No modifications to Qt/PySide6.
- Python: PSF license; https://www.python.org/downloads/source/ . Windows local build uses Python 3.14; CI uses Python 3.12. No modifications to Python.
- psutil, pywinauto: BSD licenses.
- pefile, comtypes, altgraph: MIT licenses.
- pywin32: PSF license.
- PyInstaller bootloader: GPL with distribution exception allowing bundled application distribution.

Builds collect dependency license files under `third-party-licenses` inside the application's `_internal` directory. LGPL and GPL texts are included. For replacing libraries, use the portable onedir package and replace the corresponding Qt DLLs/dylibs with ABI-compatible versions. For rebuilding, follow CONTRIBUTING.md; installation certificates/signing are not claimed.
