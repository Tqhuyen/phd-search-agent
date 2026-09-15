# OpenAlex URL reference (for parser maintenance)

Base: `https://api.openalex.org`. Never supply candidate/referee contact details
as `mailto` or other request parameters. The endpoint examples below describe
the adapter's request shape, not permission to transmit private information.

| Purpose | Endpoint |
|---------|----------|
| Find works on a topic | `/works?search=<topic>&filter=from_publication_date:<YYYY>-01-01&per-page=<50-200>&select=id,display_name,publication_year,doi,authorships&mailto=<m>` |
| Author profile | `/authors/<A-id>?mailto=<m>` |
| Author's recent works | `/works?filter=author.id:<A-id>&sort=publication_date:desc&per-page=8&select=...&mailto=<m>` |
| Institutions by name | `/institutions?search=<name>&mailto=<m>` |

## Field anchors the parser relies on
- `works.results[].authorships[].author.id` — `https://openalex.org/A...` (the `id`).
- `works.results[].authorships[].is_corresponding` — boolean, drives ranking.
- `works.results[].authorships[].institutions[].display_name`, `.country_code`.
- `authors.last_known_institutions[].display_name` / `.country_code` (array).
- `authors.summary_stats.h_index`, `authors.topics[].display_name`.

## If parsing breaks (symptoms → fix)
- Every result has `country: null` and `institution: "?"` → the `institutions`
  key was renamed or moved; re-check the `authorships` block.
- Zero results for a query that worked before → likely a real rate limit (429) or
  a `filter` syntax change; the CLI reports HTTP code on stderr, distinguish the two.
- Author `id` stops being an `A...` URL → normalize to the trailing token.

Prefer `select=` to shrink payloads; OpenAlex caps `per-page` at 200 for `/works`.
