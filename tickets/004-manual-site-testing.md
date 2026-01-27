# Ticket: Manual Site Testing Checklist

## Status: Ready

## Summary

Go through every feature on the site and verify it works. Check both domains. Report any bugs as new tickets. Do not fix anything — just document what you find.

## Before You Start

- Open the site in a fresh browser window (or incognito)
- Have both domains ready:
  - https://alonovo.cooperation.org
  - https://alonovo.linkedtrust.us
- Test on desktop first, then mobile (or use browser dev tools responsive mode)

---

## Main Page (both domains)

### Page Load
- [ ] Page loads without white screen or errors
- [ ] Header shows "Alonovo" title and tagline
- [ ] Header stats show correct counts (Companies / Values / Sectors) — should be 335+ companies, 10 values
- [ ] Stats are displayed vertically on the left side of the header
- [ ] Company cards grid loads below the filters
- [ ] No console errors (open browser dev tools → Console tab)

### Company Cards
- [ ] Each card shows company name
- [ ] Cards with tickers show the ticker below the name
- [ ] Cards with a computed grade show the colored grade badge (A green, B lime, C yellow, D orange, F red)
- [ ] Cards with value highlights show them (e.g., "ESG Risk: 19.0", "Cruelty-free & Vegan")
- [ ] Cards with badges show them at the bottom (positive green, negative red, neutral gray)
- [ ] Hovering a card shows a subtle lift animation
- [ ] Clicking a card navigates to the company detail page

### Search
- [ ] Typing in search box filters companies in real time
- [ ] Search by company name works (try "Apple")
- [ ] Search by ticker works (try "AAPL")
- [ ] Clearing search shows all companies again
- [ ] Search is case-insensitive

### Sector Filter
- [ ] Dropdown shows "All Sectors" plus every sector
- [ ] Selecting a sector filters to only companies in that sector
- [ ] Company count in header updates to show filtered count
- [ ] Setting back to "All Sectors" shows all companies

### Value Filter
- [ ] Dropdown shows "All Values" plus every value (ESG Score, Cruelty-Free, Corporate Lobbying, etc.)
- [ ] Selecting a value filters to companies that have data for that value
- [ ] Companies without that value are hidden

### Grade Filter
- [ ] Dropdown shows "All Grades" plus A through F
- [ ] Selecting a grade filters to companies with that overall grade
- [ ] Filter uses the computed overall grade (not individual value grades)

### Sort Button
- [ ] Button shows "Grade ↕" initially
- [ ] First click: "Best first ↓" — A grades at top, F at bottom
- [ ] Second click: "Worst first ↑" — F grades at top, A at bottom
- [ ] Third click: "Grade ↕" — back to default order
- [ ] Companies with disqualifying F grades (ICE detention, ICE collaborator) sort to bottom when "Best first"

### Combined Filters
- [ ] Search + sector filter work together
- [ ] Search + grade filter work together
- [ ] All three filters + sort work together
- [ ] Header count updates correctly with combined filters

---

## Company Detail Page

### Pick 5 companies to test (one from each category):
1. A company with many values (e.g., Costco — has lobbying, animal welfare, ESG, stood up)
2. A company with only ESG score (e.g., Adobe)
3. A company with an F grade (e.g., GEO Group or Tesla)
4. A PETA cruelty-free company (e.g., Lush)
5. A company with ICE data (e.g., Dell)

### For each company:
- [ ] Detail page loads without errors
- [ ] Company name and ticker shown at top
- [ ] Sector shown
- [ ] Overall grade badge shown with correct color
- [ ] Badges section shows if company has badges
- [ ] "Value Ratings" section lists each value with its grade
- [ ] Each value card shows the display text (e.g., "ESG Risk: 28.0 (2 sources)")
- [ ] Each value card shows the grade with correct color
- [ ] Claims/sources shown under each value card (if claims exist for that value)
- [ ] Source links are clickable and open in new tab
- [ ] "Back to all companies" link works and returns to main page

### Specific checks:
- [ ] Tesla shows "Ethics of Executives: F" with the USAid explanation
- [ ] GEO Group or CoreCivic shows "ICE detention operator" with F grade
- [ ] Costco shows "Stood Up to Pressure" with positive grade
- [ ] Lush shows "Cruelty-free & Vegan" with A grade
- [ ] A company with 2 ESG sources shows "(2 sources)" in display text

