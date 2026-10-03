---
name: asoscan-router
description: When the user wants any App Store Optimization (ASO) task powered by ASOScan, such as keyword volume or difficulty, app rank or rank tracking, keyword opportunities, spying on a competitor's keywords, competitor analysis, review sentiment, review replies, listing text for another language, or a metadata/listing audit. Also use when the user mentions "ASO", "app store optimization", "keyword volume", "keyword difficulty", "my app's rank", "keywords my competitor ranks for", or "audit my app listing". Start here. It checks that the ASOScan tools are connected or an API key is set, then routes to the right ASOScan skill.
metadata:
  version: 1.3.0
---

# ASOScan Router

The entry point for the ASOScan skill pack. ASOScan gives you **real** ASO data:
keyword volume and difficulty, your live rank, opportunities, competitor keywords
and review sentiment, so you optimize from numbers instead of guessing. This
skill (1) checks that ASOScan is reachable, through the connected ASOScan tools
or an API key, then (2) routes to the right specialist.

## Step 0 — General ASO question? No key needed.

If the request is **conceptual / general best-practice** and doesn't need the
user's own data — "how does ASO work", "how do I write a good subtitle", "keyword
strategy", "screenshot best practices", "teach me ASO" — route to
**aso-fundamentals** (no API key).

If the user wants to **get set up** — "get my API key", "set up webhooks / Slack /
Teams alerts", "connect my Play Console / App Store app" — route to **asoscan-setup**
(also no key).

## Step 1: Check how ASOScan is connected (for the data skills)

1. **ASOScan tools are connected** (the ASOScan plugin or connector in ChatGPT or Claude, or any MCP client): you are ready. Do not ask for an API key. `get_usage` (free) shows the API credits left.
2. **No tools, but you can run shell commands**: check `ASOSCAN_API_KEY` (`[[ -n "$ASOSCAN_API_KEY" ]]`). If it is set, optionally validate once with `GET /usage` (free). Never print the key.
3. **Neither**: route to **asoscan-setup**. Don't call the API without a connection or a key.

## Step 2 — Resolve the app

ASOScan only sees the apps in the user's own account. Call `list_my_apps` (or `GET /apps`) and match the user's app by name and store; use its `id` in every later step.

If the user's app is not in the list, offer to add it: ask for its App Store or Google Play link (or bundle or package id) and **which country to track** (never guess a country). Adding uses 2 API credits and one app slot, so ask first. Tool: `add_app`. API: `POST /apps` with `{ "storeUrl": "...", "country": "US" }`. The ASO score and recommendations are ready in about a minute; keyword opportunities start to appear a few minutes later.

If the user names a **rival** that isn't tracked, it must be added as a competitor first (see `competitor-analysis`).

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
| Write or post a reply to a review | **review-insights** |
| Audit / improve the listing (title, subtitle, description, keywords) + ASO score | **metadata-audit** |
| Listing text for another language | **metadata-audit** |
| A full ASO review | run **metadata-audit** first, then pull in **keyword-opportunities** and **competitor-analysis** |

If the intent is ambiguous, ask one clarifying question, then route.

## Calling the ASOScan API (shared conventions)

- **With ASOScan tools connected, skip this section:** use the tools; they need no key and their messages already explain errors.
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
