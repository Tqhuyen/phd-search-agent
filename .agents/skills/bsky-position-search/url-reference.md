# Bluesky URL reference (for parser maintenance)

Base: `https://api.bsky.app/xrpc` (public AppView). Key-free for reads.

| Purpose | Endpoint |
|---------|----------|
| Search posts | `/app.bsky.feed.searchPosts?q=<query>&limit=<1-100>&sort=latest` |
| Read a thread | `/app.bsky.feed.getPostThread?uri=<at-uri>` |
| Resolve a handle | `/com.atproto.identity.resolveHandle?handle=<handle>` |

## Field anchors the parser relies on
- `posts[].uri` — the `at://did:.../app.bsky.feed.post/<rkey>`; stored as `id`.
- `posts[].author.handle` — used to build the `bsky.app/profile/...` link.
- `posts[].record.text`, `posts[].record.createdAt` — the post body and date.
- `posts[].indexedAt` — fallback date when `createdAt` is absent.
- `thread.post.embed.external.uri` — an attached link (often the actual job ad).
- `thread.post.record.text`, `.author.handle` for `detail`.

## Link form
`https://bsky.app/profile/<handle>/post/<rkey>` where `<rkey>` is the last
path segment of the `at://` URI.

## If parsing breaks (symptoms → fix)
- `indexedAt` present but `createdAt` missing → the record shape changed; the CLI
  already falls back, but check `record` nesting.
- Handle resolution fails → the post may be from a taken-down account; report it,
  do not retry in a loop.
- Search returns unrelated posts → the AppView search index lagged; re-run once,
  then move on.

A 429 is a rate limit, not breakage. Back off; do not treat it as "no results".
