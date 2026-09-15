---
name: phd-scraper
description: >
  Finds research PhD positions, funded fellowships, and active labs/PIs matching
  your profile via the installed portal-search CLIs (OpenAlex, Bluesky, and any
  skill added with /add-portal), deduplicates across runs, and presents matches
  with a quick fit check. Triggers on: find a PhD, search positions, PhD
  openings, find a lab, new positions, /search.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(python .agents/skills/*/cli/search.py *), Bash(python tools/phd_key.py:*), WebFetch, WebSearch, Agent, AskUserQuestion
framework_version: 0.1.0
---

# PhD Scraper

Find positions and labs, deduplicate, quick-score, present.

This is a harness-driven workflow, not an autonomous scraper. Only OpenAlex and
Bluesky CLI adapters ship; discover available web/agent tools before using them.
If delegation is unavailable, work sequentially and disclose the limitation.
Prioritize named doctoral calls; exclude postdocs unless requested. Separate
verified open calls from programs, watchlist leads, and closed calls according
to `../phd-application-assistant/07-web-research.md`.

## Invocation
- "Find PhD positions" / "/search"
- Optional focus: "/search protein design"; "broad" for all query categories;
  "health" for a portal health check only.

## Step 0 — Load state
1. Read `position_scraper/seen_positions.json` (create as `{"seen": {}}` if missing).
2. Read `positions_tracker.csv` for already-applied labs/roles.
3. Read `search-queries.md` (this directory).

## Step 1 — Search
Run the top 3 query categories by default; "broad" runs all.

**Primary: the installed portal CLIs under `.agents/skills/*/`.** Discover them by
reading every `SKILL.md` under `.agents/skills/*/SKILL.md` and use each portal's
own documented flags — do not guess. Honor `enabled: false` in a portal's
frontmatter by skipping it and noting it in the summary.

Translate the query terms into each portal's flags, scope recency with the
portal's `--jobage` (or filter client-side when the portal has no recency flag),
cap at ~20 results per call, and request `--format json`. Run portals in parallel
via the Agent tool. Tolerate per-portal failures — log and continue.

**Fallback: WebSearch** for portals in `search-queries.md` that have no CLI skill,
or when a CLI fails at runtime. Use the site-specific query strings directly and
tag results as `websearch`.

## Step 2 — Fetch & parse
For promising hits, run the portal's `detail` command (or WebFetch the posting)
to discover leads, then verify official/application links using the full evidence
checklist in `../phd-application-assistant/07-web-research.md`. Store source URLs,
checked_at, and unknown flags alongside the evidence. Do not bypass access blocks;
blocked/unverified leads belong on the watchlist, not the verified-open list.

Skip a candidate if its URL or its lab+title already appears in
`seen_positions.json` or in `positions_tracker.csv`.

## Step 2.5 — Mass-posting detection
If two or more results share a program/ID and differ only by location, consolidate
into one row and note the spread. Flag it as a caution signal, never an accusation.

## Step 3 — Quick fit
Rapid signal only, not the full rubric:
- **High:** the lab's recent work directly overlaps the candidate's methods.
- **Medium:** adjacent.
- **Low:** requires skills the candidate lacks.

Apply the gates from `../phd-application-assistant/03-position-evaluation.md` only
on verified evidence. Unknown degree, language, or funding produces a FLAG, not
Low or REJECT; a declared-but-lower language level is also a FLAG.

## Step 4 — Deduplicate & store
Derive each key with the helper, never by ad-hoc slugifying:

```bash
python tools/phd_key.py --lab "<lab/PI>" --title "<title>" --url "<url>"
```

Write **all** fetched items (new and skipped) to `seen_positions.json`:

```json
{"seen": {"<key>": {
  "title": "...", "lab": "...", "url": "...",
  "first_seen": "YYYY-MM-DD", "posted_date": null, "deadline": null,
  "fit": "high|medium|low", "status": "new|skipped|ranked|applied|expired",
  "portal": "<portal skill>", "source": "cli|websearch"
}}}
```

`/rank` extends entries additively with `rank_score`, `rank_verdict`, `rank_date`,
`gate`, `strengths`, `gaps`. Never drop those fields when rewriting. `null`
deadline means unknown unless explicit rolling/no-deadline evidence is recorded.
Add classification and the full evidence-checklist fields to each entry; do not
infer missing values or assume the CLI supplies them. Never downgrade existing
confirmed tracking state when regenerating search evidence.

## Step 5 — Present

```
## New PhD Matches - YYYY-MM-DD

Found X new (Y high, Z medium, W low).
skipped (disabled): <portal>, <portal>
fallback (websearch): <portal>, <portal>
health: <portal> - degraded|broken|inconclusive (reason)

| # | Fit | Position / Lab | Institution | Country | Funding | Deadline | URL |
|---|-----|----------------|-------------|---------|---------|----------|-----|
```

Present verified open calls first, with programs/watchlist and closed calls in
separate sections. Include linked evidence records and checked_at for every row.
Add 2–3 highlight bullets per high match (why it fits, requirements to check, red
flags). Then ask which numbers to evaluate, and route into
**phd-application-assistant**.

## Step 4.75 — Portal health check
Scrapers rot silently. For each enabled portal that ran: inspect results for
null/garbled fields, and compare yield to prior runs. A suspect portal gets one
sentinel probe with its SKILL.md example query, one retry, then a verdict. A 429
is **inconclusive (rate-limited)**, never "broken". `/search health` probes every
installed portal directly. The `enabled` toggle is the only thing the health check
may edit, and only with confirmation.

## Important rules
1. Never fabricate postings. Only present real CLI/WebSearch output.
2. Always deduplicate against `seen_positions.json` and `positions_tracker.csv`.
3. Only officially verified open doctoral calls enter the open-position list.
   Keep unknowns on the watchlist and verified closed calls separate.
4. Fetch `detail` only for promising hits, not every result.
5. Flag distribution patterns, never accuse a program of being fake.
6. Health verdicts come only from observed output; untestable = inconclusive.
