# ASOScan API — Error Handling & Credit Contract

Every skill obeys this contract when a call to the ASOScan API returns a non-2xx
status. Errors are `application/problem+json` (RFC 7807) — read `title`/`detail`
for the human message.

| Status | Meaning | What the skill does |
|---|---|---|
| **200–299** | Success | Use the body. A successful call spent credits — note `X-ApiCredits-Remaining` if it's getting low. |
| **400** | Bad request / failed lookup (e.g. research found nothing) | Explain what failed. **Free** — no credit spent. Suggest a corrected term/params. |
| **401** | Missing or invalid API key | The key is absent, wrong, or revoked. Stop and run the onboarding flow (`onboarding.md`). Do not retry blindly. |
| **403** | `API access not included` (plan without API) **or** `Insufficient scope` (a write call with a read-only key) | For plan: tell the user their ASOScan plan doesn't include API access and point them to upgrade / the plans page. For scope: their key is read-only — they need a key with **write** scope for add-keyword / add-competitor actions. |
| **402** | Monthly credit allowance exhausted | Read `X-ApiCredits-Remaining` (0) and `X-ApiCredits-Reset`. Tell the user credits reset on that date, or they can upgrade for more. **Stop making paid calls.** |
| **429** | Rate limited (per-key bucket: burst 20, ~10/sec) | Back off. Read `RateLimit-Reset` (delta-seconds), wait, then retry once. Batch calls to avoid this. |
| **404** | App / keyword / resource not found, or not in this account | The API is owner-scoped. The app/keyword isn't tracked by this account. **Free.** Confirm the id via `GET /apps`, or tell the user to add the app/competitor in ASOScan first. |
| **503** | `API unavailable` | The ASOScan Public API isn't enabled for this account yet (it's rolling out). Point the user to the onboarding doc / support to get access, then stop. |
| **5xx** | Server error | Transient. Retry once after a short pause; if it persists, report it and stop. |

## Guardrails

- **Never retry a `401`/`403`/`402`/`503` in a loop** — they won't fix themselves
  by retrying. Surface the right message and stop.
- **Budget before you spend.** Before a batch of paid calls (especially research
  at 8 credits), check `GET /usage` (free) if you're unsure how much is left.
- **Cache within the session.** Don't re-run the same research term or re-fetch
  the same keyword list twice in one task.
- **Secrets hygiene.** Never print, echo, or log the value of `ASOSCAN_API_KEY`.
