# 03 — Position Evaluation Rubric

Score every candidate against the profile. Total 100. Output per candidate in
`/rank` and `/apply`.

| Dimension | Weight | What you check |
|-----------|--------|----------------|
| Topic fit | 40 | Overlap between the lab's recent work and the candidate's methods/domain. |
| Activity & recency | 20 | At least one paper or page in the last 12 months; the group is actually running. |
| Funding & feasibility | 20 | Salaried/studentship attached? Eligible? Country schemes (ERC, DFG, UKRI, MEXT, CSC, NSERC, RTP, FWO…). |
| Supervision quality | 10 | Verified mentoring practices, student feedback/outcomes, supervision arrangements; otherwise unknown. |
| Logistics | 10 | Region, visa, language, start date vs the candidate's target. |

Bands: **80+ strong fit** · **65–79 good fit** · **50–64 worth a look** ·
**below 50 low fit** on known evidence. Unknown dimensions stay `?`; report
coverage rather than treating missing evidence as zero or a hard rejection.

## Vetoes (score = REJECT, with the reason named)
- **Deadline passed**, verified on an official source with timezone, and no
  rolling admission stated. Uncertain dates/timezones are FLAG, not REJECT.
- **Degree requirement** the candidate cannot meet (e.g. requires a completed
  Master's by the required date and the user confirms they cannot meet it).
  Unknown degree/completion timing is FLAG, not REJECT.
- **Language gate:** an undeclared language/level is unknown and a FLAG.
  A requirement *higher* than the candidate's declared level is
  a **FLAG**, not a veto — surface it, let the user judge.
- **Funding gate (only if the profile says funded-required):** no funding is
  attached and an official source confirms the scheme is self-funded.
  Unknown funding or eligibility is FLAG, not REJECT. Verify requirements on
  official sources and record evidence per `07-web-research.md`.

## Activity check (mandatory)
Before scoring Activity > 0, fetch one primary source (lab page, OpenAlex author
page, recent paper) that confirms recent work. An aggregator listing alone is not
evidence. Mark unconfirmed fields `?`.

## Supervision evidence
Group size is descriptive context only, not evidence of supervision quality or
attention. Do not award or deduct points from headcount. Corresponding authors
may be students or postdocs; verify PI role and supervisory eligibility on an
official institutional page. A PI listing does not prove an open position.

## Output shape

```
| Dimension              | Score | Evidence (verbatim / link) |
|------------------------|-------|----------------------------|
| Topic fit              |  /40  |                            |
| Activity & recency     |  /20  |                            |
| Funding & feasibility  |  /20  |                            |
| Supervision quality    |  /10  |                            |
| Logistics              |  /10  |                            |
| **Total / verdict**    |  /100 |                            |

Strengths:  (1–3 verbatim bullets)
Gaps / risks:  (1–3 verbatim bullets)
Gate:  PASS | FLAG <reason> | REJECT <reason>
Apply recommendation: apply now | apply if X | skip
```
