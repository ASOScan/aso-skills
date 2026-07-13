---
name: asoscan-router
description: When the user wants any App Store Optimization (ASO) task powered by ASOScan — keyword volume or difficulty, app rank or rank tracking, keyword opportunities, spying on a competitor's keywords, competitor analysis, review sentiment, or a metadata/listing audit. Also use when the user mentions "ASO", "app store optimization", "keyword volume", "keyword difficulty", "my app's rank", "keywords my competitor ranks for", or "audit my app listing". Start here — it makes sure the ASOScan API key is set, then routes to the right ASOScan skill.
metadata:
  version: 1.1.0
---

# ASOScan Router

The entry point for the ASOScan skill pack. ASOScan gives you **real** ASO data —
keyword volume & difficulty, your live rank, opportunities, competitor keywords,
and review sentiment — so you optimize from numbers instead of guessing. This
skill (1) makes sure the API key is set, then (2) routes to the right specialist.

## Step 0 — General ASO question? No key needed.

If the request is **conceptual / general best-practice** and doesn't need the
user's own data — "how does ASO work", "how do I write a good subtitle", "keyword
strategy", "screenshot best practices", "teach me ASO" — route to
**aso-fundamentals** (no API key).

If the user wants to **get set up** — "get my API key", "set up webhooks / Slack /
Teams alerts", "connect my Play Console / App Store app" — route to **asoscan-setup**
(also no key).

## Step 1 — Ensure the API key (for the data skills)

For anything that needs the user's real data, check the `ASOSCAN_API_KEY`
environment variable (`[[ -n "$ASOSCAN_API_KEY" ]]`).

- **If it's empty:** route to **asoscan-setup**, which walks the user through
  creating an ASOScan account, adding an app, and minting a key — then they
  `export ASOSCAN_API_KEY=…` and come back. Don't call the API without a key.
- **If it's set:** optionally validate once with `GET /usage` (free), then continue.

Never print or echo the key.

## Step 2 — Resolve the app

The ASOScan API is **owner-scoped** — it only sees apps in the user's ASOScan
account. Call `GET /apps` and match the user's app by name/store; use its `id` (a
GUID) in every `/apps/{id}/…` path. If the user names a **rival** that isn't
tracked, note it must be added as a competitor first (see `competitor-analysis`).

## Step 3 — Route to the right skill

| The user wants… | Route to |
|---|---|
| General ASO advice / best practices / "how does X work" (no data) | **aso-fundamentals** (no key) |
| Get an API key · webhooks / Slack / Teams alerts · connect Play Console or App Store | **asoscan-setup** (no key) |
| Keyword volume, difficulty, their rank, rank history, or research on a term | **keyword-intelligence** |
| "What keywords should I target?" / gap-scored suggestions | **keyword-opportunities** |
| "What keywords does *this app* rank for?" (reverse lookup) | **keyword-spy** |
| Compare against competitors / add a rival / category rank | **competitor-analysis** |
| What users say — sentiment, complaints, feature requests | **review-insights** |
| Audit / improve the listing (title, subtitle, description, keywords) + ASO score | **metadata-audit** |
| A full ASO review | run **metadata-audit** first, then pull in **keyword-opportunities** and **competitor-analysis** |

If the intent is ambiguous, ask one clarifying question, then route.

## Calling the ASOScan API (shared conventions)

- **Base:** `https://asoscan.com/api/public/v1` · **Auth:** header
  `Authorization: Bearer $ASOSCAN_API_KEY`. JSON, camelCase fields.
- **Safe call** — capture the status so you can handle errors:
  ```bash
  BASE="https://asoscan.com/api/public/v1"; AUTH="Authorization: Bearer $ASOSCAN_API_KEY"
  resp="$(curl -s -w '\n%{http_code}' -H "$AUTH" "$BASE/apps")"
  code="$(printf '%s' "$resp" | tail -n1)"; body="$(printf '%s' "$resp" | sed '$d')"
  ```
  URL-encode multi-word query values: `-G --data-urlencode "term=habit tracker"`.
- **Errors:** `401` missing/invalid key → asoscan-setup · `403` no API access →
  upgrade, or read-only key on a write → needs a write key · `402` out of credits
  (read `X-ApiCredits-Remaining` / `-Reset`) · `429` back off · `404` not
  owned/tracked · `503` API not enabled for this account yet.
- **Credits:** successful (2xx) calls spend credits; failed calls are free; live
  research is the expensive one (8) — cache it. Watch `X-ApiCredits-Remaining`.
- **Full reference + try-it console:** <https://asoscan.com/api/developers>

## Honesty

Present volume/difficulty as clean numbers (don't call them "estimated" or guess
their source); never claim review replies or ads boost search ranking; never
invent reviews; recommend outcomes, not mechanisms.
