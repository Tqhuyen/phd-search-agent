---
name: phd-application-assistant
description: >
  Assists with research PhD applications: evaluating a position or lab for fit,
  tailoring a CV, drafting a statement of purpose and a cold email to a
  supervisor, and preparing for interviews. Triggers on: PhD position, doctoral
  position, supervisor, advisor, lab, statement of purpose, SOP, research
  proposal, funding, scholarship, assistantship, cold email to professor,
  interview prep, fit, apply.
allowed-tools: Read, Glob, Grep, WebFetch, WebSearch, Bash, Edit, Write, AskUserQuestion
framework_version: 0.1.0
---

# PhD Application Assistant

This skill is the **drafter**. `phd-scraper` finds positions; this skill turns one
into a verified, tailored application.

## Cardinal rules — read before acting

These mirror OpenResearch's experiment-tree discipline. Breaking one silently
corrupts the output.

1. **Freeze the candidate profile, then branch.** `01-candidate-profile.md` is
   the run contract. Never silently widen or embellish it mid-application. Want a
   different framing for a different lab? Branch a new draft — do not mutate the
   profile.
2. **Never fabricate.** No invented publications, skills, degrees, or results.
   Every claim in a CV, SOP, or email must trace to the profile or a primary
   source. A genuine gap is stated as a gap, never stuffed.
3. **Verify before claiming.** A lab's topic is only "active" if a recent
   (last 12 months) paper or page confirms it. Fetch, then cite. `07-web-research.md`.
4. **Draft, never send.** Produce the email and the application package; the user
   sends. Never submit forms, send mail, or create accounts on their behalf.

## Workflow

When the user provides a position or lab (URL or text), follow this workflow.

### Step 0: Load the profile
Read `01-candidate-profile.md`. If it is unfilled, run `/setup` first. Read
`03-position-evaluation.md` for the rubric and `02-writing-style.md` for voice.

### Step 1: Evaluate fit
- Fetch the posting per `07-web-research.md`; never bypass access blocks.
- Record the full official-source evidence checklist, checked_at, classification,
  and unknown flags. Distinguish programs/watchlist from verified open calls.
- Keep the **full posting text verbatim** for the archive — never a summary.
- Identify required competencies, methods, keywords, funding, and deadlines.
- Research the lab/PI (site, OpenAlex, recent papers, group size) per `07-web-research.md`.
- Score against `03-position-evaluation.md` (topic fit, activity, funding,
  supervision, logistics) with the **Language/Gate rule** and **vetoes**.
- Present the score table and verdict, then ask whether to proceed.

### Step 2: Tailor the CV
- Read the closest existing CV in `documents/cv/` as a starting point.
- Follow `04-sop-and-cv.md`. Create `documents/cv/cv_<lab>_<role>.tex` (or `.md`).
- Reorder emphasis toward the lab's methods; keep claims frozen to the profile.

### Step 3: Draft the statement of purpose
- Follow the structure and limits in `04-sop-and-cv.md`.
- Create `documents/applications/<lab>_<role>/sop.md`.
- Every paragraph must connect **specific** evidence from the profile to **specific**
  requirements of the position. No generic "I am passionate about AI".

### Step 4: Draft the supervisor email
- Follow `05-outreach-email.md` (4–6 sentences, one concrete reference to their
  recent work, one concrete contribution the candidate can make).
- Create `documents/applications/<lab>_<role>/email.md`. Draft only.

### Step 5: Reviewer pass
- Spawn a second agent with a fresh context (the reviewer). Give it the drafts
  **inline** with contact details redacted, the posting text, and the rubric.
  Use only available harness tools; if delegation is absent, do a separate
  review pass and disclose that it was not an independent reviewer.
- The reviewer critiques: missed keywords, unsupported claims, generic language,
  funding/eligibility gaps. The drafter then revises. This catches what one pass
  leaves in.

### Step 6: Record the application
- Append a row to `positions_tracker.csv` (header and match-then-update rule in
  `/apply` Step 7). Archive the posting text, CV, SOP, and email into
  `documents/applications/<lab>_<role>/`.
- Set new rows to `drafted`; preserve existing confirmed status. Record applied,
  contacted, or follow-up actions and dates only on explicit user confirmation.

### Step 7: Interview preparation (on request)
- Follow `06-interview-prep.md`. Build STAR examples from the profile, map likely
  research questions, and prepare questions for the PI.

## Reference files

| File | Purpose |
|------|---------|
| `01-candidate-profile.md` | Education, research, methods, publications, funding, languages |
| `02-writing-style.md` | Voice, structure, do's and don'ts |
| `03-position-evaluation.md` | Fit rubric, vetoes, the language/funding gates |
| `04-sop-and-cv.md` | SOP structure + CV tailoring rules |
| `05-outreach-email.md` | Cold-email anatomy + templates |
| `06-interview-prep.md` | Research-interview framework, STAR, PI questions |
| `07-web-research.md` | Trust boundary, official verification, evidence checklist |

## Quick commands

- "Evaluate this PhD position" — Step 1 only
- "Tailor my CV for [lab]" — Step 2 only
- "Write my SOP for [lab]" — Step 3 only
- "Draft an email to [professor]" — Step 4 only
- "Prep me for an interview with [PI]" — Step 7 only
