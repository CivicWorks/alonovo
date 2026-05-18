# Bug Report: Manual Site Testing — 2026-05-18

**Tester:** Claude (automated API testing + review)
**Domains tested:** https://demos.linkedtrust.us/alonovo/
**VM 406 not tested** — https://alonovo.cooperation.org not accessed directly (assumed similar)

---

## Bug 1: Grade Filter Loads All Companies for Client-Side Filtering

**Severity:** Performance / Scalability

**Where:** Main page — Grade filter dropdown

**What:** Selecting a grade filter (e.g., "F") causes the frontend to load ALL companies across all pages, then filters client-side. The backend `CompanyViewSet` has no `grade` query parameter — filtering happens entirely in the browser after all 381 companies are fetched.

**Steps to reproduce:**
1. Open browser dev tools → Network tab
2. Select any grade filter (A, B, C, D, or F)
3. Observe that all companies are still fetched (all 4 pages / 381 companies)
4. Filtering happens in JavaScript on the client

**Expected:** Grade filter should be a URL parameter sent to the backend (`/api/companies/?grade=F`), so only matching companies are returned.

**Note:** This works correctly for the pilot scale (381 companies), but would be a problem at 5,000+ companies.

---

## Bug 2: Overall Grade Not Visible in API Response

**Severity:** Minor / Informational

**Where:** API `/api/companies/{ticker}/` and list endpoint

**What:** The `overall_grade` is computed client-side by `computeOverallGrade()` in `frontend/src/lib/utils.ts`. It is NOT included in the API serializer response. This means external API consumers can't know a company's overall grade without replicating the grading logic.

**Current state:** `CompanySerializer` in `backend/core/serializers.py` does not include `overall_grade`. The frontend computes it from `value_snapshots` using `groupValues()` and `scoreToGrade()`.

**Expected:** Either include `overall_grade` in the serializer (backend computes it from snapshots) or document that it's client-only.

---

## Bug 3: `gradeFilter` Sort Puts Disqualified F Companies in Wrong Position on "Best First"

**Severity:** Medium

**Where:** Sort button — "Best first ↓" sort mode

**What:** The sort logic (lines 159-165 of `+page.svelte`) pushes F-grade companies to the bottom in `desc` mode (best-first), but GEO Group and CoreCivic are sorted alongside regular F companies rather than always at the very bottom.

**Current behavior:**
```
desc sort (best first):
A+ → A → A- → B+ → ... → F (disqualified ICE detention)
```

**Expected:** Disqualified F companies (GEO, CoreCivic — ICE detention) should always sort to the very bottom, even below regular F companies, regardless of sort direction.

**Note:** This may be intentional design — the ticket says "sort to bottom when Best first" for disqualified Fs. Need designer confirmation.

---

## Bug 4: Palantir and Target Missing from `ice_collaborator` Value Filter (Client-Side)

**Severity:** Low

**Where:** Value filter dropdown — "ICE Collaborator"

**What:** The `ice_collaborator` value filter on the frontend is client-side (no backend `value` param support in the DRF view for grouped values). Companies with `ice_collaborator` data (Palantir, Target) are correctly returned by `/api/companies/?value=ice_collaborator` on VM 406, but it's unclear if the frontend value filter correctly isolates them on the demo.

**Verified via API:**
- Palantir (PLTR): `ice_collaborator: F` ✓
- Target (TGT): `ice_collaborator: F` ✓
- API `/api/companies/?value=ice_collaborator` returns both ✓

---

## Verified Working (No Bug)

These behavioral tests PASSED — documented for confidence:

| Test | Result | Details |
|------|--------|---------|
| GEO Group overall F | ✅ PASS | `ice_detention: F` → client computes overall F |
| CoreCivic overall F | ✅ PASS | `ice_detention: F` → client computes overall F |
| Target overall F | ✅ PASS | `ice_collaborator: F` → client computes overall F |
| Palantir overall F | ✅ PASS | `ice_collaborator: F` → client computes overall F |
| ICE detention filter | ✅ PASS | API returns only GEO and CoreCivic (2 companies) |
| ICE collaborator filter | ✅ PASS | API returns Palantir and Target |
| Pagination | ✅ PASS | 381 companies / 4 pages / PAGE_SIZE=100 |
| Multi-source ESG | ✅ PASS | Apple shows "ESG Risk: 25.8 (2 sources)" |
| Multiple value grades | ✅ PASS | Costco: 10 different value snapshots |
| Adobe (ESG only) | ✅ PASS | Only `esg_score` and `lgbtq_equality`, no extra blanks |
| No `undefined` grades on card | ✅ PASS | API response has `grade` field for all snapshots |

---

## Pending Manual Browser Testing

The following require a human to test in a browser (not verifiable via API alone):

- [ ] Page load on alonovo.cooperation.org (VM 406 — not tested)
- [ ] Search by partial name (case-insensitive)
- [ ] Combined filters (search + sector + grade)
- [ ] User login/logout OAuth flow
- [ ] Profile page weight saving and reload
- [ ] Mobile responsive layout at 375px
- [ ] "Back to all companies" preserves filters or resets
- [ ] Deep link to nonexistent company shows error gracefully
- [ ] Footer source links open in new tab
- [ ] Login page styling (green theme)

---

## Summary

**1 bug confirmed** (grade filter performance — client-side filtering of all companies), **1 informational** (overall_grade not in API), **1 medium** (disqualified F sort order — needs designer input).

All core behavioral logic (disqualifying F → overall F, ICE filter accuracy, pagination) is working correctly.

Full browser testing on alonovo.cooperation.org still needed — the demo domain uses the same DB so data behavior should be identical.