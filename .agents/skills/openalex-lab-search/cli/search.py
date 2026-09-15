#!/usr/bin/env python3
"""openalex-lab-search: find active labs / PIs publishing on a topic.

Portal CLI for the phd-search-agent framework. Contract (same shape as every
portal skill in this repo):

  search.py search -q "<topic>" [--country DE] [--jobage <days>] [--limit N] [--format json|table|plain]
  search.py detail <openalex-author-id|url> [--format json|plain]

Stdlib only. OpenAlex is a public, key-free API (please keep the polite mailto).
JSON result shape: {"meta": {...}, "results": [ {id,title,institution,country,
date,url,description,...} ]}
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import date, timedelta

MAILTO = "phd-search-agent@users.noreply.github.com"
UA = "phd-search-agent/0.1 (mailto:%s)" % MAILTO
OPENALEX = "https://api.openalex.org"

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


def emit(meta: dict, results: list, fmt: str) -> int:
    if fmt == "json":
        print(json.dumps({"meta": meta, "results": results}, indent=2, ensure_ascii=False))
        return 0
    if fmt == "table":
        print("%-34s %-10s %-7s %-6s %s" % ("PI / LAB", "COUNTRY", "WORKS", "CORR", "INSTITUTION"))
        print("-" * 110)
        for r in results:
            print("%-34s %-10s %-7s %-6s %s" % (
                short(r.get("title") or "", 34), r.get("country") or "--",
                r.get("works", ""), r.get("corresponding", ""), short(r.get("institution") or "", 44)))
        print("\n%d result(s). Use --format json for ids and sample papers." % len(results))
        return 0
    # plain
    print("%s | %d result(s)" % (meta.get("query", ""), len(results)))
    print("-" * 100)
    for r in results:
        print("%s  [%s]  works=%s corr=%s" % (r.get("title"), r.get("country") or "--",
                                              r.get("works"), r.get("corresponding")))
        print("   %s" % r.get("institution") or "?")
        print("   %s" % r.get("url"))
        for s in (r.get("samples") or [])[:1]:
            print("   e.g. %s" % short(s, 90))
    return 0


def cmd_search(args) -> int:
    cutoff = (date.today() - timedelta(days=args.jobage)).isoformat()
    params = {
        "search": args.query,
        "filter": "from_publication_date:%s" % cutoff,
        "per-page": str(args.scan),
        "select": "id,display_name,publication_year,doi,authorships",
        "mailto": MAILTO,
    }
    url = "%s/works?%s" % (OPENALEX, urllib.parse.urlencode(params))
    try:
        data = get_json(url)
    except urllib.error.HTTPError as e:
        return fail("OpenAlex HTTP %s: %s" % (e.code, e.reason), "upstream")
    except urllib.error.URLError as e:
        return fail("network error: %s" % e.reason, "network")

    authors: dict = {}
    for w in data.get("results", []):
        title = w.get("display_name") or ""
        for a in w.get("authorships") or []:
            au = a.get("author") or {}
            aid = au.get("id")
            if not aid:
                continue
            rec = authors.setdefault(aid, {"name": au.get("display_name") or aid, "works": 0,
                                           "corresponding": 0, "insts": defaultdict(int),
                                           "countries": defaultdict(int), "samples": []})
            rec["works"] += 1
            if a.get("is_corresponding"):
                rec["corresponding"] += 1
            for inst in a.get("institutions") or []:
                if inst.get("display_name"):
                    rec["insts"][inst["display_name"]] += 1
                if inst.get("country_code"):
                    rec["countries"][inst["country_code"].upper()] += 1
            if title and len(rec["samples"]) < 3:
                rec["samples"].append(norm_ws(title))

    results = []
    for aid, rec in authors.items():
        if args.country and args.country.upper() not in rec["countries"]:
            continue
        top_inst = max(rec["insts"].items(), key=lambda kv: kv[1])[0] if rec["insts"] else "?"
        top_cc = max(rec["countries"].items(), key=lambda kv: kv[1])[0] if rec["countries"] else "?"
        results.append({
            "id": aid,
            "title": rec["name"],
            "institution": top_inst,
            "country": top_cc,
            "date": None,
            "url": aid,
            "description": rec["samples"][0] if rec["samples"] else None,
            "works": rec["works"],
            "corresponding": rec["corresponding"],
            "samples": rec["samples"],
        })
    results.sort(key=lambda r: (-(r["works"] + 2 * r["corresponding"]), r["title"].lower()))
    results = results[: args.limit]

    meta = {"query": args.query, "source": "openalex", "country": args.country,
            "window_since": cutoff, "matched_works": data.get("meta", {}).get("count"),
            "count": len(results)}
    return emit(meta, results, args.format)


def cmd_detail(args) -> int:
    target = args.target.strip()
    match = re.fullmatch(r"(?:https?://(?:openalex\.org/|api\.openalex\.org/authors/))?(A[0-9]+)/?", target)
    if not match:
        return fail("expected an OpenAlex author id like A5039930829", "bad-id")
    target = match.group(1)
    try:
        author = get_json("%s/authors/%s?mailto=%s" % (OPENALEX, target, MAILTO))
        works = get_json("%s/works?%s" % (OPENALEX, urllib.parse.urlencode({
            "filter": "author.id:%s" % target,
            "sort": "publication_date:desc",
            "per-page": "8",
            "select": "id,display_name,publication_year,doi",
            "mailto": MAILTO,
        })))
    except urllib.error.HTTPError as e:
        return fail("OpenAlex HTTP %s: %s" % (e.code, e.reason), "upstream")
    except urllib.error.URLError as e:
        return fail("network error: %s" % e.reason, "network")

    insts = author.get("last_known_institutions") or author.get("last_known_institution") or []
    if isinstance(insts, dict):
        insts = [insts]
    result = {
        "id": author.get("id"),
        "title": author.get("display_name"),
        "institution": (insts[0].get("display_name") if insts else None),
        "country": (insts[0].get("country_code") if insts else None),
        "url": author.get("id"),
        "orcid": author.get("orcid"),
        "works": author.get("works_count"),
        "cited_by": author.get("cited_by_count"),
        "h_index": (author.get("summary_stats") or {}).get("h_index"),
        "topics": [t.get("display_name") for t in (author.get("topics") or [])[:8]],
        "recent_works": [w.get("display_name") for w in works.get("results", [])],
    }
    if args.format == "json":
        print(json.dumps({"meta": {"source": "openalex", "id": target}, "result": result},
                         indent=2, ensure_ascii=False))
        return 0
    print("%s" % result["title"])
    print("  institution: %s (%s)" % (result["institution"] or "?", result["country"] or "?"))
    print("  works=%s  cited_by=%s  h_index=%s" % (result["works"], result["cited_by"], result["h_index"]))
    print("  openalex: %s" % result["url"])
    if result["topics"]:
        print("  topics: %s" % ", ".join(result["topics"]))
    print("  recent works:")
    for w in result["recent_works"]:
        print("    - %s" % w)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Find active labs/PIs on a topic via OpenAlex.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("search")
    p.add_argument("-q", "--query", required=True)
    p.add_argument("--country", default=None, help="ISO alpha-2 filter, e.g. DE")
    p.add_argument("--jobage", type=bounded_int(36500), default=1095, help="activity window in days (1-36500; default 1095)")
    p.add_argument("--scan", type=bounded_int(200), default=200, help="works to scan (1-200)")
    p.add_argument("--limit", type=bounded_int(200), default=25, help="results (1-200)")
    p.add_argument("--format", choices=["json", "table", "plain"], default="json")
    p.set_defaults(func=cmd_search)

    p = sub.add_parser("detail")
    p.add_argument("target")
    p.add_argument("--format", choices=["json", "plain"], default="json")
    p.set_defaults(func=cmd_detail)

    args = ap.parse_args()
    try:
        return args.func(args)
    except TimeoutError as e:
        return fail("request timed out: %s" % e, "network")
    except (json.JSONDecodeError, UnicodeError) as e:
        return fail("invalid upstream JSON: %s" % e, "upstream")


if __name__ == "__main__":
    sys.exit(main())
