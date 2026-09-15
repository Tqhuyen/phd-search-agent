---
description: Inspect and safely sync opportunity evidence using available Sheets MCP tools.
agent: build
---

# /sheets-sync

Usage: `/sheets-sync <spreadsheet URL or ID> [tab/range]`.
This is a harness-driven workflow, not a bundled Sheets client or configured MCP.

1. Discover the actual MCP tools available in this session and inspect their
   schemas for spreadsheet metadata, reads, and writes with explicit RAW input.
   If any required capability is absent, stop clearly and name what is missing.
   Never invent tool calls or substitute a direct API/client without user consent.
2. Confirm the target and intended scope. Read metadata, headers, occupied ranges,
   formulas, and existing rows before proposing any write. If inspection fails,
   stop; do not create a replacement or bypass an access block.
3. Prepare only public opportunity evidence from `07-web-research.md`, including
   classification, source URLs, checked_at, and unknown flags. Exclude candidate
   profiles, contact details, credentials, private notes, and application drafts.
4. Deduplicate against both the input and existing rows using official call ID
   plus cycle, or canonical official URL plus title/cycle. Reuse existing keys;
   ambiguous matches require clarification, not a new duplicate row.
5. Show the exact destination, column mapping, and proposed additions for approval.
   Default to append-only in a confirmed empty range. Never clear, replace, or
   overwrite user data, formulas, headers, or formatting. Conflicting updates go
   in a separately approved empty range/tab, leaving originals intact.
6. Re-read the target immediately before writing; if it changed, re-plan. Use the
   discovered tool's explicit `RAW` value input mode, never `USER_ENTERED` or an
   unspecified default. If RAW cannot be guaranteed, stop before writing.
7. Read back the written range, compare every value and key, and check duplicates.
   Report verified counts and range only after readback. On partial failure or
   timeout, inspect before retrying; do not blindly append again or claim upload.
