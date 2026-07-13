# Evals — manual test scenarios

Per [Anthropic's skill best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices),
each scenario describes a query + the behavior a correct run should show. There's no
built-in runner — these are for **manual review**: load the pack into your agent,
run the `query`, and check every `expected_behavior` holds.

**Shape:** `{ skills, query, setup?, expected_behavior[] }` (`setup` lists
prerequisites, e.g. an API key + a tracked app).

## How to run
1. Install the pack (or copy `skills/` into your agent's skills dir).
2. For `setup` that needs data: `export ASOSCAN_API_KEY="asosk_live_…"` and have at
   least one app tracked in your ASOScan account.
3. Run each scenario's `query` in a fresh session and verify the expected behaviors.
4. Test across Claude Haiku / Sonnet / Opus if you'll use more than one.

## Scenarios
- `aso-fundamentals.json` — no key needed
- `onboarding-first-run.json` — no key (first-run guidance)
- `keyword-intelligence.json` — needs key + tracked app
- `keyword-opportunities.json` — needs key + tracked app
- `metadata-audit.json` — needs key + tracked app
