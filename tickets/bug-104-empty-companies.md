# Bug: 104 companies have zero data (no values, badges, or scores)

## Where
Main page company cards, API

## What
104 out of 485 companies have no value_snapshots, no badges, and no scores. These show up as blank cards with just a company name and sector — no grade, no highlights, nothing useful. Most are food/consumer staples brands with no ticker.

## Expected
Companies with no data should either:
1. Not be shown on the main page (filter them out), or
2. Show a "No data yet" indicator so users understand why there's no grade

## Steps to Reproduce
1. Go to https://demos.linkedtrust.us/alonovo/
2. Scroll through the company cards
3. Notice many cards with no grade badge, no value highlights, no badges

## Examples
- 365 by Whole Foods, Amy's Kitchen, Annie's Homegrown, Beyond Meat, Bob's Red Mill, Cargill, etc.
- Most are in "Consumer Staples" sector with no ticker

## Notes
These are likely shell companies created during a data import (e.g., cage-free eggs import) where the company was referenced but no claims were actually attached. The header stats show "485 Companies" which overstates the useful data — only 381 have any value data.
