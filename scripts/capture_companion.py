"""Capture actual Qt windows; uses no user identifiers or Parsec screenshots."""
from pathlib import Path
import tempfile
from PySide6.QtWidgets import QApplication
from parsec_chinese.app import Window
from parsec_chinese.state import StateStore
from parsec_chinese.detection import detect
from parsec_chinese.bridge import WindowsBridge
from parsec_chinese.translations import Translations

def main():
    target = Path(__file__).resolve().parents[1] / "docs/images"
    target.mkdir(parents=True, exist_ok=True)
    installation = detect()
    snapshot = WindowsBridge(installation, Translations()).read()
    app = QApplication([])
    with tempfile.TemporaryDirectory() as temp:
        window = Window(StateStore(temp), installation, autodetect=False)
        window.resize(1160, 860)
        window.show()
        app.processEvents()
        window.grab().save(str(target / "companion-overview-zh-CN.png"))
        window.snapshot = snapshot
        window.pages.setCurrentIndex(1)
        for language in ("en", "zh-CN", "zh-TW"):
            window.set_language(language)
            app.processEvents()
            window.grab().save(str(target / f"companion-live-{language}.png"))
        window.set_language("zh-CN")
        window.pages.setCurrentIndex(2)
        window.search.setText("Decoder")
        app.processEvents()
        window.grab().save(str(target / "companion-glossary.png"))
        window.close()
    print(f"Captured actual companion windows to {target}")

if __name__ == "__main__":
    main()
