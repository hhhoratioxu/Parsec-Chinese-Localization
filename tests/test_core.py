from dataclasses import replace
import json
from pathlib import Path
import os
import pytest
from parsec_chinese.translations import Translations, unique_object
from parsec_chinese.state import StateStore, Preferences
from parsec_chinese.bridge import WindowsBridge, BridgeError, safe_value, NAVIGATION
from parsec_chinese.detection import Installation, active_version


def test_dictionary_complete():
    t = Translations()
    assert len(t.catalog) == 160
    assert t.term("Computers", "zh-CN") == "计算机"
    assert t.term("Computers", "zh-TW") == "電腦"
    assert all(v["native_replacement"] is False for v in t.catalog.values())


def test_placeholders_are_checked():
    t = Translations()
    t.languages["zh-TW"]["ui.read_coverage"] = "錯誤 {translated}"
    with pytest.raises(ValueError, match="Placeholder"):
        t.validate()


def test_missing_key_rejected():
    t = Translations()
    del t.languages["zh-CN"]["ui.coverage"]
    with pytest.raises(ValueError, match="Incomplete"):
        t.validate()


def test_duplicate_keys_rejected():
    with pytest.raises(ValueError, match="Duplicate"):
        json.loads('{"a":1,"a":2}', object_pairs_hook=unique_object)


@pytest.mark.parametrize("lang", ["en", "zh-CN", "zh-TW"])
def test_language_change_idempotent_and_restore(tmp_path, lang):
    store = StateStore(tmp_path)
    store.save(Preferences(language=lang))
    original = (tmp_path / "preferences.json").read_bytes()
    backup = (tmp_path / "preferences.backup.json").read_bytes()
    assert store.save(Preferences(language=lang)) is False
    assert (tmp_path / "preferences.json").read_bytes() == original
    assert (tmp_path / "preferences.backup.json").read_bytes() == backup
    assert store.restore_backup() == Preferences()


def test_backup_retains_previous_preferences(tmp_path):
    s = StateStore(tmp_path)
    s.save(Preferences(language="zh-TW", theme="dark"))
    s.save(Preferences(language="en", theme="dark"))
    assert s.restore_backup() == Preferences(language="zh-TW", theme="dark")


def test_atomic_write_failure_keeps_original(tmp_path, monkeypatch):
    s = StateStore(tmp_path)
    s.save(Preferences(language="en"))
    original = (tmp_path / "preferences.json").read_bytes()
    real_replace = os.replace
    def fail_new(src, dst):
        if Path(dst).name == "preferences.json":
            raise PermissionError("denied")
        return real_replace(src, dst)
    monkeypatch.setattr(os, "replace", fail_new)
    with pytest.raises(PermissionError):
        s.save(Preferences(language="zh-TW"))
    assert (tmp_path / "preferences.json").read_bytes() == original
    assert not list(tmp_path.glob(".preferences-*"))
    assert not (tmp_path / "preferences.lock").exists()


def test_corrupt_file_refused_without_overwriting(tmp_path):
    (tmp_path / "preferences.json").write_text("invalid")
    with pytest.raises(ValueError):
        StateStore(tmp_path).save(Preferences())
    assert (tmp_path / "preferences.json").read_text() == "invalid"


def test_missing_backup_reports_error(tmp_path):
    with pytest.raises(FileNotFoundError):
        StateStore(tmp_path).restore_backup()


def test_concurrent_writer_refused(tmp_path):
    (tmp_path / "preferences.lock").touch()
    with pytest.raises(FileExistsError):
        StateStore(tmp_path).save(Preferences())


def test_missing_translation_files(tmp_path):
    with pytest.raises(FileNotFoundError):
        Translations(tmp_path)


def test_cleanup_removes_only_own_files(tmp_path):
    store = StateStore(tmp_path)
    store.save(Preferences())
    store.log("language_changed")
    (tmp_path / "other-user-file.txt").write_text("keep")
    store.clear()
    assert {p.name for p in tmp_path.iterdir()} == {"other-user-file.txt"}


def test_log_refuses_private_text(tmp_path):
    with pytest.raises(ValueError):
        StateStore(tmp_path).log("token=secret")
    assert not (tmp_path / "events.log").exists()


@pytest.mark.parametrize("prefs", [{"language":"xx"}, {"theme":"unknown"}, {"schema":2}])
def test_invalid_preferences(prefs):
    with pytest.raises(ValueError):
        Preferences(**prefs)


@pytest.mark.parametrize("value", ["user@example.com", "secret-token", "MyPrivatePC", "https://parsec.app/join/secret"])
def test_values_filtered(value):
    assert safe_value(value, Translations()) == ""


@pytest.mark.parametrize("value", ["50 Mbps", "144", "0.0", "1920 x 1080", "Use Client Resolution", "Off"])
def test_public_values(value):
    assert safe_value(value, Translations()) == value


def test_unverified_version_refused_before_uia(tmp_path):
    exe = tmp_path / "parsecd.exe"
    exe.touch()
    bridge = WindowsBridge(Installation(exe, "150-999z", True, "win32"), Translations())
    with pytest.raises(BridgeError, match="unsupported_version"):
        bridge.read()


def test_non_windows_live_refused(tmp_path):
    exe = tmp_path / "parsec"
    exe.touch()
    bridge = WindowsBridge(Installation(exe, "150-105c", True, "darwin"), Translations())
    with pytest.raises(BridgeError, match="unsupported_version"):
        bridge.read()


def test_non_navigation_actions_refused():
    bridge = WindowsBridge(Installation(), Translations())
    assert "Join" not in NAVIGATION and "Log out" not in NAVIGATION
    with pytest.raises(BridgeError, match="navigation_refused"):
        bridge.navigate("Join")


@pytest.mark.parametrize("name", ["../../bad.dll", "parsecd-150-105c.dll.exe", "unknown", None])
def test_library_path_validation(tmp_path, name):
    (tmp_path / "appdata.json").write_text(json.dumps({"so_name":name}))
    assert active_version(tmp_path) == "unknown"


def test_library_version(tmp_path):
    (tmp_path / "appdata.json").write_text(json.dumps({"so_name":"parsecd-150-105c.dll", "secret":"not-returned"}))
    assert active_version(tmp_path) == "150-105c"


def test_symlink_refused(tmp_path):
    target = tmp_path / "target"
    target.mkdir()
    link = tmp_path / "link"
    try:
        link.symlink_to(target, target_is_directory=True)
    except OSError:
        pytest.skip("Creating symlinks is not permitted on this runner")
    with pytest.raises(ValueError, match="Redirected"):
        StateStore(link).save(Preferences())
