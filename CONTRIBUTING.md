# Contributing to ASOScan ASO Skills

Thanks for helping make App Store Optimization easier from inside AI coding agents. This repo is a
pack of [Agent Skills](https://github.com/ASOScan/aso-skills) (`SKILL.md` files) that run in Claude
Code, Cursor, and any Agent-Skills client. Contributions of all sizes are welcome.

## Ways to contribute

- **New skill** — a new ASO capability (e.g. localization coverage, A/B-test framing, seasonality).
- **Improve a skill** — a sharper framework, a better output template, clearer trigger phrases.
- **More markets** — add locale-specific tips/examples to `aso-fundamentals`.
- **Better examples** — real prompts that show a skill off, in the README or in `evals/`.
- **Docs** — fix or clarify the `reference/` API notes or the onboarding guide.
- **Report a bug** — a skill that misfires, a wrong limit, a broken endpoint.

Not sure where to start? Look for issues labelled
[`good first issue`](https://github.com/ASOScan/aso-skills/labels/good%20first%20issue).

## Skill anatomy

Every skill is a folder under `skills/<name>/` with a `SKILL.md`:

```
---
name: keyword-intelligence          # lowercase-hyphens, <=64 chars, no "claude"/"anthropic"
description: >-                      # third person; what it does + WHEN to use it + trigger phrases; <=1024 chars
  Researches keyword volume, difficulty, rank and rank history for an app...
metadata:
  version: 1.1.0
---

# Keyword Intelligence

Framework -> the exact API call(s) -> scoring rubric -> output template.
```

Rules that keep the pack consistent:

1. **Self-contained.** A skill inlines the exact API calls it needs (base URL, its endpoints,
   response fields, error + credit handling) and reads the key from `ASOSCAN_API_KEY`. No `../`
   links to other skills — each one installs and runs on its own. (The `reference/` folder is the
   human API reference, not a runtime dependency.)
2. **The `description` earns the skill.** It's how the agent decides whether to use it — write it in
   the third person with concrete trigger phrases, and say when *not* to use it.
3. **Keep `SKILL.md` focused** (aim for under ~500 lines). Put long tables in `reference/`.

## The honesty rules (non-negotiable)

ASO is a small niche where one wrong or over-claimed fact is reputational poison. Every skill must:

- Present keyword **volume/difficulty as clean numbers** — never label them "estimated" or reveal a source.
- **Never claim** review replies or ads boost search ranking (they don't).
- **Never fabricate** reviews, testimonials, ratings, or numbers.
- **Verify facts against official sources** — Apple App Store / Google Play docs first — before stating
  a character/byte limit, policy, or ranking behavior. Don't state an ASO fact from memory.
- Sell the **outcome**, not a mechanism.

A PR that breaks these will be asked to change before it can be merged.

## Test your change

- `bash scripts/asoscan-check.sh` — validates a key and that the API is reachable.
- The [`evals/`](evals/) folder has manual scenarios; add one when you add a skill.
- Install locally and try it: `npx skills add <your-fork>/aso-skills --skill <name>`, or copy
  `skills/<name>/` into `.claude/skills/`.

## Pull requests

1. Fork + branch (`skill/<name>` or `fix/<thing>`).
2. Keep the change scoped; update the README **Skills** table if you add a skill.
3. Open a PR describing what it does, plus a real prompt that exercises it.

Questions about your ASOScan **account** (keys, billing, your data) belong at
[asoscan.com](https://asoscan.com) support — not as an issue here.
