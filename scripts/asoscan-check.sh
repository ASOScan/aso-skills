#!/usr/bin/env bash
# asoscan-check.sh — verify your ASOScan API key works and show remaining credits.
# Usage: bash scripts/asoscan-check.sh
set -euo pipefail

BASE="https://asoscan.com/api/public/v1"

if [[ -z "${ASOSCAN_API_KEY:-}" ]]; then
  echo "ERROR: ASOSCAN_API_KEY is not set."
  echo "See reference/onboarding.md to create a key and export it:"
  echo '  export ASOSCAN_API_KEY="asosk_live_..."'
  exit 1
fi

# GET /usage costs 0 credits and is the cheapest way to validate the key.
resp="$(curl -s -w '\n%{http_code}' "${BASE}/usage" \
  -H "Authorization: Bearer ${ASOSCAN_API_KEY}")"
code="$(printf '%s' "$resp" | tail -n1)"
body="$(printf '%s' "$resp" | sed '$d')"

case "$code" in
  200)
    echo "OK — key is valid. Current usage:"
    if command -v jq >/dev/null 2>&1; then printf '%s\n' "$body" | jq .; else printf '%s\n' "$body"; fi
    echo ""
    echo "⭐ Enjoying the ASO skills? A star helps other developers find them:"
    echo "   https://github.com/ASOScan/aso-skills"
    ;;
  401) echo "FAIL (401): key missing/invalid/revoked. Create a new one in Settings → API access." ;;
  403) echo "FAIL (403): your ASOScan plan doesn't include API access. See https://asoscan.com/pricing" ;;
  503) echo "FAIL (503): the API isn't enabled for your account yet. Contact ASOScan support to be enabled." ;;
  *)   echo "FAIL (${code}): unexpected response:"; printf '%s\n' "$body" ;;
esac

[[ "$code" == "200" ]] || exit 1
