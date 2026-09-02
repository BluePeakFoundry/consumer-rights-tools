# Practical Refund and Billing Tools

A small static index for Blue Peak Foundry browser-based tools covering consumer refunds, passenger compensation, business billing checks, and freelance quote planning.

## Included public tools

- SEPA Direct Debit Refund Draft: https://bluepeakfoundry.github.io/sepa-direct-debit-refund-draft/
- EU Rail Delay Compensation Calculator: https://bluepeakfoundry.github.io/rail-delay-compensation/
- B2B Refund Leakage Checklist: https://bluepeakfoundry.github.io/b2b-refund-leakage-checklist/
- AP Duplicate Payment SQL Checks: https://bluepeakfoundry.github.io/ap-duplicate-payment-sql-checks/
- Freelance Quote & Late-Payment Calculator: https://bluepeakfoundry.github.io/freelance-quote-late-payment-tool/

## Privacy and scope

This site is static. It does not submit forms, use cookies, or collect personal data. Privacy-friendly aggregate analytics measure visits and non-personal CTA events.

The tools are educational starting points, not legal, accounting, or tax advice. Users should verify current official guidance before sending requests, claims, or business messages.

## Validation

Run:

```bash
python3 validate_index.py
python3 -m json.tool manifest.json >/dev/null
```

Expected local result after building the manifest:

```text
OK tools hub files=7 links=5 money_verified_eur=0 external_actions=0
```
