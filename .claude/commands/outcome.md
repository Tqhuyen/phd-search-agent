---
description: Record what happened to an application; follow up on quiet ones.
agent: build
---

# /outcome — Record Application Results

Usage: `/outcome`, `/outcome <lab>`, `/outcome followup`.

## Record an outcome
Record actions and dates only from explicit user confirmation, never inferred
from generated drafts. Ask for the actual date if it is missing.
1. Update the `positions_tracker.csv` row for the lab/role: `status`
   (`applied`, `interview`, `offer`, `rejected`, `silent`), `outcome`, and dates.
   Status values are exactly: `drafted, applied, contacted, interview, offer,
   rejected, silent, expired`. Match the row by `lab` + `position_title`; create
   it only if the user applied outside `/apply`.
2. Write `documents/applications/<lab>_<role>/outcome.md` with dates and, if given,
   feedback (this is what a later `/interview` or calibration pass reads).
3. If a stage was reached, offer a thank-you note (draft only).

## /outcome followup
- Surface applications with no change for more than 10 days (`status: applied` or
  `contacted`, stale `contacted_on`).
- For each, draft a short channel-appropriate nudge using **only** claims from the
  materials already submitted. Drafts only, never sent, at most twice per application.
- Do not change `followed_up_on`, contact dates, or status when drafting. Update
  `followed_up_on` only after the user confirms sending and supplies the date.

## Calibration
- Once a few applications resolve, point the user back to `/setup` to recalibrate
  the fit rubric from what actually got interviews.
