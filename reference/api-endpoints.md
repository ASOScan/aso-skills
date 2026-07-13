# ASOScan API — Endpoint & Response Reference

The complete human reference for the **ASOScan Public Data API**: base URL, auth,
safe-call patterns, every endpoint, and exact response shapes. Each skill inlines
the compact subset it needs (skills are self-contained); this file is the full
reference. Interactive try-it console: <https://asoscan.com/api/developers>.

## Contents

- Base URL & auth
- How to call safely
- Scope of the data (owner-scoped)
- Credit awareness
- Endpoints (table)
- Response shapes (exact camelCase fields)
- Response headers to watch
- Human-facing docs

---

## Base URL & auth

- **Base URL:** `https://asoscan.com/api/public/v1`
- **Auth header:** `Authorization: Bearer $ASOSCAN_API_KEY`
- **Key format:** `asosk_live_…` (created in the ASOScan dashboard — see `onboarding.md`)
- **Wire format:** JSON, **camelCase** field names, enums as strings
  (e.g. `"platform": "iOS"`). Errors are RFC 7807 `application/problem+json`.

---

## How to call safely (copy these patterns)

Read the key from the `ASOSCAN_API_KEY` environment variable — **never hardcode
or echo it**. If it's empty, stop and run `onboarding.md`.

```bash
BASE="https://asoscan.com/api/public/v1"
AUTH="Authorization: Bearer $ASOSCAN_API_KEY"

# GET — capture BOTH the body and the HTTP status so you can honor error-handling.md:
resp="$(curl -s -w '\n%{http_code}' -H "$AUTH" "$BASE/apps")"
code="$(printf '%s' "$resp" | tail -n1)"
body="$(printf '%s' "$resp" | sed '$d')"
# → branch on $code per error-handling.md, then parse $body (JSON).

# GET with params that may contain spaces (e.g. a multi-word term) — URL-encode them:
curl -s -G -H "$AUTH" "$BASE/apps/$APP_ID/keywords/research" \
  --data-urlencode "term=habit tracker" \
  --data-urlencode "country=US"

# POST JSON (write-scoped key required):
curl -s -X POST -H "$AUTH" -H "Content-Type: application/json" \
  "$BASE/apps/$APP_ID/keywords" \
  -d '{"terms":["habit tracker","daily planner"],"country":"US"}'
```

Always URL-encode multi-word query values with `-G --data-urlencode`. Always
check the status code before trusting the body.

---

## Scope of the data — READ THIS FIRST

The API is **owner-scoped**: it only returns data for apps that live in the
authenticated user's ASOScan account. `GET /apps` lists exactly those apps; use
an app's `id` (a GUID) in every `/apps/{id}/…` path.

- To analyze a **rival/competitor** app, first add it as a competitor with
  `POST /apps/{id}/competitors` (write scope), then read its data.
- You **cannot** query an arbitrary app the account doesn't track — a foreign or
  unknown id returns **404**.

---

## Credit awareness

Every **successful (2xx)** call spends credits. Failed calls (`404`, validation
errors, a failed research lookup that returns `400`) are **free**. `GET /usage`
is free. Read `X-ApiCredits-Remaining` and stay frugal. **Live research is 8
credits** — cache the result for a term within the session; never repeat the same
`term`+`country`.

---

## Endpoints

| Resource | Method · Path | Cost |
|---|---|---|
| Apps | `GET /apps` | 1 |
| Apps | `GET /apps/{id}` | 1 |
| Keywords | `GET /apps/{id}/keywords?country=&rankWindow=7d` | 1 |
| Keywords | `GET /apps/{id}/keywords/{keywordId}/history?days=30` | 1 |
| Keywords | `GET /apps/{id}/keywords/{keywordId}/metrics-history?days=180` | 1 |
| Keywords | `GET /apps/{id}/keywords/research?term=&country=US` | **8** |
| Keywords (write) | `POST /apps/{id}/keywords` — `{ "terms": [...], "country": "US" }` | 2 |
| Opportunities | `GET /apps/{id}/opportunities?country=&limit=50` | **2** |
| Keyword Spy | `GET /apps/{id}/keyword-spy?country=` | **2** |
| Competitors | `GET /apps/{id}/competitors?country=` | 1 |
| Competitors (write) | `POST /apps/{id}/competitors` — `{ "storeUrl": "…" }` | 2 |
| ASO Score | `GET /apps/{id}/aso-score?country=` | 1 |
| Reviews | `GET /apps/{id}/reviews?page=1&pageSize=20&rating=&sort=newest` | 1 |
| Reviews | `GET /apps/{id}/reviews/insights` | 1 |
| Ranks | `GET /apps/{id}/category-rank?country=&days=30` | 1 |
| Ranks | `GET /apps/{id}/rating-history` | 1 |
| Metadata | `GET /apps/{id}/metadata?country=` | 1 |
| Metadata | `GET /apps/{id}/metadata/changelog?country=` | 1 |
| Usage | `GET /usage` | 0 |

**Query parameter details** (defaults + clamps enforced server-side):

- `country` — ISO code (`US`, `DE`, …). Omit to use the app's primary country.
- `rankWindow` — `1d` \| `7d` (default) \| `30d`; drives the keyword `rankDelta`.
- `limit` (opportunities) — default 50, clamped **1–200**.
- `days` — history: default 30, clamp **1–365**; metrics-history: default 180,
  clamp **1–730**; category-rank: default 30, clamp **1–365**.
- Reviews: `page` (default 1), `pageSize` (default 20, clamp **1–100**),
  `rating` (optional `1`–`5`), `sort` (default `newest`).