---

## User Menu & Auth

### Logged Out
- [ ] User menu shows "Sign In" option
- [ ] Clicking "Sign In" goes to Google OAuth login page
- [ ] Login page has Alonovo styling (green header, white card)

### Logged In (use Google account)
- [ ] After login, redirects back to the site
- [ ] User menu shows email address
- [ ] User menu has "Profile", "Admin" (if staff), and "Sign Out" options
- [ ] Clicking "Sign Out" goes to logout confirmation page
- [ ] Logout page has Alonovo styling
- [ ] After logout, user menu shows "Sign In" again

---

## Profile Page

- [ ] Accessible from user menu when logged in
- [ ] Shows "Your Profile" heading with email
- [ ] Shows "Value Weights" section with sliders
- [ ] Each non-fixed value has a slider (0-10)
- [ ] Slider labels update as you drag (Don't care, Low, Moderate, Important, Very important, Critical)
- [ ] Fixed values (ICE Contracts, ICE Detention, ICE Collaborator) shown in "Always Counted" section without sliders
- [ ] "Save Weights" button works — shows "Saving..." then "Saved!"
- [ ] Refreshing the page preserves saved weights
- [ ] "Back" link returns to main page

---

## Cross-Domain

- [ ] https://alonovo.cooperation.org loads and works
- [ ] https://alonovo.linkedtrust.us loads and works
- [ ] Both show the same data
- [ ] Company detail pages work on both domains
- [ ] Google login works on both domains (after redirect URLs are configured)

---

## Mobile / Responsive

Test at 375px width (iPhone SE) and 768px width (tablet):

- [ ] Header text is readable, not cut off
- [ ] Header stats hidden on small screens (< 600px)
- [ ] Filter inputs stack vertically on small screens
- [ ] Company cards fill the width on small screens (single column)
- [ ] Company detail page is readable
- [ ] Profile page sliders are usable on touch

---

## Footer

- [ ] Footer shows data source links (OpenSecrets, BBFAW, EggTrack, USASpending)
- [ ] All footer links open in new tabs
- [ ] "Alonovo - Guiding capital toward ethical companies" text shown

---

## Performance

- [ ] Main page loads in under 3 seconds on desktop
- [ ] Filtering/search responds instantly (no lag)
- [ ] Company detail page loads in under 2 seconds
- [ ] No visible layout shift as data loads

---

## Behavioral Tests (the important ones)

These test that the system actually works correctly end-to-end — not just that pages load, but that the logic is right.

### Disqualifying Values Force F Overall

Companies with an F on a disqualifying value (ICE Detention, ICE Collaborator) must show F as their overall grade, regardless of other scores.

- [ ] Find GEO Group — overall grade should be F (disqualified by ICE Detention)
- [ ] Find CoreCivic — overall grade should be F (disqualified by ICE Detention)
- [ ] Find Palantir — overall grade should be F (disqualified by ICE Collaborator)
- [ ] Find Target — overall grade should be F (disqualified by ICE Collaborator)
- [ ] Verify these companies sort to the bottom when using "Best first ↓" sort
- [ ] Verify these companies sort to the top when using "Worst first ↑" sort

### Overall Grade Reflects All Values

The overall grade averages all value scores for a company. Companies with more values should have grades that make sense across all of them.

- [ ] Find Costco — has lobbying, animal welfare, ESG, stood up. Overall grade should reflect the mix (should be B)
- [ ] Find McDonald's — has lobbying, animal welfare, cage-free, ESG. Overall should be worse than a company with only good ESG
- [ ] Find a company with only ESG data (e.g., Adobe) — overall grade should match its ESG grade exactly
- [ ] Find Procter & Gamble — has ESG + "Tests on animals" F. Overall should be pulled down by the F
- [ ] Find Johnson & Johnson — same situation, ESG + animal testing F. Verify overall is worse than ESG alone

### Multiple Data Sources Merge Correctly

Some companies have ESG claims from both Yahoo/Sustainalytics and S&P Global. These get normalized and averaged.

- [ ] Find Apple (AAPL) — detail page should show ESG with "(2 sources)" in display text
- [ ] Find Costco (COST) — check if ESG shows source count
- [ ] On the detail page, verify both source claims appear under the ESG value card
- [ ] Verify the ESG risk number is an average (not just one source)

### Value Filter Shows Correct Companies

- [ ] Filter by "Cruelty-Free (Animal Testing)" — should show ~55 companies (Lush, L'Oréal, P&G, etc.)
- [ ] Filter by "ICE Detention Operations" — should show only GEO Group and CoreCivic
- [ ] Filter by "Stood Up to Pressure" — should show only Costco
- [ ] Filter by "Ethics of Executives" — should show only Tesla
- [ ] Filter by "ESG Score" — should show 250+ companies
- [ ] Companies NOT in a filter should be hidden (e.g., Lush should not appear when filtering by Corporate Lobbying)

### Grade Filter Uses Overall Grade

- [ ] Filter by "F grade" — should include disqualified companies (GEO Group, CoreCivic, Palantir, Target) AND companies whose average score is F
- [ ] Filter by "A grades" — should only show companies whose OVERALL grade is A, not companies that have an A on just one value
- [ ] Verify: a company with ESG grade A but animal testing grade F should NOT appear in "A grades" filter

### Cards Only Show Data That Exists

- [ ] Find a company with only ESG data — card should NOT show lobbying, animal welfare, cruelty-free, or other values it has no data for
- [ ] Find a company with multiple values — card should show highlights for each value it HAS data for
- [ ] No card should show "undefined", "null", "NaN", or blank grades

### Profile Weights (requires login)

**Note: Weights are saved but do NOT currently affect the main page grades. The main page uses a simple average. This section tests that the profile page itself works correctly — saving, loading, and displaying weights. Future work will make weights affect displayed grades.**

- [ ] Log in with Google
- [ ] Go to Profile page
- [ ] Verify all non-fixed values have sliders (ESG Score, Corporate Lobbying, Cage-Free Eggs, Farm Animal Welfare, Cruelty-Free, Stood Up to Pressure, Ethics of Executives)
- [ ] Verify fixed values (ICE Contracts, ICE Detention Operations, ICE Collaborator) appear in "Always Counted" section WITHOUT sliders
- [ ] Set "ESG Score" slider to 0 ("Don't care") — verify label updates
- [ ] Set "Corporate Lobbying" slider to 10 — verify label shows "Critical"
- [ ] Click "Save Weights" — verify "Saved!" confirmation appears
- [ ] Refresh the page — verify your slider positions were preserved
- [ ] Set all sliders to 5, save — verify they all show 5 after refresh

### Auth State Transitions

- [ ] Visit profile page while logged out — should redirect to home page
- [ ] Log in — profile page should now be accessible
- [ ] Log out — profile page should redirect again
- [ ] Log in on alonovo.cooperation.org — check if session works on alonovo.linkedtrust.us (it may not — document whether it does or doesn't, this is expected behavior to note)

### Navigation and Back Buttons

- [ ] From main page, click a company card, then click "Back to all companies" — filters and search should be reset (or preserved, document which)
- [ ] From main page, click a company card, then use browser back button — verify it returns to main page
- [ ] From profile page, click "Back" — returns to main page
- [ ] Deep link: paste `https://alonovo.cooperation.org/company/AAPL` directly — should load Apple detail page
- [ ] Deep link to nonexistent company: `https://alonovo.cooperation.org/company/FAKE` — should show error message, not white screen

### Edge Cases

- [ ] Search for a string that matches nothing (e.g., "zzzzz") — should show empty grid, no errors, header shows "0 Companies"
- [ ] Filter by sector + filter by value where no company matches both — should show empty grid gracefully
- [ ] Very long company name — should not break card layout
- [ ] Company with no ticker (e.g., "S.C. Johnson") — card should still render without ticker, detail page should still work

---

## How to Report Bugs

For each bug found, note:
1. **Where:** Which page and section
2. **What:** What you expected vs what happened
3. **Steps:** How to reproduce
4. **Screenshot:** If visual

Create a new file in `tickets/` for each bug: `tickets/bug-SHORT-DESCRIPTION.md`

## DO NOT

- Do not fix bugs you find — just document them
- Do not change any code or data
- Do not run management commands
- Do not restart any servers
