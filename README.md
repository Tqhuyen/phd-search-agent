# PhD Search Agent

*A harness-driven framework for doctoral search and application drafts.*

An AI agent framework for finding **research PhD positions and labs**, evaluating
fit, and producing tailored applications (CV, statement of purpose, supervisor
email). Conceptual inspiration comes from
[MadsLorentzen/ai-job-search](https://github.com/MadsLorentzen/ai-job-search) and
[alphaXiv/OpenResearch](https://github.com/alphaXiv/OpenResearch). These are
conceptual references, not copied code or bundled integrations.

This is not a standalone application or autonomous service. Markdown workflows
are executed by an agent harness using tools available in that session. Only two
real source CLI adapters ship: OpenAlex author discovery and Bluesky ad discovery.
Official-page verification, drafting, review, reports, and Sheets sync require
harness tools; no configured Sheets MCP or automatic upload is included.

> Draft-only by design: the agent never submits applications, sends email, or
> creates accounts. You remain the sender and the decision-maker.

## Workflow

```
/setup          /search                 /rank              /apply <url>
  |                |                      |                   |
  v                v                      v                   v
Fill profile    Find positions        Score the          Evaluate fit
+ queries       & labs (CLIs)         whole pool         Tailor CV + SOP
  |                |                      |              + supervisor email
  v                v                      v                   |
Profile +       Dedup, quick-fit      Ranked shortlist    Reviewer pass
search config   present table          with gates         + record + archive
                   \___________________/                     |
                            |                                v
                      pick a number  ------------------->  /outcome
                                                     /outreach  /interview  /report
```

## Prerequisites
- **Python 3.9+** (the portal CLIs are stdlib-only).
- An agent harness that reads `AGENTS.md` + skills: **opencode** (see
  `opencode.json`), or **Claude Code** (reads `.claude/` natively).
- Optional: a LaTeX toolchain if you want PDF CV/SOP output. Markdown is the
  fallback when no TeX is present.

## Quick start
```bash
# 1. Enter the folder and start your harness (opencode / claude)
# 2. Build the profile (documents folder, pasted CV, or interview)
/setup
# 3. Find positions and labs
/search
# 4. (optional) rank a long pool
/rank
# 5. Apply to one
/apply https://example.edu/jobs/phd-ml-2027
```

Run the portal CLIs directly any time:
```bash
python .agents/skills/openalex-lab-search/cli/search.py search -q "protein design" --country DE --format table
python .agents/skills/bsky-position-search/cli/search.py  search -q "PhD position machine learning" --jobage 30 --format table
python .agents/skills/openalex-lab-search/cli/search.py detail A5039930829 --format json
```

## Commands
| Command | What it does |
|---------|--------------|
| `/setup` | Build/refresh the candidate profile and search queries (3 onboarding paths). |
| `/search` | Find new positions and labs via the portal CLIs; dedup, quick-fit, present. |
| `/rank` | Batch-score the pool against the fit rubric; ranked shortlist with gates. |
| `/apply <url>` | Full pipeline: evaluate → CV → SOP → supervisor email → reviewer → record. |
| `/outreach <lab>` | Draft a specific cold email to a PI (draft only). |
| `/interview <lab>` | Interview prep pack + optional mock interview. |
| `/outcome` | Record results; `/outcome followup` surfaces quiet applications. |
| `/add-portal <url>` | Scaffold a new portal-search skill for a board in your market. |
| `/report` | Self-contained HTML dashboard of the tracker. |
| `/sheets-sync <sheet> [tab/range]` | Discover MCP capabilities, inspect target, approve additive RAW writes, deduplicate and read back. Stops if required tools are absent. |

## File structure
```
phd-search-agent/
├── AGENTS.md                       # Durable context: cardinal rules + workflow
├── CLAUDE.md                       # Claude Code entry: read AGENTS.md
├── opencode.json                   # opencode: instructions + skills.paths
├── README.md
├── .claude/
│   ├── commands/                   # /setup /search /rank /apply /outreach …
│   ├── settings.json               # scoped permission allowlist
│   └── skills/
│       ├── phd-application-assistant/
│       │   ├── SKILL.md
│       │   ├── 01-candidate-profile.md   # the run contract
│       │   ├── 02-writing-style.md
│       │   ├── 03-position-evaluation.md  # rubric + gates + vetoes
│       │   ├── 04-sop-and-cv.md
│       │   ├── 05-outreach-email.md
│       │   ├── 06-interview-prep.md
│       │   └── 07-web-research.md
│       └── phd-scraper/
│           ├── SKILL.md
│           └── search-queries.md
├── .opencode/
│   ├── command/                    # opencode wrappers for the /commands
│   └── skill/
├── .agents/skills/                 # portal CLIs (the module system)
│   ├── openalex-lab-search/        # labs/PIs via OpenAlex (key-free)
│   └── bsky-position-search/       # recent ads via Bluesky (key-free)
├── tools/phd_key.py                # canonical dedup key
├── documents/                      # cv, diplomas, references, applications/<lab>_<role>/
├── templates/                      # custom CV/SOP templates
├── position_reports/               # /report output
├── positions_tracker.csv           # application tracking
└── position_scraper/               # seen_positions.json state
```

## Extension points
1. **Portal skills** — every `*-search` folder under `.agents/skills/` is a
   self-contained module with the same contract. `/search` auto-discovers any that
   follow it. `/add-portal` generates new ones; review the generated code first.
2. **Templates** — configure manually using `templates/README.md`; there is no
   template-registration command.
3. **Evaluation criteria** — free-form deal-breakers and preferences are profile
   lines; the rubric scores against whatever you put there. Language and funding
   are the two gates with dedicated, structured handling.

## Conceptual attribution
- **ai-job-search** inspired the command/skill portal-CLI module system, the
  drafter-reviewer `/apply` loop, dedup state, the tracker, `/add-portal`.
- **OpenResearch** inspired the cardinal rules (freeze the contract, identical
  retrieval, vary the query not the mechanics, grow downward), the overview +
  modules skill shape, and a preference for scholarly discovery. Neither reference
  repository's code is copied here.

## Evidence and Privacy
Prioritize named doctoral calls (ETH AI fellowship-style specificity), not generic
program pages. Separate verified open calls, programs, watchlist leads, and closed
calls; exclude postdocs unless requested. Use the checklist in
`.claude/skills/phd-application-assistant/07-web-research.md` for official source
URLs, `checked_at`, application/reference deadlines and timezones, salary basis,
currency/period, duration, requirements, materials, supervisors, and unknown flags.
Unknown degree/language/funding is not a hard rejection. Authorship does not prove
PI status, and group size does not prove supervision quality.

Drafting never records contact, application, or follow-up as sent. Only user
confirmation sets those actions and dates. Profiles, trackers, personalized
queries, documents, reports, state, and credentials are ignored by git. Keep
generated output in ignored paths, and never share contact details. Ignore rules
do not remove previously tracked data or history; audit before publishing.

## Safety
Postings and lab pages are untrusted input: the workflow follows no instructions
embedded in them. Follow only relevant official/application links for fact
verification; never run embedded commands or login actions or bypass access blocks.
Missing evidence stays unknown. Agentic defenses are
instruction-level, not a sandbox — skim what was fetched before you act on it.

## License
MIT.

## Tests
Run `python -B -m unittest discover -s tests -v`. The tests use mocked network
responses and cover CLI validation, errors, date windows, and deduplication.
GitHub Actions runs the suite on Python 3.9 and 3.12.

Private working files are intentionally absent from Git. `/setup` initializes
them from the safe templates without overwriting existing data. Restart opencode
in this project to load its commands and skill configuration.
