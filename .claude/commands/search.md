---
description: Find new PhD positions and labs across portal CLIs; dedup and quick-score.
agent: build
---

# /search — Find New PhD Positions and Labs

Run the **phd-scraper** skill (`.claude/skills/phd-scraper/SKILL.md`) end to end.

## Inputs
- Optional focus area: `/search protein design`.
- `broad` — run all query categories, not just the top 3.
- `health` — run only the portal health check (Step 4.75), no searching.

## Steps (see the skill for the full text)
1. **Load state:** `position_scraper/seen_positions.json`, `positions_tracker.csv`,
   `search-queries.md`.
2. **Search** the installed portals under `.agents/skills/*/cli/` in parallel,
   using each portal's own SKILL.md flags. Scope recency with `--jobage`. Honor
   `enabled: false`. Fall back to WebSearch where no CLI exists.
3. **Fetch detail** for promising hits; verify official sources and record the
   full evidence checklist from `07-web-research.md`, including checked_at.
4. **Mass-posting check** within the run.
5. **Quick fit** (High/Medium/Low) with the language/funding gate as an override.
6. **Dedup** against seen state and the tracker; key via `tools/phd_key.py`.
7. **Health check** suspect portals (bounded).
8. **Present** named doctoral calls first, sorted by fit within classification.
   Separate verified open calls, programs, watchlist leads, and closed calls.
   Exclude postdocs unless requested; unknown degree/language/funding is a FLAG.

## Example portal calls
```bash
python .agents/skills/openalex-lab-search/cli/search.py search -q "<topic>" --country <XX> --format json
python .agents/skills/bsky-position-search/cli/search.py search -q "<topic> PhD position" --jobage 45 --format json
```

## After presenting
Ask which numbers to evaluate. Route the chosen ones into **phd-application-assistant**
(Step 1 fit evaluation first). If 8+ new results, suggest `/rank`.
