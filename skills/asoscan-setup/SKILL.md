---
name: asoscan-setup
description: When the user wants to set up or configure ASOScan — get their API access key, set up webhooks (including sending alerts to Slack or Microsoft Teams), or connect their Google Play Console (Android) or App Store Connect (iOS) account. Also use when the user mentions "get my API key", "create an API key", "set up webhooks", "send alerts to Slack", "alerts in Teams", "connect my Play Console", "connect my App Store account", "connect my app", or "how do I hook this up". This skill works with no API key (it helps you get one). It walks you through the ASOScan side and looks up the live third-party steps.
metadata:
  version: 1.1.0
---

# ASOScan Setup & Connect

Guides the user through configuring ASOScan: getting an **API key**, setting up
**webhooks** (incl. Slack / Teams), and **connecting** their Play Console / App
Store Connect accounts. **No API key needed to run this skill** — it's how they get
set up.

> ⚑ **Third-party UIs change — verify live, don't recite from memory.** For any
> step that happens **outside** ASOScan (Slack, Microsoft Teams / Power Automate,
> Google Play Console / Google Cloud, App Store Connect), **look up the current
> official instructions with web search before walking the user through them**, and
> prefer ASOScan's own up-to-date tutorials/docs where linked below. The
> **ASOScan-side** steps in this skill are current; the **external** steps you must
> confirm live each time.
>
> **Gating note:** webhooks and connections may not appear in every account —
> they're rolling out and depend on the plan/feature flags. If the user doesn't see
> a section, tell them the feature may not be enabled for their account yet.

---

## 1. Get your ASOScan API key

Copy this checklist and tick each step:

```
API key setup
- [ ] 1. Create an ASOScan account + add at least one app
- [ ] 2. Settings → API access → New key name → Read-only / Read+write → Create key
- [ ] 3. Copy the key now (asosk_live_… is shown once)
- [ ] 4. export ASOSCAN_API_KEY="asosk_live_…"
- [ ] 5. Verify → expect 200 + your usage
```

**Details:**
1. Sign up at **asoscan.com** and add an app. The API is **owner-scoped** — it works
   on the apps in your account, so you need at least one.
2. **Settings → API access** → type a **New key name** → choose **Read-only** or
   **Read + write** (write lets the skills add keywords & competitors) → **Create
   key**. **Copy it now — `asosk_live_…` is shown only once.**
3. Set it as an environment variable:
   ```bash
   export ASOSCAN_API_KEY="asosk_live_…"     # bash/zsh (add to ~/.zshrc to persist)
   ```
   ```fish
   set -Ux ASOSCAN_API_KEY "asosk_live_…"     # fish
   ```
   ```powershell
   setx ASOSCAN_API_KEY "asosk_live_…"        # Windows PowerShell — open a new terminal after
   ```
4. Verify (either works):
   ```bash
   bash scripts/asoscan-check.sh              # from the skill pack, or:
   curl -s "https://asoscan.com/api/public/v1/usage" -H "Authorization: Bearer $ASOSCAN_API_KEY"
   ```

If the **API access** section isn't visible, the plan may not include API access —
see **asoscan.com/pricing**. Once the key works, come back and use any data skill.

---

## 2. Webhooks — get pushed events (Slack / Teams / your endpoint)

**What they are:** ASOScan can POST an event to a URL you own the moment something
happens — a rank drop, a competitor metadata change, a new opportunity, etc. — so
your team reacts without polling.

**Where:** ASOScan **dashboard → Settings → Webhooks**. Webhooks are **configured in
the dashboard, not via the public API** — a skill can't self-register them; guide
the user, don't `curl` it.

**Steps (ASOScan side) — the form is inline on that page:**
1. Go to **Settings → Webhooks**.
2. **Delivery format** — pick **Signed JSON** (your own HTTPS endpoint), **Slack**,
   or **Microsoft Teams**.
3. **Endpoint URL** — paste the destination (see per-format below).
4. **Events** — tap the event chips to choose which fire. The page shows the live,
   authoritative list (e.g. rank updated, app-sync completed, competitor metadata
   changed, review analyzed, new opportunities).
5. **Label** (optional) — a name like "Ops Slack relay".
6. Click **Add endpoint**, then **Send test** on the new row to confirm it lands.

**Signed JSON endpoint:** each delivery is **HMAC-SHA256 signed** — header
`X-ASOScan-Signature: t=<timestamp>,v1=<hex>` over `"{timestamp}.{rawBody}"`. Verify
it with a stdlib HMAC check (no SDK). The signing secret (`whsec_…`) is shown
**once** when you add the endpoint. For Slack/Teams there's no secret to manage —
the channel URL is the secret.

