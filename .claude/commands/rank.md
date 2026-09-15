---
description: Batch-score newly found positions against the fit rubric.
agent: build
---

# /rank — Rank New Positions

Bridge `/search` and `/apply`: score every newly seen position against the full
rubric in `.claude/skills/phd-application-assistant/03-position-evaluation.md`
and return a ranked shortlist.

## Steps
1. Read `position_scraper/seen_positions.json`; select entries with
   `status: "new"` (or a user-specified subset).
2. For each, spawn a scoring agent (parallel, fresh context) that:
   - Fetches the posting and the lab's recent output (per `07-web-research.md`).
   - Scores the five dimensions and applies vetoes/gates.
   - Returns the score table plus 1–3 verbatim `strengths` and `gaps` bullets.
3. Write results back to the entry **additively** — never drop existing fields:
   `rank_score` (0–100), `rank_verdict` (band), `rank_date`, `gate`
   (PASS/FLAG/REJECT + note), `strengths`, `gaps`, and set `status: "ranked"`.
   Mark dead postings `status: "expired"` rather than deleting them.
4. Present named doctoral calls first, sorted by score within classification;
   keep programs/watchlist separate from verified open calls. Include the full
   evidence record from `07-web-research.md`, checked_at, and unknown flags.

## Rules
- A scoring agent that cannot fetch a source returns `?` for that dimension, not
  a guess. Missing data lowers confidence, it does not raise the score.
- Deadline urgency: within 7 days = act now; within 30 = plan. Mark expired only
  from official verified date/time/timezone evidence; otherwise FLAG uncertainty.
- Never fabricate a score. If the posting is unreadable, mark it and say so.

## After presenting
Offer to run `/apply` on a chosen number.
