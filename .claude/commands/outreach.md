---
description: Draft a cold email to a prospective supervisor (draft only, never sent).
agent: build
---

# /outreach — Supervisor Cold Email

Draft a short, specific email to a PI. **Draft only; never send.**

Usage: `/outreach <lab or PI>` or `/outreach <url>`.

## Steps
1. Identify the PI and confirm a **recent** (last 12 months) paper or project via
   `07-web-research.md`. If none can be confirmed, stop and say so — a generic
   email without a real hook does more harm than good.
2. Write the email per `05-outreach-email.md`: subject, one-sentence intro, one
   specific hook to their work, one concrete contribution, the ask, close.
3. Save to `documents/applications/<lab>_<role>/email.md` (or `documents/outreach/<lab>.md`
   when there is no formal application).
4. Log a tracker row if one does not exist with `status: "drafted"`; leave
   `contacted_on` empty. Preserve an existing confirmed status. Set `contacted`
   and the actual contact date only when the user confirms sending.
5. Present the draft. Suggest follow-up about 10 days after confirmed sending,
   not after drafting. Do not schedule or send anything.

## Rules
- 4–6 sentences, under ~150 words. No em-dashes, no cliches.
- One lab per email. Cite a verified paper by name.
- Never claim experience the profile does not support.
