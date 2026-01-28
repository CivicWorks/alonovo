# Category Roll-Up

## What Changed

Individual subcategory values (e.g., "ICE/CBP Contracts", "ICE Detention Operations") are no longer exposed directly in the UI. Instead, they are rolled up into main categories that users see.

## Main Categories

| Category | Constituent Values |
|---|---|
| Political Lobbying | `corporate_lobbying` |
| Executive Pay Ratios | `ethics_of_executives` |
| Carbon Footprint | `esg_score` |
| ICE Collaboration | `ice_contracts`, `ice_detention`, `ice_collaborator` |
| Animal Welfare | `farm_animal_welfare`, `cage_free_eggs`, `cruelty_free` |
| Stood Up | `stood_up` |
| Fair Labor/Anti-Union | *(no data yet)* |
| DEI Policies | *(no data yet)* |
| Supply Chain Standards | *(no data yet)* |

## How It Works

- **No data model changes.** The backend still stores and serves flat values and snapshots.
- The category mapping lives in `frontend/src/lib/categories.ts`.
- `rollUpToCategories()` in `frontend/src/lib/utils.ts` groups a company's value snapshots by category and computes a category-level grade (average of constituent value scores).
- The overall grade calculation is unchanged — it still averages all individual value scores.

## Where Categories Appear

- **Main page:** Filter dropdown shows category names instead of individual values.
- **Company detail page:** Shows category-level grade cards. Claims are grouped under each category.
- **Profile page:** Weight sliders are per-category. When saved, the category weight is applied to all constituent values.

## Adding a New Value to an Existing Category

1. Create the value, scoring rule, claims, and snapshots as usual (see `prompts/add-data.md`).
2. Add the new value's slug to the appropriate category's `valueSlugs` array in `frontend/src/lib/categories.ts`.

## Adding a New Category

1. Add the data (values, claims, snapshots) via a management command.
2. Add a new entry to the `CATEGORIES` array in `frontend/src/lib/categories.ts` with the category slug, display name, and constituent value slugs.
