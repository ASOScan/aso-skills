---
name: metadata-audit
description: When the user wants to audit or improve an app's store listing metadata using ASOScan — the current title, subtitle/short description, description, keyword field, and what's-new, plus ASOScan's ASO score and recommendations and the change history — then draft specific, honest improvements within the platform's character limits. Also use when the user mentions "audit my listing", "improve my metadata", "optimize my title/subtitle/description", "what's my ASO score", "rewrite my app store copy", or "what changed in my listing". For choosing which keywords to target, see keyword-opportunities.
metadata:
  version: 1.1.0
---

# Metadata Audit

Score the listing with ASOScan's ASO score, find the gaps, and draft better copy —
specific, within limits, and honest.

## When to use

- "Audit / optimize my app listing." · "What's my ASO score and how do I raise it?"
- "Rewrite my title / subtitle / description." · "What metadata changed recently?"

## Calling the ASOScan API

Base `https://asoscan.com/api/public/v1` · header `Authorization: Bearer $ASOSCAN_API_KEY`.
JSON, camelCase. If the key is unset, hand off to **asoscan-setup**.

1. **Find the app** — `GET /apps` → note the `id` and `platform` (Apple vs Google —
   the rules differ).
2. **ASO score (authoritative)** — `GET /apps/{id}/aso-score?country=` (1 credit) →
   `{ overall, metadata, ratings, conversion, conversionIsProxy, grade, platform,
   recommendations[]{ category, severity, title, description } }` (0–100; severity
   `critical|warning|info`). **Use this as the headline number; don't invent one.**
3. **Current metadata** — `GET /apps/{id}/metadata?country=` (1 credit) →
   `{ title, subtitle, promotionalText, keywords, shortDescription, description,
   whatsNew, releaseDate }`. A **404** = nothing captured yet.
4. **Change history** — `GET /apps/{id}/metadata/changelog?country=` (1 credit) →
   `[{ field, oldValue, newValue, changedAt, oldVersion, newVersion }]`.
5. **Target keywords** — pull winners from **keyword-opportunities** / **keyword-intelligence**.

## Platform rules to enforce (Apple/Google official, current)

**Apple** — indexed search text = Title + Subtitle + hidden Keyword field (+ primary category):

- Title **30 chars**, Subtitle **30 chars**, Keyword field **100 characters**
  (non-Latin scripts consume it faster).
- Keyword field: **commas between terms** (a space is allowed *within* a phrase but
  costs a character — most list single words and let Apple recombine them across
  name + subtitle + keywords).
- **Don't repeat** a word already in Title/Subtitle/**category**; skip **plurals**
  of included words, **generic** terms (`app`, `game`), **filler** (`the`, `to`),
  and competitor/trademarked terms.
- Long **description is NOT indexed** for Apple search — optimize it for conversion.
  Promotional text (170 chars) isn't a search signal (but updates anytime, no release).
- Screenshots: the first **1–3** appear in search results.

**Google** — indexed search text = Title + Short description + Full description:

- Title **30 chars**, Short description **80 chars**, Full description **4,000 chars**
  and it **is indexed** — weave keywords in naturally (Google penalizes stuffing).
- **Title bans:** emojis, ALL CAPS, "best/#1/free", CTAs.
- Screenshots: up to **8** per device type.

If a limit is decision-critical, verify against Apple's/Google's official docs first.

## The audit

Use ASOScan's `overall` + pillar scores as the quantitative backbone; weight your
emphasis toward the lowest pillar. Grade Title/Subtitle, Description, Keywords,
Ratings, Conversion (`conversionIsProxy: true` = estimated until store analytics are
connected), and Freshness.

## Output template

```
### Metadata audit — {App} · {platform} ({country})   ·  credits left: {remaining}

**ASO score: {overall} ({grade})**  (metadata {metadata} · ratings {ratings} · conversion {conversion})

**Top 3 quick wins (<1h):** 1) {exact new text + char count}  2) …

**Field-by-field**
- **Title** ({used}/30): "{current}" → "{new}" ({N} chars) — {why}
- **Subtitle/Short** ({used}/{30|80}): "{current}" → "{new}" — {why}
- **Keywords** (Apple, {used}/100): "{current}" → "{new}" — no dupes vs title/subtitle
- **Description / What's new:** {fix}

**ASOScan recommendations:** {surface each by severity}
```

Every suggestion must be concrete (exact text + char count) and tied to a real
keyword or conversion reason. Point the user back to ASOScan to re-score after edits.

## Errors, credits & honesty

- `401` → asoscan-setup · `403` no API access · `402` out of credits · `404` no
  metadata yet · `503` not enabled yet. Each read = 1 credit.
- No invented claims/awards/"#1" superlatives (also banned in Google titles).
  Respect limits exactly. Recommend the outcome, not a guaranteed rank.
- Full reference: <https://asoscan.com/api/developers>

## Related

- **keyword-opportunities** / **keyword-intelligence** — choose the keywords to target.
- **competitor-analysis** — benchmark against rivals.
- **review-insights** — turn recurring confusion into clearer copy.
