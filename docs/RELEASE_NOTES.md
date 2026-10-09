# v0.1.2 · Experimental Chinese companion

**This is a companion, not complete native Parsec localization. Native text replacement: 0%.**

- Simplified Chinese, Traditional Chinese and English companion UI.
- 165 bilingual glossary entries with provenance metadata.
- On-demand read-only public settings mirror for signed Windows Parsec 150-105c and UI 150-33661022248.
- Official page navigation is disabled after unreliable UIA Invoke completion was observed. Users switch pages manually in Parsec. No connection, authentication or setting-value automation.
- Live reads use an on-demand isolated helper with an 18-second timeout and no output pipes; a stalled provider cannot trap the companion window.
- Backed up, atomic companion preferences; restore companion English and cleanup.
- Windows x64 installer and portable package. macOS arm64 and Intel DMGs provide the companion and glossary; live AX integration is unavailable.

All installers are **unsigned**. macOS apps are not Developer ID signed or notarized. Build/smoke checks do not establish Gatekeeper acceptance, real macOS Parsec integration or streaming performance. Never disable system security. Source/rebuild options remain available if an OS blocks an unsigned app.

The project's README and docs/VALIDATION.md distinguish automated checks, real Windows observations and unverified behavior. No proprietary Parsec binaries or user data are distributed.
