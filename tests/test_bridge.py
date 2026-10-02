"""Tests that run without Forge or Gradio installed."""
import ast
import importlib.util
import unittest
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


local = load("bridge_local_connection", "local_connection.py")
core = load("library_desk_core", "bridge_core.py")


class Forbidden(Exception):
    def __init__(self, code, detail):
        super().__init__(detail)
        self.code = code


class CheckLocalTests(unittest.TestCase):
    """check_local() is extracted from the Forge script, which imports Forge modules."""

    def setUp(self):
        source = ast.parse((ROOT / "scripts" / "library_desk_bridge.py").read_text(encoding="utf-8"))
        selected = ast.Module(
            body=[n for n in source.body if isinstance(n, ast.FunctionDef) and n.name in {"library_url", "check_local"}],
            type_ignores=[],
        )
        self.ns = {
            "shared": SimpleNamespace(opts=SimpleNamespace(data={"library_desk_url": "http://127.0.0.1:8787"})),
            "local": local,
            "urlparse": urlparse,
            "HTTPException": Forbidden,
        }
        exec(compile(selected, "<check_local>", "exec"), self.ns)

    def call(self, *, client="127.0.0.1", host="127.0.0.1:7860", origin=None):
        headers = {"host": host}
        if origin is not None:
            headers["origin"] = origin
        request = SimpleNamespace(client=SimpleNamespace(host=client), headers=headers, url=SimpleNamespace(port=7860))
        self.ns["check_local"](request)

    def assertRejected(self, **kwargs):
        with self.assertRaises(Forbidden) as caught:
            self.call(**kwargs)
        self.assertEqual(caught.exception.code, 403)

    def test_local_requests_are_allowed(self):
        self.call()
        self.call(host="localhost:7860")
        self.call(host="[::1]:7860", client="::1")
        self.call(origin="http://127.0.0.1:7860")
        self.call(origin="http://localhost:8787")
        self.call(host="127.0.0.1:7860", origin="")

    def test_dns_rebinding_host_is_rejected(self):
        # Same-origin GET from a rebound page: no Origin, attacker's Host.
        self.assertRejected(host="evil.example:7860")
        self.assertRejected(host="evil.example")
        self.assertRejected(host="")
        self.assertRejected(host="192.168.1.10:7860")

    def test_remote_clients_and_foreign_origins_are_rejected(self):
        self.assertRejected(client="192.168.1.20")
        self.assertRejected(origin="https://example.com")
        self.assertRejected(origin="http://127.0.0.1:9999")
        self.assertRejected(origin="http://user:pass@127.0.0.1:7860")


class LocalConnectionTests(unittest.TestCase):
    def test_normalize_loopback_url(self):
        self.assertEqual(local.normalize_loopback_url("http://localhost:8787/"), "http://localhost:8787")
        self.assertEqual(local.normalize_loopback_url("http://[::1]:8787"), "http://[::1]:8787")
        for bad in ("https://127.0.0.1:8787", "http://example.com:8787", "http://127.0.0.1:8787/api",
                    "http://u:p@127.0.0.1:8787", "http://127.0.0.1:99999", 8787):
            with self.assertRaises(ValueError):
                local.normalize_loopback_url(bad)

    def test_is_loopback_host_header(self):
        for ok in ("127.0.0.1", "127.0.0.1:7860", "localhost:7860", "LOCALHOST.", "[::1]:7860", "127.1.2.3"):
            self.assertTrue(local.is_loopback_host_header(ok), ok)
        for bad in ("", None, "evil.example", "localhost.evil.example", "192.168.0.2:7860", "[::2]", "127.0.0.1:abc"):
            self.assertFalse(local.is_loopback_host_header(bad), bad)


class BridgeStateTests(unittest.TestCase):
    def setUp(self):
        self.now = 100.0
        self.state = core.BridgeState(clock=lambda: self.now)

    def test_queue_requires_fresh_snapshot_and_valid_mode(self):
        with self.assertRaises(ValueError):
            self.state.queue({"mode": "checkpoint"})
        self.state.capture({"checkpoint": "a"}, "s1")
        with self.assertRaises(ValueError):
            self.state.queue({"mode": "generate"})
        with self.assertRaises(ValueError):
            self.state.queue({"mode": "lora"}, busy=True)
        result = self.state.queue({"mode": "lora"})
        self.assertTrue(result["ok"])
        self.assertIsNone(self.state.take("other-session"))
        self.assertEqual(self.state.take("s1")["id"], result["id"])

    def test_pending_command_expires(self):
        self.state.capture({}, "s1")
        self.state.queue({"mode": "lora"})
        self.now += 31
        status = self.state.status()
        self.assertFalse(status["pending"])
        self.assertFalse(status["last_result"]["ok"])

    def test_capture_selection_and_option_types(self):
        self.assertEqual(core.capture_selection(1, [("A", "a"), ("B", "b")]), "b")
        with self.assertRaises(ValueError):
            core.capture_selection(5, ["a"])
        self.assertEqual(core.compatible_option(2, 1.5), 2.0)
        with self.assertRaises(ValueError):
            core.compatible_option(1.5, 1)
        with self.assertRaises(ValueError):
            core.compatible_option("1", 1)


if __name__ == "__main__":
    unittest.main()
