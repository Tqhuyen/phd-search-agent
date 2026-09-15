---
description: Full application pipeline for one position — evaluate, tailor CV, draft SOP + email, review, record.
agent: build
---

# /apply — Full Application Pipeline

Run the **phd-application-assistant** skill workflow for one position.

Usage: `/apply <url>` or `/apply <paste the full posting text>`.

## Steps
1. **Evaluate fit.** Fetch and keep the posting **verbatim**. Research the lab/PI.
   Score via `03-position-evaluation.md` with gates/vetoes. Present the table and
   verdict; ask whether to proceed.
2. **Tailor the CV.** From the closest CV in `documents/cv/`, per `04-sop-and-cv.md`.
   Write `documents/cv/cv_<lab>_<role>.tex` (or `.md`).
3. **Draft the SOP.** Structure and length per `04-sop-and-cv.md`; write
   `documents/applications/<lab>_<role>/sop.md`.
4. **Draft the supervisor email.** Per `05-outreach-email.md`; write
   `documents/applications/<lab>_<role>/email.md`. Draft only — never send.
5. **Reviewer pass.** Spawn a fresh-context reviewer with the drafts inline, the
   posting text, and the rubric; redact contact details before sharing. If the
   harness cannot delegate, disclose and perform a separate review pass instead.
   It criticises missed keywords, unsupported
   claims, generic language, and eligibility gaps. Revise.
6. **Compile & inspect** the CV PDF (page limit, no orphaned titles, contact
   details extractable). Iterate on the source until clean.
7. **Record the application.** This is the single source of truth for writing a
   tracker row — the skill's Step 6 defers to it:
   - Derive `<lab>_<role>` once (see `documents/README.md`); if empty, stop.
   - Archive into `documents/applications/<lab>_<role>/`: `posting.txt` (verbatim),
     `cv.*`, `sop.md`, `email.md`.
   - Append one row to `positions_tracker.csv` with the header defined in that file.
     Match an existing row by `lab` + `position_title` first and update it; else
      append. Set new rows to `status: "drafted"`; preserve existing confirmed
      status. Record actions/dates only after explicit user confirmation.
   - Never touch `position_scraper/seen_positions.json` here.
8. **Present** the package with a verification checklist and open questions.
   Archive `evidence.md` with the complete `07-web-research.md` checklist,
   including official source URLs, checked_at, and unknown flags.

## Rules
- Never fabricate. Every claim traces to the profile or a verified source.
- Never submit forms, send email, or create accounts. The user acts.
