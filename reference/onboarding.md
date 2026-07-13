# Getting your ASOScan API key (first-run setup)

These skills need an ASOScan account and an API key. Run this once. When a skill
finds `ASOSCAN_API_KEY` is empty, walk the user through these steps — don't try
to call the API without a key.

## 1. Create an ASOScan account (or sign in)

Sign up at
**<https://asoscan.com/register?utm_source=github&utm_medium=skill&utm_campaign=aso-skills&utm_content=onboarding>**
and add at least one app (paste your App Store or Google Play URL). The API is
**owner-scoped** — it works on the apps in your account, so you need one tracked
app to do anything useful.

> API access is included on the ASOScan plans listed at
> <https://asoscan.com/pricing?utm_source=github&utm_medium=skill&utm_campaign=aso-skills&utm_content=onboarding>.
> Higher plans get more monthly credits. If a call later returns `403 API access
> not included`, your current plan doesn't include the API yet.

## 2. Create an API key

In the ASOScan dashboard go to **Settings → API access**, click **Create key**,
give it a name, and choose a scope:

- **read** — everything except adding keywords/competitors.
- **read + write** — also lets the skills track keywords and add competitors on
  your behalf. Pick this if you want the write actions.

**Copy the key immediately — it's shown only once.** It looks like
`asosk_live_XXXXXXXX…`.

## 3. Set the key as an environment variable

The skills read the key from `ASOSCAN_API_KEY`. Set it in your shell:

```bash
# macOS / Linux (bash / zsh) — add to ~/.zshrc or ~/.bashrc to persist
export ASOSCAN_API_KEY="asosk_live_XXXXXXXX..."
```

```fish
# fish
set -Ux ASOSCAN_API_KEY "asosk_live_XXXXXXXX..."
```

```powershell
# Windows PowerShell (persist for your user)
setx ASOSCAN_API_KEY "asosk_live_XXXXXXXX..."
# then open a new terminal
```

## 4. Verify

```bash
bash scripts/asoscan-check.sh
```

or directly:

```bash
curl -s "https://asoscan.com/api/public/v1/usage" \
  -H "Authorization: Bearer $ASOSCAN_API_KEY"
```

A JSON body with your credit usage means you're ready. A `401` means the key is
wrong; a `503` means the API isn't enabled for your account yet (contact support
to be enabled). See `error-handling.md` for the full contract.

## Security

Never commit the key, paste it into chat, or print it in logs. If it leaks,
revoke it in **Settings → API access** and create a new one.
