import subprocess
import pytest
from parsec_chinese.isolated_bridge import IsolatedBridge, worker
from parsec_chinese.detection import Installation
from parsec_chinese.translations import Translations
from parsec_chinese.bridge import BridgeError


def test_provider_timeout_bounded(tmp_path, monkeypatch):
    exe = tmp_path / "parsecd.exe"
    exe.touch()
    bridge = IsolatedBridge(Installation(exe,"150-105c",True,"win32"), Translations(), timeout=0.1)
    def stall(command, **kwargs):
        assert kwargs["timeout"] == 0.1
        raise subprocess.TimeoutExpired(command, 0.1)
    monkeypatch.setattr(subprocess, "run", stall)
    with pytest.raises(BridgeError, match="provider_timeout"):
        bridge.read()


def test_worker_cannot_write_arbitrary_path(tmp_path):
    output = tmp_path / "parsecd.dll"
    assert worker("read", output) == 2
    assert not output.exists()


def test_unknown_version_does_not_start_helper(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Child must not start")
    monkeypatch.setattr(subprocess, "run", forbidden)
    with pytest.raises(BridgeError, match="unsupported_version"):
        IsolatedBridge(Installation(), Translations()).read()
