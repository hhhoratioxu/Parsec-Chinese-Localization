# Compatibility

| Feature | Windows | macOS |
| --- | --- | --- |
| Companion UI / dictionary / own preferences | Implemented | Implemented; CI packaging target |
| Install/version detection | Real local detection of 150-105c; portable running executable recognized | Bundle ID/Info.plist detection; real Parsec installation untested |
| Signature check | Authenticode issuer and validity checked | Live integration unavailable; no signature compatibility claim |
| Public settings reads | APP 150-105c and UI 150-33661022248 only; WebView2 | Not implemented; disabled |
| Official-page navigation | Disabled after real Invoke completion failures; manual navigation in official app | Not implemented; disabled |
| Native text replacement | 0%; disabled | 0%; disabled |
| Signed distribution | No certificate | No Developer ID / notarization |

Unknown application versions, UI versions, missing documents, ambiguous windows, minimized windows or changed navigation structure refuse live operations. No bypass option exists. Version checks happen on every read/navigation, not only at startup.

The Windows asset directory search considers shared ProgramData, per-user AppData and portable executable directories. It only reads the active DLL filename. An ambiguous/stale metadata version cannot authorize a different UI because live APP/UI button versions must also match. No Parsec configuration is changed to enable WebView2.

macOS packaging architecture is determined by each native CI runner; it is not a universal binary. Minimum supported OS follows Qt/PySide6 6.12 binaries. Actual CI results and hardware verification boundaries are recorded in VALIDATION.md. Windows 10 hardware and macOS Parsec integration are untested.
