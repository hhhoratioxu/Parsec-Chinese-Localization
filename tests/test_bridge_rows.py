from types import SimpleNamespace as NS
from parsec_chinese.bridge import WindowsBridge
from parsec_chinese.translations import Translations
from parsec_chinese.detection import Installation


class Node:
    def __init__(self, name, kind="Text", role="heading", children=()):
        self.element_info = NS(name=name, control_type=kind, element=NS(CurrentAriaRole=role))
        self.nodes = list(children)
        self.owner = None
        for c in self.nodes:
            c.owner = self
        self.iface_value = NS(CurrentValue="Hardware")

    def descendants(self):
        return [c for node in self.nodes for c in (node, *node.descendants())]

    def parent(self):
        return self.owner

    def is_enabled(self):
        return True


def test_grouped_client_fields_and_private_text(monkeypatch):
    heading = Node("Decoder")
    control = Node("Decoder", "ComboBox", "combobox")
    group = Node("", "Group", "group", (heading, control))
    private = Node("private-account#123", role="")
    root = Node("", "Window", "", (group, private))
    bridge = WindowsBridge(Installation(), Translations())
    monkeypatch.setattr(bridge, "_window", lambda: (root, []))
    snapshot = bridge.read()
    assert snapshot.observed == snapshot.translated == 1
    assert snapshot.rows[0].label == "Decoder"
    assert snapshot.rows[0].value == "Hardware"


def test_unknown_heading_counted_but_not_retained(monkeypatch):
    heading = Node("Unverified setting")
    control = Node("Unverified setting", "Edit", "textbox")
    root = Node("", "Group", "group", (heading, control))
    bridge = WindowsBridge(Installation(), Translations())
    monkeypatch.setattr(bridge, "_window", lambda: (root, []))
    snapshot = bridge.read()
    assert snapshot.observed == 1
    assert snapshot.rows == ()


def test_host_name_edit_value_never_accessed(monkeypatch):
    heading = Node("Host Name")
    control = Node("Host Name", "Edit", "textbox")
    del control.iface_value
    root = Node("", "Group", "group", (heading, control))
    bridge = WindowsBridge(Installation(), Translations())
    monkeypatch.setattr(bridge, "_window", lambda: (root, []))
    snapshot = bridge.read()
    assert snapshot.rows[0].value == ""
