# Ticket: Add Frontend Pagination for Company List

## Status: Ready

## Summary

The company list page currently loads all companies in a single API call (no pagination). This works fine at our current size (~335 companies) but will not scale. Add pagination to the frontend so we can re-enable backend pagination.

## Current Behavior

- Backend: `CompanyViewSet` has `pagination_class = None` — returns all companies as a flat JSON array
- Frontend: `fetchCompanies()` in `frontend/src/lib/api.ts` makes one fetch and returns the full list
- The header shows the total count from `filtered.length`

## Desired Behavior

- Backend: Re-enable DRF pagination (remove `pagination_class = None` from `backend/core/views.py` line 20)
- Frontend: Either fetch all pages on load, or add a "Load More" / infinite scroll UI
- The header count must still show the TOTAL filtered count, not just the current page

## Approach: Fetch All Pages on Load (Recommended)

This is the safest approach — no UI changes needed, just change `fetchCompanies()`.

**File to edit:** `frontend/src/lib/api.ts` — `fetchCompanies()` function only

```typescript
export async function fetchCompanies(): Promise<Company[]> {
    const all: Company[] = [];
    let url: string | null = `${apiBase()}/companies/`;
    while (url) {
        const response = await fetch(url);
        if (!response.ok) throw new Error('Failed to fetch companies');
        const data = await response.json();
        if (Array.isArray(data)) {
            // No pagination (current state)
            return data;
        }
        all.push(...data.results);
        url = data.next;
    }
    return all;
}
```

Then in `backend/core/views.py`, remove `pagination_class = None` from `CompanyViewSet`.

## DO NOT

- Do not change the company card components, filters, sorting, or header stats
- Do not change models, serializers, or other views
- Do not change the page size in DRF settings (default 100 is fine)
- Do not add URL query parameters to the frontend for pagination state
- Do not change `fetchCompany()` (single company lookup) — only `fetchCompanies()` (list)

## How to Test

1. Make the changes
2. Refresh the main page
3. Verify the header shows the correct total company count (335+)
4. Verify search, sector filter, value filter, and grade filter all still work
5. Verify sort by grade still works
6. Click a company card — verify the detail page still loads

## Files Involved

| File | Change |
|------|--------|
| `frontend/src/lib/api.ts` | Update `fetchCompanies()` to handle paginated responses |
| `backend/core/views.py` | Remove `pagination_class = None` from `CompanyViewSet` |
