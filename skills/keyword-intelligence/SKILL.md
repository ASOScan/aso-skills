---
name: keyword-intelligence
description: When the user wants to analyze keyword performance for an app tracked in ASOScan — real search volume, difficulty, the app's current rank and rank movement, daily rank history, weekly volume/difficulty trends, or live on-demand research for a new term. Also use when the user mentions "how hard is this keyword", "search volume for X", "where do I rank for Y", "is my rank going up or down", "show my rank history", or "research this keyword". For discovering new keywords to target, see keyword-opportunities.
metadata:
  version: 1.2.0
---

# Keyword Intelligence

Turn ASOScan's real keyword data into a clear read on which keywords are worth the
effort and how the app is trending — so you prioritize from numbers, not hunches.

## When to use

- "What's the volume/difficulty of `<keyword>`?"
- "Where does my app rank for `<keyword>`? Is it moving?"
- "Show me my rank history / volume trend for `<keyword>`."
- "Research `<a keyword I don't track yet>`."

## Calling the ASOScan API

Base `https://asoscan.com/api/public/v1` · header `Authorization: Bearer $ASOSCAN_API_KEY`
(read from the env var; never hardcode/echo it). JSON, camelCase. Capture the
status to handle errors (see the bottom). If the key is unset, hand off to
**asoscan-setup**.

1. **Find the app** — `GET /apps` → each `{ id, name, platform, storeId, category }`.
   Use the `id`.
2. **Tracked keywords + current state** — `GET /apps/{id}/keywords?country=&rankWindow=7d`
   (1 credit). Each row: `{ id, term, country, rank, rankDelta, rankCheckedAt,
   volume, difficulty, isFavorite }`. `rankWindow` = `1d|7d|30d`. Fetch the list
   once and filter locally. The row's `id` is the `{keywordId}` for history calls.
3. **Rank history** — `GET /apps/{id}/keywords/{keywordId}/history?days=30`
   (1 credit) → `[{ rank, recordedAt }]` (days 1–365).
4. **Volume/difficulty trend** — `GET /apps/{id}/keywords/{keywordId}/metrics-history?days=180`
   (1 credit) → `{ term, country, volume[]{ at, value }, difficulty[]{ at, value } }`.
5. **Live research** (a term not tracked yet) — `GET /apps/{id}/keywords/research?term=…&country=US`
   (**8 credits — cache it**; URL-encode the term) → `{ term, platform, country,
   volume, difficulty, competingAppsCount, topApps[] }`. A failed lookup is 400 (free).
6. **Find easier alternatives when a term is hard.** If a researched term is high-volume but
   **high-difficulty** (🟠 Stretch), research 2–3 long-tail variants of it — add a qualifier such as
   `<term> games`, `<term> app`, `color <term>`, `best <term>` — via the research endpoint (step 5),
   and surface any that keep useful volume at **lower difficulty** (a 🟢 Win-now alternative). Cache
   each. This is the highest-leverage move for a Stretch term: point the user at a keyword they can
   realistically win instead of one they can't.

## How to read the numbers

- **volume** — relative search demand (higher = more searches); compare within one market.
- **difficulty** — how hard to rank (higher = harder). The prize is
  **high-volume, low-difficulty** terms the app can realistically win.
- **rank + rankDelta** — position (`null` = not ranked) and its change over the
  window. **Positive `rankDelta` = improvement** (toward #1).

| Tier | Signal | Action |
|---|---|---|
| 🟢 Win now | High volume · low difficulty · not ranking well yet | Prioritize in metadata |
| 🟡 Defend | High volume · already top ~10 | Hold; watch rankDelta |
| 🟠 Stretch | High volume · high difficulty | Long game; needs authority |
| ⚪ Low leverage | Low volume | Only if highly relevant |

## Output template

```
### Keyword intelligence — {App} ({country})   ·  credits left: {X-ApiCredits-Remaining}

| Keyword | Volume | Difficulty | Rank | Δ ({window}) | Read |
|---|---|---|---|---|---|
| … | … | … | … | ▲/▼ … | Win now / Defend / … |

**Trends:** {keyword}: rank {from → to} over {N}d; volume {trend}; difficulty {trend}.
**What I'd do:** 1) {specific action tied to a keyword}  2) …
```

Then nudge the next step in ASOScan: track the winners via **keyword-opportunities**
and place them with **metadata-audit**.

## Errors, credits & honesty

- `401` → asoscan-setup · `403` → plan without API access · `402` out of credits
  (read `X-ApiCredits-Remaining`/`-Reset`) · `429` back off · `404` not tracked ·
  `503` API not enabled yet. Successful calls spend credits; failed calls are free.
- Present volume/difficulty as clean numbers — don't label them "estimated" or
  guess their source. Never promise a specific rank.
- Full reference: <https://asoscan.com/api/developers>

## Related

- **keyword-opportunities** — discover *new* keywords worth targeting.
- **keyword-spy** — every keyword an app already ranks for.
- **metadata-audit** — put the winning keywords into the listing.
