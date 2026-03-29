# Bug: Duplicate/inconsistent sector names

## Where
Sector filter dropdown on main page, API data

## What
Several sector names are inconsistent duplicates:
- **"Restaurant" (2 companies)** vs **"Restaurants" (5 companies)** — McDonald's and Starbucks are in "Restaurant", others in "Restaurants"
- **"Health Care" (28 companies)** vs **"Healthcare" (2 companies)** — Sanofi and UnitedHealth Group are in "Healthcare", the rest in "Health Care"

## Expected
Each sector should have one consistent name. The filter dropdown should not show near-duplicates.

## Steps to Reproduce
1. Go to https://demos.linkedtrust.us/alonovo/
2. Open the Sector filter dropdown
3. See both "Restaurant" and "Restaurants", and both "Health Care" and "Healthcare"

## Companies affected
- Healthcare: Sanofi (SNY), UnitedHealth Group (UNH) — should be "Health Care"
- Restaurant: McDonald's (MCD), Starbucks (SBUX) — should be "Restaurants"
