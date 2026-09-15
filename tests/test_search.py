import contextlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import unittest
from datetime import date
from unittest.mock import patch
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlsplit


ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


key = load("phd_key", "tools/phd_key.py")
oa = load("openalex_search", ".agents/skills/openalex-lab-search/cli/search.py")
bsky = load("bluesky_search", ".agents/skills/bsky-position-search/cli/search.py")
POST = "at://did:plc:abc123/app.bsky.feed.post/3abc123"


def invoke(module, *args):
    stdout, stderr = io.StringIO(), io.StringIO()
    with patch.object(sys, "argv", ["search.py", *args]):
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                status = module.main()
            except SystemExit as exc:
                status = exc.code
    return status, stdout.getvalue(), stderr.getvalue()


class KeyTests(unittest.TestCase):
    def test_full_inputs_disambiguate(self):
        pairs = [
            (("lab", "x" * 70 + "a", ""), ("lab", "x" * 70 + "b", "")),
            (("x" * 50 + "a", "t", ""), ("x" * 50 + "b", "t", "")),
            (("lab", "title", "https://a"), ("lab", "title", "https://b")),
            (("\u7814\u7a76", "\u535a\u58eb", ""), ("\u5927\u5b66", "\u535a\u58eb", "")),
            (("lab", "a+b", ""), ("lab", "a b", "")),
            (("a\x00b", "c", ""), ("a", "b\x00c", "")),
        ]
        for left, right in pairs:
            with self.subTest(left=left, right=right):
                self.assertNotEqual(key.key_for(*left), key.key_for(*right))

    def test_stability_length_and_unicode_normalization(self):
        for values in [("", "", ""), ("x" * 200, "y" * 200, "https://a")]:
            result = key.key_for(*values)
            self.assertEqual(result, key.key_for(*values))
            self.assertLessEqual(len(result), 80)
            self.assertRegex(result, r"^[a-z0-9_-]+$")
        self.assertEqual(key.key_for("caf\u00e9", "t", ""), key.key_for("cafe\u0301", "t", ""))

    def test_audit_invalid_json(self):
        with patch.object(key.os.path, "exists", return_value=True):
            with patch("builtins.open", return_value=io.StringIO("{")):
                status, stdout, stderr = invoke(key, "--audit")
        self.assertEqual(status, 1)
        self.assertEqual(stdout, "")
        self.assertEqual(json.loads(stderr)["code"], "audit")


