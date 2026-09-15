#!/usr/bin/env python3
"""bsky-position-search: search recent PhD/advert posts on Bluesky.

Portal CLI for the phd-search-agent framework. Bluesky's public AppView API is
key-free. Same contract as every portal skill:

  search.py search -q "PhD position machine learning" [--jobage <days>] [--limit N] [--format json|table|plain]
  search.py detail <at-uri|bsky-post-url> [--format json|plain]

JSON result shape: {"meta": {...}, "results": [ {id,title,company,location,date,url,description} ]}
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

BSKY = "https://api.bsky.app/xrpc"
UA = "phd-search-agent/0.1"

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass


def get_json(url: str, timeout: int = 45):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.load(resp)


def norm_ws(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def short(text: str, n: int) -> str:
    text = norm_ws(text)
    return text if len(text) <= n else text[: n - 1] + "\u2026"


def fail(message: str, code: str = "error") -> int:
    print(json.dumps({"error": message, "code": code}, ensure_ascii=False), file=sys.stderr)
    return 1


def bounded_int(maximum: int):
    def parse(value: str) -> int:
        try:
            number = int(value)
        except ValueError:
            raise argparse.ArgumentTypeError("expected an integer") from None
        if not 1 <= number <= maximum:
            raise argparse.ArgumentTypeError("must be between 1 and %d" % maximum)
        return number
    return parse


def bsky_url(at_uri: str, handle: str) -> str:
    rkey = at_uri.rsplit("/", 1)[-1] if at_uri else ""
    return "https://bsky.app/profile/%s/post/%s" % (handle, rkey)


def emit(meta: dict, results: list, fmt: str) -> int:
    if fmt == "json":
        print(json.dumps({"meta": meta, "results": results}, indent=2, ensure_ascii=False))
        return 0
    if fmt == "table":
        print("%-12s %-28s %s" % ("DATE", "AUTHOR", "POST"))
        print("-" * 110)
        for r in results:
            print("%-12s %-28s %s" % (r.get("date") or "?", short("@" + (r.get("author") or ""), 28),
                                      short(r.get("description") or "", 64)))
        print("\n%d result(s)." % len(results))
        return 0
    print("%s | %d result(s)" % (meta.get("query", ""), len(results)))
    print("-" * 100)
    for r in results:
        print("%s  @%s" % (r.get("date"), r.get("author")))
        print("   %s" % short(r.get("description") or "", 160))
        print("   %s" % r.get("url"))
    return 0


def cmd_search(args) -> int:
    params = {"q": args.query, "limit": str(min(max(args.limit * 3, 25), 100)), "sort": "latest"}
    url = "%s/app.bsky.feed.searchPosts?%s" % (BSKY, urllib.parse.urlencode(params))
    try:
        data = get_json(url)
    except urllib.error.HTTPError as e:
        return fail("Bluesky HTTP %s: %s" % (e.code, e.reason), "upstream")
    except urllib.error.URLError as e:
        return fail("network error: %s" % e.reason, "network")

    cutoff = datetime.now(timezone.utc) - timedelta(days=args.jobage)
    seen, results = set(), []
    for p in data.get("posts", []):
        at_uri = p.get("uri", "")
        if not at_uri or at_uri in seen:
            continue
        seen.add(at_uri)
        rec = p.get("record") or {}
        created = rec.get("createdAt") or p.get("indexedAt") or ""
        try:
            ts = datetime.fromisoformat(created.replace("Z", "+00:00"))
        except Exception:
            ts = None
        if ts and ts < cutoff:
            continue
        handle = (p.get("author") or {}).get("handle", "unknown")
        text = norm_ws(rec.get("text") or "")
        results.append({
            "id": at_uri,
            "title": short(text, 80),
            "company": None,
            "location": None,
            "date": (ts.date().isoformat() if ts else (created[:10] or None)),
            "url": bsky_url(at_uri, handle),
            "description": text,
            "author": handle,
            "likes": p.get("likeCount", 0),
        })
    results = results[: args.limit]
    meta = {"query": args.query, "source": "bluesky", "window_days": args.jobage, "count": len(results)}
    return emit(meta, results, args.format)


def cmd_detail(args) -> int:
    target = args.target.strip()
    actor = r"(?:did:[a-z0-9]+:[A-Za-z0-9._:%-]+|[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+)"
    rkey_pattern = r"[A-Za-z0-9_~:-][A-Za-z0-9._~:-]{0,511}"
    m = re.fullmatch(r"https?://bsky\.app/profile/(%s)/post/(%s)/?(?:[?#][^\s]*)?" % (actor, rkey_pattern), target)
    if m:
        handle, rkey = m.group(1), m.group(2)
        # resolve handle -> did, then build at-uri
        did = handle
        if not handle.startswith("did:"):
            resolved = get_json("%s/com.atproto.identity.resolveHandle?handle=%s"
                                % (BSKY, urllib.parse.quote(handle)))
            did = resolved.get("did", "")
            if not isinstance(did, str) or not re.fullmatch(r"did:[a-z0-9]+:[A-Za-z0-9._:%-]+", did):
                return fail("could not resolve handle to a DID", "resolve")
        at_uri = "at://%s/app.bsky.feed.post/%s" % (did, rkey)
    elif re.fullmatch(r"at://%s/app\.bsky\.feed\.post/%s" % (actor, rkey_pattern), target):
        at_uri = target
        handle = "unknown"
    else:
        return fail("expected an at:// uri or a bsky.app post url", "bad-id")

    url = "%s/app.bsky.feed.getPostThread?uri=%s" % (BSKY, urllib.parse.quote(at_uri))
    try:
        data = get_json(url)
    except urllib.error.HTTPError as e:
        return fail("Bluesky HTTP %s: %s" % (e.code, e.reason), "upstream")
    except urllib.error.URLError as e:
        return fail("network error: %s" % e.reason, "network")

    post = ((data.get("thread") or {}).get("post") or {})
    if not post:
        return fail("Bluesky post not found or unavailable", "not-found")
    rec = post.get("record") or {}
    handle = (post.get("author") or {}).get("handle", handle)
    embeds = []
    ext = (post.get("embed") or {}).get("external")
    if isinstance(ext, dict) and ext.get("uri"):
        embeds.append(ext["uri"])
    result = {
        "id": at_uri,
        "title": short(norm_ws(rec.get("text") or ""), 80),
        "url": bsky_url(at_uri, handle),
        "author": handle,
        "date": (rec.get("createdAt") or "")[:10],
        "description": norm_ws(rec.get("text") or ""),
        "embeds": embeds,
    }
    if args.format == "json":
        print(json.dumps({"meta": {"source": "bluesky", "id": at_uri}, "result": result},
                         indent=2, ensure_ascii=False))
        return 0
    print("@%s  %s" % (result["author"], result["date"]))
    print(result["description"])
    if result["embeds"]:
        for e in result["embeds"]:
            print("link: %s" % e)
    print(result["url"])
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Search recent PhD/advert posts on Bluesky.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("search")
    p.add_argument("-q", "--query", required=True)
    p.add_argument("--jobage", type=bounded_int(36500), default=45, help="only posts newer than N days (1-36500)")
    p.add_argument("--limit", type=bounded_int(100), default=25, help="results (1-100)")
    p.add_argument("--format", choices=["json", "table", "plain"], default="json")
    p.set_defaults(func=cmd_search)

    p = sub.add_parser("detail")
    p.add_argument("target")
    p.add_argument("--format", choices=["json", "plain"], default="json")
    p.set_defaults(func=cmd_detail)

    args = ap.parse_args()
    try:
        return args.func(args)
    except urllib.error.HTTPError as e:
        return fail("Bluesky HTTP %s: %s" % (e.code, e.reason), "upstream")
    except urllib.error.URLError as e:
        return fail("network error: %s" % e.reason, "network")
    except TimeoutError as e:
        return fail("request timed out: %s" % e, "network")
    except (json.JSONDecodeError, UnicodeError) as e:
        return fail("invalid upstream JSON: %s" % e, "upstream")


if __name__ == "__main__":
    sys.exit(main())
