---
description: Generate a self-contained HTML dashboard of the application tracker.
agent: build
---

# /report — Application Dashboard

Generate a single self-contained HTML file (inline CSS/SVG, no external
dependencies, works offline) from `positions_tracker.csv` and the application
archives.

## Steps
1. Read `positions_tracker.csv` and, where present,
   `documents/applications/*/outcome.md`.
2. Build the report with:
   - Stat cards: total tracked, drafted, applied, interviews, offers, rejections.
   - Charts (inline SVG): status breakdown, country breakdown, funnel, and a
     timeline of activity by month.
   - A filterable table of all rows (lab, title, institution, country, funding,
     deadline, score, status, links).
3. Write `position_reports/report_<YYYY-MM-DD>.html`; tell the user the path and
   that it opens directly in a browser.
4. Re-runnable any time after `/apply` or `/outcome` adds entries.

## Rules
- No external network calls in the generated HTML; it must render offline.
- Never include referee contact details or other sensitive personal data in the report.
