# EU Consumer Rights Tools

A small static index for Blue Peak Foundry browser-based consumer rights tools.

## Included public tools

- SEPA Direct Debit Refund Draft: https://bluepeakfoundry.github.io/sepa-direct-debit-refund-draft/
- EU Rail Delay Compensation Calculator: https://bluepeakfoundry.github.io/rail-delay-compensation/
- B2B Refund Leakage Checklist: https://bluepeakfoundry.github.io/b2b-refund-leakage-checklist/

## Privacy and scope

This site is static. It does not collect data, submit forms, use analytics, or load runtime resources from remote domains. Links point to existing public tools and official-style explanatory pages.

The tools are educational starting points, not legal advice. Users should verify current official guidance before sending requests or claims.

## Validation

Run:

```bash
python3 validate_index.py
python3 -m json.tool manifest.json >/dev/null
```

Expected local result after building the manifest:

```text
OK consumer rights index files=7 money_verified_eur=0 external_actions=0
```
