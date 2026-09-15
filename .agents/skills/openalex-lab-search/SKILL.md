---
name: openalex-lab-search
version: 0.1.0
description: >
  Search active labs and principal investigators publishing on a research topic
  via the OpenAlex scholarly graph (public, key-free). Use to find who is working
  on a topic right now, filter by country, and look up one author's profile and
  recent papers. Trigger phrases: find a lab, who works on X, find a supervisor,
  active research groups, professor working on, OpenAlex author lookup.
context: fork
enabled: true
allowed-tools: Bash(python .agents/skills/openalex-lab-search/cli/search.py *)
---

# OpenAlex Lab Search

Finds **author leads** by scanning recent works on a topic and ranking authors
by output plus corresponding-author count. Corresponding authors may be students
or postdocs; this is not proof of PI status, supervision eligibility, or a vacancy.
Verify institutional roles and current official doctoral calls with
`phd-application-assistant` Step 1.

> Never put candidate/referee contact details in queries or API parameters.
> Check CLI configuration before use; do not supply a private address as `mailto`.

## Commands

```bash
python .agents/skills/openalex-lab-search/cli/search.py search -q "<topic>" \
    [--country DE] [--jobage <days>] [--scan <50-200>] [--limit N] [--format json|table|plain]

python .agents/skills/openalex-lab-search/cli/search.py detail <A-id|url> [--format json|plain]
```

Key flags:
- `-q/--query` — topic terms (2–6 keywords work best).
- `--country` — ISO alpha-2 (e.g. `DE`, `GB`, `CA`, `AU`).
- `--jobage` — activity window in days (default 1095 = ~3 years).
- `--scan` — recent works to scan (50–200, default 200).
- `--limit` — max PIs returned.
- `--format` — `json` (default), `table`, `plain`.

`detail` takes an OpenAlex author id like `A5039930829` and returns affiliations,
h-index, topics, and the 8 most recent works.

## Examples

```bash
# Who works on protein design in Germany?
python .agents/skills/openalex-lab-search/cli/search.py search -q "protein design" --country DE --format table

# Recent RL groups in the UK
python .agents/skills/openalex-lab-search/cli/search.py search -q "reinforcement learning" --country GB --jobage 730 --format table

# Deep profile of one PI
python .agents/skills/openalex-lab-search/cli/search.py detail A5039930829 --format json
```

## Output contract
`{"meta": {"query", "source", "country", "window_since", "matched_works", "count"},
"results": [{id, title, institution, country, date, url, description, works,
corresponding, samples}]}`. Errors go to stderr as `{"error","code"}` with exit 1.

## Notes
- Author identities on OpenAlex can merge/split. Confirm across the lab page and
  Google Scholar before trusting one id.
- Ranking favors corresponding authors, but a corresponding author can still be a
  postdoc. Verify seniority on the lab page.
- Rate limits are generous but not unlimited; a few queries per topic per run.
