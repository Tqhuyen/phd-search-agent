---
description: Generate a new portal-search skill for a PhD job board in your market.
agent: build
---

# /add-portal — Add a Job-Portal Skill

Scaffold a search CLI for a PhD/funding portal that this repo does not ship
(EURAXESS, FindAPhD, jobs.ac.uk, AcademicTransfer, scholarshipdb, a national
board, a university system, …).

Usage: `/add-portal <portal-url>`.

## Steps
1. **Investigate.** Fetch the portal and find the search-URL pattern, the result
   structure, and the detail-page structure. Read `robots.txt` and any ToS. If the
   portal is auth-walled or explicitly forbids automated access, **decline** and
   say why.
2. **Scaffold** a skill folder following the shipped pattern exactly:
   ```
   .agents/skills/<name>-search/
   ├── SKILL.md            # frontmatter: name, version, description, context: fork,
   │                       #   enabled: true, allowed-tools
   ├── url-reference.md    # endpoints + parser field anchors
   └── cli/search.py       # search/detail, --format json|table|plain
   ```
   Match the output contract: `{"meta": {...}, "results": [{id,title,company,
   location,date,url,description,...}]}`, errors to stderr with exit 1.
3. **Test-run** a live query against the portal and confirm real results come back.
4. **Register** nothing manually — `/search` auto-discovers any
   `.agents/skills/*/SKILL.md` that follows the contract.
5. If the portal blocks/restricts automated access, stop and document the
   limitation. A personal-use warning is not permission to bypass restrictions.

## Contract rules for a well-built portal skill
- No lifetime scripts (`postinstall` etc.); declare no runtime dependencies.
- Only network calls go to the portal it claims to search.
- Reads/writes stay inside its own folder.
- Ship a `--jobage` recency filter or document that results are filtered client-side.

Review generated code with the user before execution. It is not automatically
trusted or pre-approved, and must not transmit private career/contact data.
