---
name: review-insights
description: When the user wants to understand what users say about an app using ASOScan — overall review sentiment plus the top topics, feature requests, and bugs mentioned, and the raw reviews behind them. Also use when the user mentions "what are users saying", "review sentiment", "top complaints", "what features are people asking for", "what bugs are mentioned", or "summarize my reviews". Works for your app or a tracked competitor.
metadata:
  version: 1.1.0
---

# Review Insights

Turn ASOScan's analyzed review stream into the few things that matter: how users
feel, what they keep asking for, and what's breaking.

## When to use

- "What are users saying about my app?"
- "Top complaints / feature requests / bugs."
- "Summarize the latest reviews." (also for a tracked competitor)

## Calling the ASOScan API

Base `https://asoscan.com/api/public/v1` · header `Authorization: Bearer $ASOSCAN_API_KEY`.
JSON, camelCase. If the key is unset, hand off to **asoscan-setup**.

1. **Find the app** — `GET /apps` → use the `id`. For a rival, it must be a tracked
   competitor first (see **competitor-analysis**).
2. **Insights** — `GET /apps/{id}/reviews/insights` (1 credit) →
   `{ totalAnalyzed, totalPending, sentiment{ positive, neutral, negative,
   averageScore }, topTopics[]{ label, count }, topFeatureRequests[]{ label, count },
   topBugs[]{ label, count } }`.
3. **Raw reviews** (for evidence) — `GET /apps/{id}/reviews?page=1&pageSize=20&rating=&sort=newest`
   (1 credit; pageSize 1–100; `rating=1..5` to isolate detractors/promoters) →
   `{ items[]{ id, author, rating, title, body, version, country, postedAt,
   developerResponse, developerResponseAt }, page, pageSize, totalCount, totalPages }`.

Lead with insights; pull raw reviews only to quote real examples. If `totalPending`
is high, note that more reviews are still being analyzed.

## How to analyze

- **Sentiment** — the positive/neutral/negative split + `averageScore` (pair with
  the rating trajectory from **competitor-analysis** for trend).
- **Themes** — cluster `topTopics`/`topFeatureRequests`/`topBugs` into *love*,
  *friction*, and *requests*, ranked by `count`.
- **Actionability** — for the top 3, name the concrete response: bugs → engineering;
  recurring confusion → onboarding/screenshots; frequent requests → roadmap or
  "What's New".
- **Quote real reviews** verbatim from `body` — never invent or paraphrase into
  something the user didn't write.

## Output template

```
### Review insights — {App}   ·  credits left: {remaining}

**Sentiment:** {positive}/{neutral}/{negative}  (avg {averageScore})  ·  {totalAnalyzed} analyzed

**Love**              | **Friction**            | **Most-requested**
- {topic} ({count})   | - {bug} ({count})       | - {request} ({count})

**Top 3 to act on:** 1) {theme} → {response}  2) …
**Evidence:** > "{verbatim review body}" — {rating}★
```

## Errors, credits & honesty

- `401` → asoscan-setup · `403` no API access · `402` out of credits · `404` not
  tracked · `503` not enabled yet. Each read = 1 credit.
- **Never fabricate reviews.** Replying to reviews builds trust/retention but is
  **not** a search-ranking signal — don't frame replies as an ASO lever.
- Full reference: <https://asoscan.com/api/developers>

## Related

- **competitor-analysis** — rating trajectory + compare sentiment across rivals.
- **metadata-audit** — turn recurring confusion into clearer copy/screenshots.
