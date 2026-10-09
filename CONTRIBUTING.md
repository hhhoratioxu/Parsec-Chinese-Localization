# Contributing

Use Python 3.12+ and a matching platform. Install Inno Setup 6 for Windows packaging. Build dependencies are pinned in pyproject.toml.

```sh
python -m pip install -e '.[dev]'
python -m pytest -q
python -m parsec_chinese
python scripts/build.py
```

On Windows, `scripts/verify_installer.ps1` checks an isolated installation and uninstall, retaining existing companion preferences. macOS CI tests the built app and mounts/verifies the actual DMG. No CI runner has a logged-in Parsec integration session.

Edit reviewed JSON in locales/ and update matching English/source metadata. The seed script is a maintainer convenience and must be updated alongside manual JSON edits. Run completeness/placeholder tests. Clearly distinguish labels observed in UI, embedded DLL labels, documented labels and reference vocabulary.

When adding a compatibility entry, inspect signatures, the real UI version, tree structure and privacy boundaries. Add meaningful refusal/privacy tests and record actual manual evidence. Do not weaken the version gate merely because a build succeeds. No native patching, unofficial protocol behavior, authentication automation or OCR-as-localization.

Make changes on a branch and submit a pull request. Include the user-visible behavior, tests actually run and unverified scope. Do not attach credentials, raw UI trees, user.bin, Parsec logs or personal screenshots.
