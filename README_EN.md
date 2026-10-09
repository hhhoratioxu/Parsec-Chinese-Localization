# Parsec Chinese Localization

**Experimental Chinese companion. Native Parsec text replacement is not implemented: 0% coverage.**

This independent project targets [Parsec Remote Desktop](https://parsec.app), not the unrelated parsec.cloud product. It is not affiliated with or endorsed by Parsec. The inspected client's strings are embedded in signed binaries and its new interface loads a remote WebView2 page. No verified native language-resource API was found. See [FEASIBILITY.md](docs/FEASIBILITY.md).

## Features and compatibility

- GUI with Simplified Chinese, Traditional Chinese, English, system fonts and light/dark themes.
- 160 searchable bilingual glossary entries, placeholder validation and provenance metadata.
- Installation/version detection and Windows Authenticode verification.
- On-demand read-only mirror of public settings headings/values on **Windows APP 150-105c / UI 150-33661022248 only**.
- Allowlisted official-page navigation. Settings changes, connections and authentication stay in the official application.
- Atomic backed-up companion preferences, English restoration and cleanup. No Parsec files are written.
- GitHub release checks only on click; event logs contain fixed names only.

Windows x64 installers and portable packages are built. macOS arm64/Intel DMGs provide the companion/glossary, with live Accessibility integration disabled. All packages are unsigned; macOS builds are not Developer ID signed or notarized. Build and smoke-test status is recorded in [VALIDATION.md](docs/VALIDATION.md). Windows 10 hardware, macOS Parsec integration and streaming benchmarks remain unverified.

## Install and use

Install the official Parsec client separately. Download an actual attachment from [Releases](https://github.com/hhhoratioxu/Parsec-Chinese-Localization/releases), verify SHA256SUMS.txt, then install the Windows EXE or keep the entire extracted portable directory. On macOS drag the app from its DMG to Applications. Follow normal OS workflows for unsigned software or build from source; do not disable security.

Select a companion language and search the glossary. On the known Windows version, open exactly one non-minimized Parsec window at a settings tab and click **Current settings → Read current page**. The snapshot is not continuously monitored. Choose an available navigation target to move to an official page and read again. No setting-value controls are mirrored as editable controls.

## Actual screenshots

These are captures of the running **companion**, including real Windows settings reads. They are not native Parsec localization before/after screenshots. Native Parsec stays unchanged; no native localization comparison exists.

![Companion overview](docs/images/companion-overview-zh-CN.png)

| English companion | Simplified Chinese companion |
| --- | --- |
| ![English](docs/images/companion-live-en.png) | ![Simplified Chinese](docs/images/companion-live-zh-CN.png) |

![Traditional Chinese companion](docs/images/companion-live-zh-TW.png)

## Restore, uninstall and limitations

Click **Restore companion to English**. Parsec needs no restoration because it was never patched. Uninstall the Windows tool through installed apps; its uninstaller deletes only its fixed preference/log files. Portable/macOS users can clear preferences in About, close the tool and remove its own app directory. Do not delete Parsec files.

Preferences: `%LOCALAPPDATA%\ParsecChineseLocalization` on Windows, `~/Library/Application Support/ParsecChineseLocalization` on macOS. `preferences.backup.json` backs up companion preferences only. A stale preference lock may be removed after closing all companion instances.

Native text replacement, login, host lists, connection overlays and private/error messages are not localized. Host names, device identifiers, edit boxes and unknown values are omitted. Unknown app/UI versions refuse live operations. A 27/27 settings-heading result applies only to that observed page, not the entire application.

FAQ: A disabled read button means the platform/version/signature is unverified. Empty values are deliberately omitted or unavailable. The tool does not change binaries, configuration, streaming protocols, drivers or permissions. Streaming performance has not been benchmarked. No user data is uploaded; an explicit GitHub check carries normal network request metadata.

## Development and license

See [CONTRIBUTING.md](CONTRIBUTING.md), [translation guidelines](docs/TRANSLATION.md), [compatibility](docs/COMPATIBILITY.md), [stage status](docs/STATUS.md), [CHANGELOG.md](CHANGELOG.md) and [security policy](SECURITY.md). Project code is [MIT](LICENSE); bundled dependencies retain their licenses in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

Provided as-is without guarantees of future compatibility. Parsec trademarks belong to their owners. No proprietary Parsec programs or assets are redistributed.
