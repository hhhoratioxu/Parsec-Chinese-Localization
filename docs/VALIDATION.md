# Validation record

Date: 2026-10-09. Local system: Windows 11 build 26200, x64, Python 3.14.

- Initial automated pass after fixing malformed version metadata: 44 passed, 1 skipped. Symlink creation test skipped because the local Windows account cannot create the test link. GUI tests use Qt offscreen mode.
- Real read-only probe: signed Parsec APP 150-105c, WebView UI 150-33661022248. Host settings page: 27 known titles / 27 observed rows; host name omitted, unknown device/application values omitted. This is not full-app coverage.
- Actual GUI/native worker and installer/uninstaller checks: in progress; final results will be recorded here before release.
- Windows local unsigned installer and portable build: initial build succeeded. Further changes require rebuilding before release.
- macOS arm64/Intel CI: configured; results pending. No real macOS Parsec integration or Gatekeeper acceptance test.

Unverified: complete native localization, Windows 10 hardware, macOS real client integration, stream/connection overlays, login/register localization and streaming performance. No synthetic test is counted as a real client integration result.
