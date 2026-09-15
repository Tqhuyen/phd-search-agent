---
description: Build or update the candidate profile and search configuration.
agent: build
---

# /setup — Candidate Profile Onboarding

Build the run contract in `.claude/skills/phd-application-assistant/01-candidate-profile.md`
and the search config in `.claude/skills/phd-scraper/search-queries.md`.

## Step 0: Detect what exists
- On a fresh clone, create the missing private profile from
  `templates/candidate-profile.md`, private search queries from
  `templates/search-queries.md`, and `positions_tracker.csv` from
  `templates/positions_tracker.csv`. Never overwrite existing files.
- If `01-candidate-profile.md` already has content, say so and ask whether to
  update, extend, or start over. `/setup --section search` reconfigures only the
  search queries.
- Check `documents/` for `cv/`, `diplomas/`, `references/`.

## Step 1: Choose a path (ask the user)
1. **Documents folder (Path A).** If `documents/` has material, read the CV PDF
   or `.tex`, diplomas, references, and any past applications. Extract into the
   profile. Idempotent — safe to re-run as material is added.
2. **Paste a CV.** Ask the user to paste a CV; parse it into the profile.
3. **Interview.** Ask the questions below, batched, one section at a time.

Never invent details. Leave a field blank rather than guessing.
Unknown degree, language, or funding stays unknown, never an automatic rejection.
Keep the profile and personalized queries private in their ignored paths; do not
transmit contact details to searches, Sheets, APIs, or external tools.

## Step 2: Interview sections (batch these)
1. Identity and links.
2. Target: field keywords (2–6), degree, start term, regions, funding need, deal-breakers.
3. Education (table rows).
4. Research experience — for each: problem, method, tools, result, what you owned.
5. Methods & skills **in context**.
6. Publications and awards.
7. **Languages** — every language and level (CEFR). This drives the language gate;
   ask explicitly rather than inferring.
8. Referees.
9. What energizes / drains you (for latent-opportunity discovery).

## Step 3: Write the profile
Fill `01-candidate-profile.md`. Keep the user's phrasing for achievements; do not
inflate numbers.

## Step 4: Configure search
Update `search-queries.md`:
- Category 1 = the 2–6 topic keywords.
- Category 2 = adjacent methods.
- Regions → `--country` ISO codes.
- Portals to run.
Also suggest role/lab types the user may not have considered, based on the profile.

## Step 5: Summarize
Report: profile sections filled, gaps left blank, search queries configured, and
the recommended next command (`/search`). Remind the user that everything from
here is draft-only and they remain the sender/decision-maker.
