from collections import Counter
import json
import re
from pathlib import Path
from .resources import resource_dir

LANGUAGES = ("en", "zh-CN", "zh-TW")
PLACEHOLDERS = re.compile(r"\{[^{}]+\}|%(?:\d+\$)?[-+#0 ]*\d*(?:\.\d+)?[sdifu]|Ctrl\+[^\s,]+|Alt\+[^\s,]+|Command\+[^\s,]+")


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate translation key: {key}")
        result[key] = value
    return result


class Translations:
    def __init__(self, root: Path | None = None):
        root = root or resource_dir()
        self.languages = {lang: json.loads((root / f"{lang}.json").read_text(encoding="utf-8"), object_pairs_hook=unique_object) for lang in LANGUAGES}
        self.catalog = json.loads((root / "catalog.json").read_text(encoding="utf-8"))
        self.validate()
        self.lookup = {value.casefold(): key for key, value in self.languages["en"].items() if key.startswith("term.")}

    def validate(self):
        base = self.languages["en"]
        for lang, data in self.languages.items():
            if set(base) != set(data):
                raise ValueError(f"Incomplete translations: {lang}")
            for key, value in data.items():
                if not isinstance(value, str) or not value.strip():
                    raise ValueError(f"Empty translation: {lang}/{key}")
                if Counter(PLACEHOLDERS.findall(base[key])) != Counter(PLACEHOLDERS.findall(value)):
                    raise ValueError(f"Placeholder mismatch: {lang}/{key}")
        term_keys = {k for k in base if k.startswith("term.")}
        if set(self.catalog) != term_keys:
            raise ValueError("Every term requires provenance")

    def text(self, key, language="zh-CN", **values):
        if language not in LANGUAGES:
            raise ValueError("Unsupported language")
        text = self.languages[language][key]
        return text.format(**values) if values else text

    def term(self, english, language="zh-CN"):
        key = self.lookup.get(english.strip().casefold())
        return self.text(key, language) if key else english

    def terms(self, language="zh-CN", query=""):
        query = query.casefold().strip()
        return [(self.languages["en"][key], self.text(key, language), self.catalog[key]["category"])
                for key in self.catalog
                if not query or query in (self.languages["en"][key] + self.text(key, language)).casefold()]