**Slack:** the user needs a Slack **Incoming Webhook URL** for the target channel,
then paste it into ASOScan with format = Slack.
> **Look up the current Slack steps live** (Slack changes this UI) — search Slack's
> official docs for creating an *Incoming Webhook* / Slack app with an incoming
> webhook. ASOScan also has a walkthrough: **asoscan.com/blog/send-aso-alerts-to-slack**.

**Microsoft Teams:** Teams delivery is built for the **Power Automate "Workflows"**
path (Microsoft is retiring the old Office 365 "Incoming Webhook" connector), so the
user creates a Workflow that "posts to a channel when a webhook request is received"
and pastes that workflow URL into ASOScan with format = Teams.
> **Look up the current Microsoft Teams / Power Automate steps live** — search
> Microsoft's official docs for the *"Post to a channel when a webhook request is
> received"* Workflows template. ASOScan walkthrough:
> **asoscan.com/blog/send-aso-alerts-to-microsoft-teams**.

Honesty: webhooks shorten your reaction time — they are **not** a ranking signal.

---

## 3. Connect your Android app (Google Play Console)

Connecting Play Console lets ASOScan sync your real reviews (and reply to them),
ratings, and listing metadata for that app.

> **You connect from the APP, not from Settings.** Open the app in ASOScan and click
> **Connect** in its header. `Settings → Connections` only *lists* connected accounts
> and lets you *disconnect* — you can't start a connection there.

**Steps (ASOScan side):**
1. Open the app → click **Connect** (in the app header) → choose **Google Play**.
2. Pick a tier:
   - **Reviews & ASO** — reviews & replies, metadata, keyword rank & ASO impact.
     Basic permissions, no security warnings (the quick, widely-available option).
   - **Reviews & ASO + Reports** (recommended) — everything above **plus** your real
     installs, downloads & churn by country; adds read-access to your Play reports
     and one reports-URL paste. (This tier needs a sensitive scope and may be
     limited/gated for now.)
3. Click **Continue with Google** → sign in and approve → you're returned to the app.
   (On the Reports tier you'll also paste your Play reports URL — the wizard has an
   in-flow help dialog showing where to copy it from.)

**Google side:** sign in with a Google account that has the Play Console permission
to **view app information** for that developer account. If the connection returns
**"0 apps"**, that permission is almost always the cause. Google's Play Console /
consent screens change — **look up the current official steps live** if the user
gets stuck.

**Gating:** if you don't see the **Connect** button / the Google Play option, the
connected-accounts feature may not be enabled for the account yet (it's rolling out).

---

## 4. Connect your iOS app (App Store Connect)

Apple has **no OAuth** — you paste an **App Store Connect API key** (a `.p8` team
key). ASOScan's in-app wizard walks you through it and **links Apple's official
guide**, so lean on the wizard.

> **Connect from the APP** (its **Connect** button), same as Android —
> `Settings → Connections` is view/disconnect only.

**Steps:**
1. Open the app → **Connect** (app header) → choose **App Store Connect**. A 4-step
   wizard opens ("App Store Connect Integration").
2. **Permissions** — generate the key with the **Admin** access level: Apple's Team
   Keys take one role each, and Admin is the only one covering metadata + reviews +
   replies + analytics. (An **App Manager** key works for metadata only —
   reviews/replies/analytics won't.) Create it in **App Store Connect → Users and
   Access → Integrations → App Store Connect API**; if you see "Permission is
   required…", click **Request Access** first (usually same-day, up to a few days).
   The wizard links Apple's official guide — use it, and **verify live** if Apple's
   UI has moved.
3. **Paste** into the form: **Issuer ID** (a UUID at the top of that ASC page),
   **Key ID** (the 10-character ID next to the key), and the **.p8 Private Key**
   (downloadable **once** at creation — store it safely).
4. The wizard shows the **apps** the key can see; confirm → **Done**.

Honesty: connected accounts let ASOScan **read your reviews, ratings, and listing
metadata and post review replies** on your behalf — it does **not** publish metadata
to the store for you.

---

## 5. Deferred — ad-account setup (coming when the features are active)

**Do not walk users through these yet.** Guidance for connecting ad accounts will
be added here when the features are generally available:

- **Google Play Ads (Google Ads campaigns, Android)** — connect a Google Ads
  account (per-user OAuth). Currently rolling out / gated.
- **Apple Search Ads (iOS)** — connect an Apple Ads account via a `.p8` key.

When a user asks about these today, tell them ad-campaign management is being rolled
out and isn't available on their account yet, and offer the ASO + keyword skills in
the meantime. (When these ship, add their setup steps here — ASOScan side verified,
Google/Apple side verified live — and flip this section from Deferred to active.)

---

## Related

- **aso-fundamentals** — learn ASO while you get set up (no key needed).
- The **data skills** — once the key is set: keyword-intelligence, keyword-opportunities,
  keyword-spy, competitor-analysis, review-insights, metadata-audit — your real numbers.

Full API reference + try-it console: <https://asoscan.com/api/developers>
