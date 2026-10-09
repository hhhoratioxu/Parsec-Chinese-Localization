from dataclasses import replace
import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt
from parsec_chinese.app import Window
from parsec_chinese.state import StateStore
from parsec_chinese.bridge import Snapshot, SettingRow
from parsec_chinese.detection import Installation


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def window(app, tmp_path):
    w = Window(StateStore(tmp_path), autodetect=False)
    w.show()
    app.processEvents()
    yield w
    w.close()


def test_no_native_success_claims(window):
    assert not window.patch_button.isEnabled()
    assert "0%" in window.stats["coverage"][1].text()
    assert not window.read_button.isEnabled()


def test_click_language_and_restore(window):
    window.language_picker.setCurrentIndex(window.language_picker.findData("zh-TW"))
    assert window.preferences.language == "zh-TW"
    assert window.store.load().language == "zh-TW"
    QTest.mouseClick(window.restore_button, Qt.MouseButton.LeftButton)
    assert window.preferences.language == "en"
    assert window.page_buttons[0].text() == "Overview"
    QTest.mouseClick(window.enable_button, Qt.MouseButton.LeftButton)
    assert window.preferences.language == "zh-CN"


def test_search_and_navigation(window):
    window.search_terms()
    window.search.setText("解码器")
    assert window.pages.currentIndex() == 2
    assert window.glossary_table.rowCount() == 1
    assert window.glossary_table.item(0,0).text() == "Decoder"


@pytest.mark.parametrize("theme", ["dark", "light", "system"])
def test_themes(window, theme):
    window.theme_picker.setCurrentIndex(window.theme_picker.findData(theme))
    assert window.store.load().theme == theme
    assert "QTableWidget" in window.styleSheet()


def test_snapshot_translates_and_omits_values(window):
    window.snapshot = Snapshot((SettingRow("Bandwidth Limit", "50 Mbps"), SettingRow("Host Name", "")), (), 2, 2, "test")
    window.fill_snapshot()
    assert window.live_table.item(0,0).text() == "带宽上限"
    assert window.live_table.item(0,2).text() == "50 Mbps"
    assert window.live_table.item(1,2).text() == window.t("omitted")


def test_cleanup(window):
    window.set_language("zh-TW")
    window.cleanup()
    assert window.preferences.language == "zh-CN"
    assert not (window.store.root / "preferences.json").exists()
