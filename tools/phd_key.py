#!/usr/bin/env python3
"""Canonical dedup key for a PhD position/lab.

The key must be a pure function of the posting so two runs never store the same
item twice. Length-caps long titles and disambiguates the cap with a hash so a
truncated title stays stable and two different long titles never collide.

  python tools/phd_key.py --lab "<lab or PI>" --title "<title>" [--url "<url>"]
  python tools/phd_key.py --audit            # report keys that predate the rule
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import unicodedata

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def slug(text: str, limit: int = 60) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
    return s[:limit].strip("-")


def key_for(lab: str, title: str, url: str) -> str:
    fields = [unicodedata.normalize("NFC", value or "").strip() for value in (lab, title, url)]
    digest = hashlib.sha256(json.dumps(fields, ensure_ascii=False).encode("utf-8")).hexdigest()[:16]
    base = ("%s__%s" % (slug(fields[0], 40), slug(fields[1]))).strip("_") or "unknown"
    return base[:63].rstrip("-_") + "-" + digest


def main() -> int:
    ap = argparse.ArgumentParser(description="Canonical dedup key for a PhD posting.")
    ap.add_argument("--lab")
    ap.add_argument("--title")
    ap.add_argument("--url", default="")
    ap.add_argument("--audit", action="store_true")
    ap.add_argument("--state", default="position_scraper/seen_positions.json")
    args = ap.parse_args()

    if args.audit:
        path = args.state
        if not os.path.exists(path):
            print(json.dumps({"audited": 0, "legacy": [], "note": "no state file"}))
            return 0
        try:
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, ValueError) as e:
            print(json.dumps({"error": str(e), "code": "audit"}), file=sys.stderr)
            return 1
        legacy = []
        for k, v in (data.get("seen") or {}).items():
            expected = key_for(v.get("lab", ""), v.get("title", ""), v.get("url", ""))
            if k != expected:
                legacy.append(k)
        print(json.dumps({"audited": len(data.get("seen") or {}), "legacy": legacy}, indent=2))
        return 0

    if not args.title:
        print("error: --title is required", file=sys.stderr)
        return 2
    print(key_for(args.lab or "", args.title, args.url))
    return 0


if __name__ == "__main__":
    sys.exit(main())