class SearchTests(unittest.TestCase):
    def setUp(self):
        # Unexpected requests must fail locally, never reach the network.
        self.network = patch("urllib.request.urlopen", side_effect=AssertionError("unexpected network"))
        self.network.start()
        self.addCleanup(self.network.stop)

    def test_exact_openalex_cutoff(self):
        for today, days, expected in [
            (date(2026, 9, 15), 45, "2026-08-01"),
            (date(2024, 3, 1), 1, "2024-02-29"),
            (date(2026, 1, 1), 1, "2025-12-31"),
        ]:
            with self.subTest(today=today, days=days):
                with patch.object(oa, "date") as clock, patch.object(oa, "get_json", return_value={"results": []}) as fetch:
                    clock.today.return_value = today
                    status, stdout, stderr = invoke(oa, "search", "-q", "ML", "--jobage", str(days), "--scan", "1")
                self.assertEqual((status, stderr), (0, ""))
                params = parse_qs(urlsplit(fetch.call_args.args[0]).query)
                self.assertEqual(params["filter"], ["from_publication_date:" + expected])
                self.assertEqual(params["per-page"], ["1"])
                self.assertEqual(json.loads(stdout)["meta"]["window_since"], expected)

    def test_numeric_inputs_rejected_before_fetch(self):
        for module, options in [(oa, {"--jobage": 36500, "--limit": 200, "--scan": 200}),
                                (bsky, {"--jobage": 36500, "--limit": 100})]:
            for option, maximum in options.items():
                for value in ["0", "-1", "1.5", "abc", str(maximum + 1), "9" * 100]:
                    with self.subTest(module=module.__name__, option=option, value=value):
                        with patch.object(module, "get_json") as fetch:
                            status, stdout, stderr = invoke(module, "search", "-q", "ML", option, value)
                        self.assertEqual(status, 2)
                        self.assertEqual(stdout, "")
                        self.assertIn("error:", stderr)
                        fetch.assert_not_called()

    def test_numeric_boundaries_accepted(self):
        for module, maximum in [(oa, 200), (bsky, 100)]:
            for days, limit in [(1, 1), (36500, maximum)]:
                with self.subTest(module=module.__name__, days=days):
                    with patch.object(module, "get_json", return_value={}):
                        status, _, stderr = invoke(module, "search", "-q", "ML", "--jobage", str(days), "--limit", str(limit))
                    self.assertEqual((status, stderr), (0, ""))

    def test_invalid_detail_ids_never_fetch(self):
        cases = [(oa, ["A", "Aabc", "A123?x=y", "https://evil.org/A123", "https://openalex.org/W123", "A123/extra"]),
                 (bsky, ["at://", "at://did:plc:abc/wrong/123", POST + "/extra", POST + "?x=y",
                         "https://bsky.app/profile/a.b/post/key/extra", "https://evil.org/profile/a.b/post/key"])]
        for module, targets in cases:
            for target in targets:
                with self.subTest(target=target):
                    with patch.object(module, "get_json") as fetch:
                        status, stdout, stderr = invoke(module, "detail", target)
                    self.assertEqual(status, 1)
                    self.assertEqual(stdout, "")
                    self.assertEqual(json.loads(stderr)["code"], "bad-id")
                    fetch.assert_not_called()

    def test_openalex_valid_detail_ids(self):
        for target in ["A123", "https://openalex.org/A123", "https://api.openalex.org/authors/A123/"]:
            with self.subTest(target=target):
                with patch.object(oa, "get_json", side_effect=[{"id": "A123"}, {"results": []}]) as fetch:
                    status, stdout, stderr = invoke(oa, "detail", target)
                self.assertEqual((status, stderr), (0, ""))
                self.assertEqual(json.loads(stdout)["meta"]["id"], "A123")
                self.assertIn("/authors/A123?", fetch.call_args_list[0].args[0])

    def test_bluesky_missing_posts(self):
        for data in [{}, {"thread": {}}, {"thread": {"$type": "app.bsky.feed.defs#notFoundPost"}},
                     {"thread": {"$type": "app.bsky.feed.defs#blockedPost"}}]:
            with self.subTest(data=data):
                with patch.object(bsky, "get_json", return_value=data):
                    status, stdout, stderr = invoke(bsky, "detail", POST)
                self.assertEqual((status, stdout), (1, ""))
                self.assertEqual(json.loads(stderr)["code"], "not-found")

    def test_bluesky_url_resolution_and_did_urls(self):
        post = {"thread": {"post": {"record": {"text": "PhD"}, "author": {"handle": "a.b"}}}}
        for actor in ["a.b", "did:plc:abc123"]:
            replies = [{"did": "did:plc:abc123"}, post] if actor == "a.b" else [post]
            with self.subTest(actor=actor):
                with patch.object(bsky, "get_json", side_effect=replies) as fetch:
                    status, stdout, stderr = invoke(bsky, "detail", "https://bsky.app/profile/%s/post/3abc123" % actor)
                self.assertEqual((status, stderr), (0, ""))
                self.assertEqual(json.loads(stdout)["result"]["id"], POST)
                self.assertEqual(fetch.call_count, len(replies))

    def test_missing_resolved_did(self):
        with patch.object(bsky, "get_json", return_value={}):
            status, stdout, stderr = invoke(bsky, "detail", "https://bsky.app/profile/a.b/post/key")
        self.assertEqual((status, stdout), (1, ""))
        self.assertEqual(json.loads(stderr)["code"], "resolve")

    def test_transport_and_json_errors(self):
        commands = [(oa, ["search", "-q", "ML"]), (oa, ["detail", "A123"]),
                    (bsky, ["search", "-q", "ML"]), (bsky, ["detail", POST]),
                    (bsky, ["detail", "https://bsky.app/profile/a.b/post/key"])]
        for module, args in commands:
            for error, code in [(TimeoutError("slow"), "network"), (URLError("offline"), "network"),
                                (HTTPError("https://example.org", 503, "unavailable", {}, None), "upstream")]:
                with self.subTest(module=module.__name__, args=args, error=error):
                    with patch("urllib.request.urlopen", side_effect=error):
                        status, stdout, stderr = invoke(module, *args)
                    self.assertEqual((status, stdout), (1, ""))
                    self.assertEqual(json.loads(stderr)["code"], code)
            for body in [b"not JSON", b"\xff"]:
                with self.subTest(module=module.__name__, args=args, body=body):
                    with patch("urllib.request.urlopen", return_value=io.BytesIO(body)):
                        status, stdout, stderr = invoke(module, *args)
                    self.assertEqual((status, stdout), (1, ""))
                    self.assertEqual(json.loads(stderr)["code"], "upstream")

    def test_later_detail_request_errors(self):
        for module, target, first in [(oa, "A123", {}),
                                      (bsky, "https://bsky.app/profile/a.b/post/key", {"did": "did:plc:abc"})]:
            for error in [TimeoutError("slow"), json.JSONDecodeError("bad", "", 0)]:
                with self.subTest(module=module.__name__, error=error):
                    with patch.object(module, "get_json", side_effect=[first, error]):
                        status, stdout, stderr = invoke(module, "detail", target)
                    self.assertEqual((status, stdout), (1, ""))
                    self.assertIn("error", json.loads(stderr))


if __name__ == "__main__":
    unittest.main()
