# Translation resources

`locales/en.json`, `zh-CN.json` and `zh-TW.json` share identical keys. `ui.*` belongs to the companion; `term.*` is bilingual Parsec vocabulary. `catalog.json` records category, provenance and `native_replacement: false` for each term. No native language pack is claimed.

Labels came from the inspected Windows 150-105c UI/DLL and official Windows/macOS navigation documentation; general vocabulary without direct evidence is marked as reference vocabulary. The recorded real Host settings page has 27 headings. Dictionary entry count is not a whole-app translation percentage.

Use professional terminology: CN 计算机／客户端／分辨率／带宽／鼠标, TW 電腦／用戶端／解析度／頻寬／滑鼠. Preserve codecs, units, format placeholders and keyboard shortcuts. Do not translate private values or turn unknown text into guessed successful states. Labels are word-wrapped; tables resize their rows after language changes.

The validator rejects duplicate JSON keys, empty text, mismatched key sets and inconsistent `{name}`, printf and shortcut placeholders. Update English and both Chinese files together, including provenance. `scripts/seed_locales.py` can regenerate the seed dictionary; reviewed JSON is what ships.

Live coverage denominator is the number of observed ARIA headings with a uniquely labelled control in a nearby container. Numerator is the number with a known title. Sections, unmatched headings and private/unknown values are omitted; this is not a count of every visible text. The native replacement percentage remains zero.
