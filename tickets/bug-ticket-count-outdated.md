# Bug: Testing ticket references outdated counts

## Where
Ticket 004 (manual-site-testing.md)

## What
The testing checklist says to verify "335+ companies, 10 values" but the actual data now has:
- **485 companies** (not 335)
- **17 values** (not 10)

New values added since the ticket was written: lgbtq_equality, exec_pay_ratio, forced_labor, ghg_emissions, gun_safety, tax_fairness, tobacco_products.

## Expected
The testing checklist should reflect current data.

## Impact
Low — this is a documentation issue in the ticket, not a site bug. But testers following the checklist might think something is wrong when counts don't match.
