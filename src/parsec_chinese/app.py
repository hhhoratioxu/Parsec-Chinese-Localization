import argparse
from dataclasses import replace
import json
from pathlib import Path
import sys
from PySide6.QtCore import Qt, QThread, Signal, QTimer, QUrl
from PySide6.QtGui import QDesktopServices, QFont, QKeySequence, QShortcut
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QStackedWidget, QFrame, QGridLayout, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QScrollArea, QAbstractItemView)
from . import __version__, REPOSITORY
from .translations import Translations
from .state import StateStore, Preferences
from .detection import detect, launch, Installation
from .bridge import WindowsBridge, BridgeError, Snapshot
from .isolated_bridge import IsolatedBridge, worker
from .updates import latest_release


class Job(QThread):
    done = Signal(object)
    failed = Signal(str)

    def __init__(self, kind, function, parent):
        super().__init__(parent)
        self.kind, self.function = kind, function

    def run(self):
        try:
            self.done.emit((self.kind, self.function()))
        except BridgeError as exc:
            self.failed.emit(str(exc))
        except Exception:
            self.failed.emit("generic")  # Never forward paths, UI text or server responses.


class Window(QMainWindow):
    def __init__(self, store=None, installation=None, autodetect=True):
        super().__init__()
        self.store = store or StateStore()
        self.translations = Translations()
        self.startup_problem = False
        try:
            self.preferences = self.store.load()
        except (OSError, ValueError, TypeError):
            self.preferences = Preferences()
            self.startup_problem = True
        self.installation = installation or Installation()
        self.snapshot = Snapshot()
        self.job = None
        self.setWindowTitle("Parsec Chinese Localization")
        self.setMinimumSize(880, 640)
        self.resize(1080, 760)
        self._build()
        self.retranslate()
        self.apply_theme()
        if autodetect:
            QTimer.singleShot(0, self.redetect)
        if self.startup_problem:
            QTimer.singleShot(0, lambda: self.message("startup_error"))

    def t(self, key, **values):
        return self.translations.text("ui." + key, self.preferences.language, **values)

    def label(self, text="", style="", wrap=True):
        label = QLabel(text)
        label.setTextFormat(Qt.TextFormat.PlainText)
        label.setWordWrap(wrap)
        if style:
            label.setObjectName(style)
        return label

    def button(self, handler):
        button = QPushButton()
        button.setMinimumHeight(38)
        button.clicked.connect(handler)
        return button

    def _build(self):
        central = QWidget()
        self.setCentralWidget(central)
        outer = QHBoxLayout(central)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        side = QFrame()
        side.setObjectName("sidebar")
        side.setFixedWidth(220)
        sidebar = QVBoxLayout(side)
        sidebar.setContentsMargins(22, 30, 22, 24)
        brand = self.label("P / 中", "brand")
        sidebar.addWidget(brand)
        sidebar.addSpacing(22)
        self.page_buttons = []
        for index in range(4):
            b = self.button(lambda checked=False, i=index: self.pages.setCurrentIndex(i))
            b.setObjectName("nav")
            sidebar.addWidget(b)
            self.page_buttons.append(b)
        sidebar.addStretch()
        self.edition = self.label(style="muted")
        sidebar.addWidget(self.edition)
        outer.addWidget(side)
        body = QVBoxLayout()
        body.setContentsMargins(30, 26, 30, 24)
        body.setSpacing(16)
        title = self.label("Parsec Chinese Localization", "title")
        body.addWidget(title)
        self.subtitle = self.label(style="muted")
        body.addWidget(self.subtitle)
        options = QHBoxLayout()
        self.language_picker = QComboBox()
        for name, lang in (("简体中文", "zh-CN"), ("繁體中文", "zh-TW"), ("English", "en")):
            self.language_picker.addItem(name, lang)
        self.language_picker.currentIndexChanged.connect(self.change_language)
        self.theme_picker = QComboBox()
        for theme in ("system", "light", "dark"):
            self.theme_picker.addItem(theme, theme)
        self.theme_picker.currentIndexChanged.connect(self.change_theme)
        options.addWidget(self.language_picker)
        options.addWidget(self.theme_picker)
        options.addStretch()
        self.github_button = self.button(lambda: QDesktopServices.openUrl(QUrl(REPOSITORY)))
        options.addWidget(self.github_button)
        body.addLayout(options)
        self.pages = QStackedWidget()
        body.addWidget(self.pages, 1)
        outer.addLayout(body, 1)
        self._overview()
        self._live()
        self._glossary()
        self._about()
        QShortcut(QKeySequence("Ctrl+F"), self, activated=self.search_terms)

    def page(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)
        self.pages.addWidget(widget)
        return layout

    def _overview(self):
        layout = self.page()
        grid = QGridLayout()
        self.stats = {}
        for i, key in enumerate(("installation", "version", "tool_version", "compatibility", "native_language", "coverage")):
            card = QFrame()
            card.setObjectName("card")
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(18, 14, 18, 14)
            heading = self.label(style="muted")
            value = self.label(style="stat")
            card_layout.addWidget(heading)
            card_layout.addWidget(value)
            grid.addWidget(card, i // 2, i % 2)
            self.stats[key] = (heading, value)
        layout.addLayout(grid)
        self.notice = self.label(style="notice")
        layout.addWidget(self.notice)
        row = QHBoxLayout()
        self.enable_button = self.button(self.enable_chinese)
        self.enable_button.setObjectName("primary")
        self.restore_button = self.button(lambda: self.set_language("en"))
        row.addWidget(self.enable_button)
        row.addWidget(self.restore_button)
        layout.addLayout(row)
        self.patch_button = QPushButton()
        self.patch_button.setEnabled(False)
        layout.addWidget(self.patch_button)
        self.patch_reason = self.label(style="muted")
        layout.addWidget(self.patch_reason)
        row = QHBoxLayout()
        self.open_button = self.button(self.open_parsec)
        self.detect_button = self.button(self.redetect)
        row.addWidget(self.open_button)
        row.addWidget(self.detect_button)
        layout.addLayout(row)
        layout.addStretch()

    def _live(self):
        layout = self.page()
        self.live_help = self.label(style="muted")
        layout.addWidget(self.live_help)
        self.read_button = self.button(self.read_current)
        layout.addWidget(self.read_button)
        nav = QHBoxLayout()
        self.nav_picker = QComboBox()
        self.nav_button = self.button(self.navigate)
        nav.addWidget(self.nav_picker, 1)
        nav.addWidget(self.nav_button)
        layout.addLayout(nav)
        self.live_status = self.label(style="muted")
        layout.addWidget(self.live_status)
        self.live_table = self.table(4)
        layout.addWidget(self.live_table, 1)
        self.settings_note = self.label(style="muted")
        layout.addWidget(self.settings_note)

    def table(self, columns):
        table = QTableWidget(0, columns)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.verticalHeader().hide()
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setWordWrap(True)
        table.setAlternatingRowColors(True)
        return table

    def _glossary(self):
        layout = self.page()
        self.search = QLineEdit()
        self.search.setClearButtonEnabled(True)
        self.search.textChanged.connect(self.fill_glossary)
        layout.addWidget(self.search)
        self.dictionary_count = self.label(style="muted")
        layout.addWidget(self.dictionary_count)
        self.glossary_table = self.table(3)
        layout.addWidget(self.glossary_table, 1)

    def _about(self):
        layout = self.page()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        inner = QVBoxLayout(content)
        self.about_labels = {}
        for key in ("limitation", "independent", "backup_help", "shortcut", "update_notice", "cleanup_help"):
            label = self.label(style="muted" if key in ("shortcut", "update_notice", "cleanup_help") else "")
            self.about_labels[key] = label
            inner.addWidget(label)
            inner.addSpacing(12)
        self.update_button = self.button(lambda: self.run_job("update", latest_release))
        self.logs_button = self.button(self.show_logs)
        self.cleanup_button = self.button(self.cleanup)
        inner.addWidget(self.update_button)
        inner.addWidget(self.logs_button)
        inner.addWidget(self.cleanup_button)
        inner.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)

    def retranslate(self):
        for b, key in zip(self.page_buttons, ("overview", "live", "glossary", "about")):
            b.setText(self.t(key))
        self.subtitle.setText(self.t("subtitle"))
        self.edition.setText(self.t("experimental", version=__version__))
        for name, key in (("github_button", "github"), ("enable_button", "enable"), ("restore_button", "restore"),
                          ("patch_button", "patch"), ("open_button", "open_parsec"), ("detect_button", "refresh"),
                          ("read_button", "read"), ("nav_button", "navigation"), ("update_button", "update"),
                          ("logs_button", "logs"), ("cleanup_button", "cleanup")):
            getattr(self, name).setText(self.t(key))
        for label, key in ((self.notice, "notice"), (self.patch_reason, "patch_reason"), (self.live_help, "live_help"), (self.settings_note, "settings_note")):
            label.setText(self.t(key))
        self.patch_button.setToolTip(self.t("patch_reason"))
        self.language_picker.blockSignals(True)
        self.language_picker.setCurrentIndex(self.language_picker.findData(self.preferences.language))
        self.language_picker.blockSignals(False)
        self.language_picker.setAccessibleName(self.t("language"))
        self.theme_picker.blockSignals(True)
        for i, key in enumerate(("system", "light", "dark")):
            self.theme_picker.setItemText(i, self.t(key))
        self.theme_picker.setCurrentIndex(self.theme_picker.findData(self.preferences.theme))
        self.theme_picker.blockSignals(False)
        self.theme_picker.setAccessibleName(self.t("theme"))
        for key, label in self.about_labels.items():
            label.setText(self.t(key))
        self.search.setPlaceholderText(self.t("search"))
        self.live_table.setHorizontalHeaderLabels([self.t(k) for k in ("translation", "term", "value", "availability")])
        self.glossary_table.setHorizontalHeaderLabels([self.t(k) for k in ("term", "translation", "category")])
        self.refresh_stats()
        self.fill_glossary()
        self.fill_snapshot()

    def refresh_stats(self):
        i = self.installation
        values = {"installation": self.t("installed" if i.installed else "missing"), "version": i.version,
                  "tool_version": __version__, "compatibility": self.t("supported" if i.live_supported else "unsupported"),
                  "native_language": self.t("native_value"), "coverage": self.t("coverage_value")}
        for key, (heading, value) in self.stats.items():
            heading.setText(self.t(key))
            value.setText(values[key])
        self.set_busy(self.job is not None)

    def set_busy(self, busy):
        for button, kind, key in ((self.detect_button, "detect", "refresh"), (self.read_button, "read", "read"),
                                  (self.nav_button, "navigate", "navigation"), (self.update_button, "update", "update")):
            button.setText(self.t("reading") if busy and self.job and self.job.kind == kind else self.t(key))
        self.detect_button.setEnabled(not busy)
        self.update_button.setEnabled(not busy)
        self.open_button.setEnabled(not busy and self.installation.installed and
                                    (self.installation.signature_valid or self.installation.platform == "darwin"))
        self.read_button.setEnabled(not busy and self.installation.live_supported)
        self.read_button.setToolTip("" if self.installation.live_supported else self.t("unsupported_version_error"))
        self.nav_button.setEnabled(not busy and bool(self.snapshot.navigation) and self.installation.live_supported)
        self.nav_picker.setEnabled(not busy and bool(self.snapshot.navigation))
        self.nav_button.setToolTip("" if self.snapshot.navigation else self.t("live_help"))

    def fill_glossary(self):
        rows = self.translations.terms(self.preferences.language, self.search.text())
        self.glossary_table.setRowCount(len(rows))
        for r, values in enumerate(rows):
            for c, value in enumerate(values):
                translated = self.translations.term("Log in" if value == "Login" else value, self.preferences.language) if c == 2 else value
                self.glossary_table.setItem(r, c, QTableWidgetItem(translated))
        self.glossary_table.resizeRowsToContents()
        self.dictionary_count.setText(self.t("dictionary_count", count=len(self.translations.catalog)))

    def fill_snapshot(self):
        rows = self.snapshot.rows
        self.live_table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            values = (self.translations.term(row.label, self.preferences.language), row.label,
                      self.translations.term(row.value, self.preferences.language) if row.value else self.t("omitted"),
                      self.t("available" if row.enabled else "disabled"))
            for c, value in enumerate(values):
                self.live_table.setItem(r, c, QTableWidgetItem(value))
        self.live_table.resizeRowsToContents()
        self.nav_picker.clear()
        for label in self.snapshot.navigation:
            self.nav_picker.addItem(self.translations.term(label, self.preferences.language), label)
        self.live_status.setText(self.t("read_coverage", translated=self.snapshot.translated, observed=self.snapshot.observed, version=self.snapshot.ui_version)
                                 if self.snapshot.ui_version and self.snapshot.observed else self.t("no_rows"))
        self.set_busy(self.job is not None)

    def set_language(self, language):
        try:
            new = replace(self.preferences, language=language)
            changed = self.store.save(new)
            self.preferences = new
            self.retranslate()
            if changed:
                self.safe_log("language_changed")
        except (OSError, ValueError, TypeError):
            self.retranslate()
            self.message("generic_error")

    def enable_chinese(self):
        language = self.language_picker.currentData()
        self.set_language(language if language != "en" else "zh-CN")

    def change_language(self):
        self.set_language(self.language_picker.currentData())

    def change_theme(self):
        try:
            new = replace(self.preferences, theme=self.theme_picker.currentData())
            self.store.save(new)
            self.preferences = new
            self.apply_theme()
            self.safe_log("theme_changed")
        except (OSError, ValueError, TypeError):
            self.retranslate()
            self.message("generic_error")

    def apply_theme(self):
        dark = self.preferences.theme == "dark" or (self.preferences.theme == "system" and QApplication.styleHints().colorScheme() == Qt.ColorScheme.Dark)
        bg, panel, fg, muted, border, alt = (("#10151e", "#192230", "#edf2fa", "#a6b5ca", "#2c3b50", "#1d2939") if dark
                                             else ("#f4f6fa", "#ffffff", "#17253b", "#5a6b82", "#dae2ee", "#f6f8fc"))
        self.setStyleSheet(f"""
            QWidget {{ font-size: 14px; color: {fg}; background: {bg}; }}
            QFrame#sidebar {{ background: {panel}; border-right: 1px solid {border}; }}
            QFrame#card {{ background: {panel}; border: 1px solid {border}; border-radius: 12px; }}
            QLabel {{ background: transparent; }}
            QLabel#title {{ font-size: 26px; font-weight: 700; }}
            QLabel#brand {{ font-size: 32px; font-weight: 700; color: #3f8fe8; }}
            QLabel#stat {{ font-size: 16px; font-weight: 600; }}
            QLabel#muted {{ color: {muted}; }}
            QLabel#notice {{ padding: 14px; background: {panel}; border-left: 3px solid #3f8fe8; border-radius: 5px; }}
            QPushButton {{ padding: 8px 12px; background: {panel}; border: 1px solid {border}; border-radius: 7px; }}
            QPushButton:hover {{ border-color: #3f8fe8; }}
            QPushButton:disabled {{ color: {muted}; }}
            QPushButton#primary {{ background: #246bc4; color: white; border-color: #246bc4; }}
            QPushButton#nav {{ text-align: left; background: transparent; border: none; padding: 12px 8px; }}
            QComboBox, QLineEdit {{ background: {panel}; padding: 9px; border: 1px solid {border}; border-radius: 6px; }}
            QTableWidget {{ background: {panel}; alternate-background-color: {alt}; gridline-color: {border}; border: 1px solid {border}; border-radius: 6px; }}
            QHeaderView::section {{ background: {panel}; padding: 9px; border: none; border-bottom: 1px solid {border}; }}
            QScrollArea {{ border: none; }}
        """)

    def run_job(self, kind, function):
        if self.job is not None:
            return
        self.job = Job(kind, function, self)
        self.job.done.connect(self.job_done)
        self.job.failed.connect(self.job_failed)
        self.job.finished.connect(self.job_finished)
        self.set_busy(True)
        self.job.start()

    def job_done(self, result):
        kind, value = result
        if kind == "detect":
            self.installation = value
            self.snapshot = Snapshot()
            self.refresh_stats()
            self.fill_snapshot()
        elif kind == "read":
            self.snapshot = value
            self.fill_snapshot()
            self.safe_log("read_succeeded")
        elif kind == "navigate":
            self.snapshot = Snapshot()
            self.fill_snapshot()  # Previous values are stale until explicitly reread.
        elif kind == "update":
            QMessageBox.information(self, self.t("update"), self.t("update_result", version=value))
            self.safe_log("update_checked")

    def job_failed(self, code):
        if self.job and self.job.kind in ("read", "navigate"):
            self.snapshot = Snapshot()
            self.fill_snapshot()
        self.safe_log("operation_failed")
        self.message({"open_parsec": "open_parsec_error", "unsupported_version": "unsupported_version_error",
                      "unsupported_ui": "unsupported_ui_error", "navigation_unavailable": "navigation_error",
                      "provider_timeout": "provider_timeout_error",
                      "navigation_refused": "navigation_error"}.get(code, "generic_error"))

    def job_finished(self):
        job, self.job = self.job, None
        if job:
            job.deleteLater()
        self.set_busy(False)

    def redetect(self):
        self.snapshot = Snapshot()
        self.fill_snapshot()
        self.run_job("detect", detect)

    def open_parsec(self):
        self.run_job("launch", lambda: launch(self.installation))

    def read_current(self):
        if self.installation.live_supported:
            self.run_job("read", lambda: IsolatedBridge(self.installation, self.translations).read())

    def navigate(self):
        label = self.nav_picker.currentData()
        if label:
            self.run_job("navigate", lambda: IsolatedBridge(self.installation, self.translations).navigate(label))

    def search_terms(self):
        self.pages.setCurrentIndex(2)
        self.search.setFocus()

    def safe_log(self, event):
        try:
            self.store.log(event)
        except OSError:
            pass

    def message(self, key):
        QMessageBox.warning(self, self.t("error"), self.t(key))

    def show_logs(self):
        try:
            path = self.store._safe("events.log")
            text = path.read_text(encoding="utf-8")[-8192:] if path.is_file() else self.t("no_logs")
            box = QMessageBox(self)
            box.setWindowTitle(self.t("logs"))
            box.setTextFormat(Qt.TextFormat.PlainText)
            box.setText(text)
            box.exec()
        except OSError:
            self.message("generic_error")

    def cleanup(self):
        try:
            self.store.clear()
            self.preferences = Preferences()
            self.snapshot = Snapshot()
            self.retranslate()
            self.apply_theme()
        except (OSError, ValueError):
            self.message("generic_error")

    def closeEvent(self, event):
        if self.job is not None and self.job.isRunning():
            event.ignore()  # Never destroy a live QThread or force-kill a read.
        else:
            event.accept()


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke-test", action="store_true", help="Run a GUI startup check without reading Parsec")
    parser.add_argument("--probe", action="store_true", help="Print a sanitized, read-only public settings snapshot")
    parser.add_argument("--reset", action="store_true", help="Remove only companion preferences and logs")
    parser.add_argument("--bridge-worker", choices=("read", "navigate"), help=argparse.SUPPRESS)
    parser.add_argument("--bridge-output", help=argparse.SUPPRESS)
    parser.add_argument("--label", default="", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if args.bridge_worker:
        return worker(args.bridge_worker, args.bridge_output or "", args.label)
    if args.reset:
        StateStore().clear()
        return 0
    if args.probe:
        from dataclasses import asdict
        result = WindowsBridge(detect(), Translations()).read()
        print(json.dumps(asdict(result), ensure_ascii=False, indent=2))
        return 0
    app = QApplication.instance() or QApplication(sys.argv[:1])
    app.setApplicationName("Parsec Chinese Localization")
    app.setOrganizationName("ParsecChineseLocalization")
    app.setFont(QFont("Microsoft YaHei UI" if sys.platform == "win32" else "PingFang TC", 10))
    if args.smoke_test:
        import tempfile
        with tempfile.TemporaryDirectory() as temp:
            window = Window(StateStore(temp), autodetect=False)
            window.show()
            QTimer.singleShot(300, app.quit)
            return app.exec()
    window = Window()
    app.styleHints().colorSchemeChanged.connect(lambda _: window.apply_theme())
    window.show()
    return app.exec()

if __name__ == "__main__":
    raise SystemExit(main())
