---
name: competitor-analysis
description: When the user wants to compare an app against its tracked competitors using ASOScan — keyword overlap and gaps, which store category each competitor uses, category chart rank over time, and rating trajectory — or add a new rival by store URL. Also use when the user mentions "compare my app to competitors", "who am I competing with", "add this competitor", "how do I stack up", "am I gaining or losing vs them", "what category do my competitors use", or "category ranking". For a competitor's full keyword list, see keyword-spy.
metadata:
  version: 1.1.0
---

# Competitor Analysis

Position the app against the rivals ASOScan tracks — where it's ahead, where it's
behind, and the single biggest lever — using real rank, rating, and keyword data.

## When to use

- "Compare my app to my competitors."
- "Add `<store URL>` as a competitor."
- "What category do my competitors use / how's my category rank vs theirs?"

## Calling the ASOScan API

Base `https://asoscan.com/api/public/v1` · header `Authorization: Bearer $ASOSCAN_API_KEY`.
JSON, camelCase. If the key is unset, hand off to **asoscan-setup**.

1. **Find the app** — `GET /apps` → `{ id, name, category, rating, … }` (your own
   `category` is here).
2. **Competitors** — `GET /apps/{id}/competitors?country=` (1 credit) →
   `[{ id, name, developer, iconUrl, rating, ratingCount, category }]`. The
   `category` is each competitor's **primary store category** — this answers "what
   category do my competitors use?" (only the primary is exposed, not Apple's
   secondary).
3. **Add a rival** (if asked) — `POST /apps/{id}/competitors { "storeUrl": "…" }`
   (2 credits, **write** key). Confirm before writing.
4. **Category rank over time** — `GET /apps/{id}/category-rank?country=&days=30`
   (1 credit) → `{ category, country, rankType, currentRank, points[]{ date, rank } }`.
5. **Rating trajectory** — `GET /apps/{id}/rating-history` (1 credit) →
   `[{ rating, totalRatings, date }]`.
6. **Keyword overlap** — pair with **keyword-spy** on each competitor for the gap list.

Category-rank and rating-history are per-app; to compare a competitor, run the same
reads on that competitor's app id (it must be a tracked competitor).

## How to analyze

- **Category placement** — list each competitor's primary `category` next to yours.
  If rivals cluster in a different (or less crowded) category, flag it — category
  choice is an ASO lever.
- **Rank momentum** — climbing or sliding over the window (`points`)?
- **Rating gap** — average `rating` and its direction vs competitors.
- **Keyword gap** (highest-leverage) — relevant terms rivals win that you don't
  target (from keyword-spy), ranked by relevance × volume.
- **Positioning** — one honest line (leader / challenger / niche) + the biggest lever.

## Output template

```
### Competitive position — {App} ({country})   ·  credits left: {remaining}

| App | Category | Category rank (now → {N}d ago) | Rating (now → trend) |
|---|---|---|---|
| {you} | {your category} | … | … |
| {competitor} | {their category} | … | … |

**Keyword gaps** (they rank, you don't — relevant): …
**Biggest lever:** {one specific move}
**Next in ASOScan:** run `keyword-spy` per competitor, then `keyword-opportunities` + `metadata-audit`.
```

## Errors, credits & honesty

- `401` → asoscan-setup · `403` no API access (or read-only key on the add) · `402`
  out of credits · `404` not tracked · `503` not enabled yet.
- Compete on breadth, coverage, and momentum. Clean numbers — don't concede a
  rival's data is "more accurate", and don't claim a tactic guarantees a rank change.
- Full reference: <https://asoscan.com/api/developers>

## Related

- **keyword-spy** — reverse-lookup each competitor's keywords.
- **keyword-opportunities** — turn gaps into a tracked target list.
- **review-insights** — compare what users say (add rivals as competitors first).