- Research: `term` is **required** (400 if missing); `country` defaults to `US`.

---

## Response shapes (exact field names — camelCase)

Parse exactly these fields. Nullable fields can be `null` — handle that.

**`GET /apps` → array of app**
`id, platform, storeId, storeUrl, name, developer?, iconUrl?, rating?, ratingCount?, version?, category?`

**`GET /apps/{id}/keywords` → array of keyword.** The `id` here is the
`{keywordId}` you pass to the history endpoints.
`id, term, country, rank?, rankDelta?, rankCheckedAt?, volume?, difficulty?, isFavorite, organicDownloads?, volumeHistory?[]`
- `rank` = current position (lower is better; `null` = not currently ranked).
- `rankDelta` = change over `rankWindow`; **positive = improved** (moved toward #1).
- `difficulty` is a number (may be fractional).

```json
[
  { "id": "a1b2…", "term": "habit tracker", "country": "US",
    "rank": 6, "rankDelta": 4, "volume": 38000, "difficulty": 41,
    "isFavorite": true, "organicDownloads": 5200 }
]
```

**`GET /apps/{id}/keywords/{keywordId}/history` → array**
`rank?, recordedAt`

**`GET /apps/{id}/keywords/{keywordId}/metrics-history` → object**
`term, country, volume[]{ at, value }, difficulty[]{ at, value }`

**`GET /apps/{id}/keywords/research` → object**
`term, platform, country, volume, difficulty, competingAppsCount, topApps[]{ storeId, name, developer?, iconUrl?, rating?, ratingCount?, storeUrl? }`

**`GET /apps/{id}/opportunities` → array.** NOTE: there is **no** "source" field
— use `opportunityScore` and `competitorRanks`.
`term, volume?, difficulty?, opportunityScore?, competitorRanks[]{ name, rank?, isYou }`
- `competitorRanks` shows who ranks for the term; the entry with `isYou: true` is
  the owner's app (`rank: null` there = you don't rank yet — the opportunity).

```json
[
  { "term": "routine app", "volume": 12000, "difficulty": 33, "opportunityScore": 82,
    "competitorRanks": [
      { "name": "Your App", "rank": null, "isYou": true },
      { "name": "Rival A", "rank": 4, "isYou": false }
    ] }
]
```

**`GET /apps/{id}/keyword-spy` → object**
`appName, iconUrl?, platform, country, totalKeywordsFound, communityPoolSize, discoveryStatus, keywords[]{ term, rank, volume?, difficulty?, origin, isTracked }`
- `origin` = `"community"` \| `"discovered"`. `isTracked` = already in your tracked set.
- `discoveryStatus` = `"cached"` \| `"none"`. The public API does NOT trigger a new
  discovery run — results are the community rank pool + any already-cached
  discovery. A just-added competitor may be sparse until discovery has cached data.
- **Owner-scoped:** `{id}` must be your own app or a **tracked competitor** — a
  foreign app id returns 404. Add a rival first via `POST …/competitors` (storeUrl).

**`GET /apps/{id}/competitors` → array of competitor**
`id, name, developer?, iconUrl?, rating?, ratingCount?, category?`

**`GET /apps/{id}/aso-score` → object**
`overall, metadata, ratings, conversion, conversionIsProxy, grade, platform, recommendations[]{ category, severity, title, description }`
- `overall` and the pillars are 0–100; `grade` is a letter; `severity` is
  `critical` \| `warning` \| `info`.

**`GET /apps/{id}/reviews` → object**
`items[]{ id, author?, rating, title?, body?, version?, country?, postedAt?, developerResponse?, developerResponseAt? }, page, pageSize, totalCount, totalPages`

**`GET /apps/{id}/reviews/insights` → object**
`totalAnalyzed, totalPending, sentiment{ positive, neutral, negative, averageScore }, topTopics[]{ label, count }, topFeatureRequests[]{ label, count }, topBugs[]{ label, count }`

**`GET /apps/{id}/category-rank` → object**
`category, country, rankType, currentRank?, points[]{ date, rank? }`

**`GET /apps/{id}/rating-history` → array**
`rating, totalRatings?, date`

**`GET /apps/{id}/metadata` → object** (404 if none captured yet)
`snapshotDate, locale, title?, subtitle?, promotionalText?, keywords?, shortDescription?, description?, whatsNew?, releaseDate?`

**`GET /apps/{id}/metadata/changelog` → array**
`field, oldValue?, newValue?, changedAt, oldVersion?, newVersion?, country?`

**`POST /apps/{id}/keywords` → object**
`added[]{ …keyword shape… }, skipped[]{ term, reason }`

**`POST /apps/{id}/competitors` → competitor object** (same shape as the list).

**`GET /usage` → object** — current-month credits used/remaining + per-endpoint
breakdown (free, 0 credits).

---

## Response headers to watch

- Credits: `X-ApiCredits-Limit` (or `unlimited`), `X-ApiCredits-Remaining`,
  `X-ApiCredits-Used`, `X-ApiCredits-Reset` (ISO-8601, start of next month UTC).
- Rate limit (IETF): `RateLimit-Limit`, `RateLimit-Remaining`, `RateLimit-Reset`
  (delta-seconds). Per-key bucket: burst 20, refill ~10/sec.

To see headers, add `-D -` (dump headers) to a `curl` call, or read them from a
`-i` response.

---

## Human-facing docs (for the user, not for calling)

- Interactive API reference (try-it console): <https://asoscan.com/api/developers>
- OpenAPI spec: <https://asoscan.com/api/public/v1/openapi.json>
- Postman collection: <https://asoscan.com/asoscan-public-api.postman_collection.json>
