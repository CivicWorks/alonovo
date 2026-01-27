# Alonovo

Consumer-facing app for ethical company ratings. Know before you buy, know before you invest.

**Live site:** https://alonovo.cooperation.org

---

## DO NOT (read this first)

1. **DO NOT drop, reset, or truncate the database.** The data is real, sourced from OpenSecrets, BBFAW, EggTrack, USASpending, S&P Global, and Yahoo Finance. There are 280+ companies and 300+ claims. If you need to undo something, restore from backup (see below).
2. **DO NOT run `python manage.py flush` or `migrate --run-syncdb` or delete migration files.**
3. **DO NOT edit `backend/alonovo/settings.py`** unless you fully understand the OAuth, CSRF, and template configuration. Incorrect changes will break Google login for all users.
4. **DO NOT change the frontend API URL** in `frontend/.env.development`. It must be `https://alonovo.cooperation.org/api` — not localhost. The browser makes API calls, not the server.
5. **DO NOT rebuild the frontend** (`npm run build`). The Vite dev server runs live on port 5173 with hot reload. Nginx proxies to it.
6. **DO NOT kill the Vite dev server or gunicorn** unless you know how to restart them (see Operations below).
7. **DO NOT modify Claims** — they are immutable by design. The model raises `ValidationError` on update. Create new claims instead.
8. **DO NOT remove the `{#if true}` wrapper around `{@const}` in Svelte templates** — Svelte 5 requires `@const` inside block tags.

---

## How to Work (important)

1. **Make one small change at a time.** Edit one file, check the browser, confirm it works, then move on. Do not batch multiple changes across files and hope they all work.
2. **Check the browser after every change.** The frontend hot-reloads — just save and look. If something breaks, undo the last change immediately.
3. **If you break something, stop and undo.** Don't try to fix forward through a cascade of errors. Revert the file (`git checkout -- path/to/file`) and try again with a smaller change.
4. **Back up before risky operations.** Any management command that writes data, any model change, any settings change — back up first (see Backups below).
5. **Test the API separately.** Use `curl https://alonovo.cooperation.org/api/companies/` to verify backend changes work before touching the frontend.
6. **Read files before editing them.** Understand what's there before you change it.

---

## Backups

Database backups live in `/home/ec2-user/alonovo2/backups/`.

**To create a backup:**
```bash
# Django JSON backup (preferred — portable, includes all apps)
cd /home/ec2-user/alonovo2/backend
source venv/bin/activate
python manage.py dumpdata --natural-primary --natural-foreign -o ../backups/alonovo_full_$(date +%Y%m%d_%H%M%S).json

# Postgres SQL backup
sudo -u postgres pg_dump alonovo > ../backups/alonovo_pgdump_$(date +%Y%m%d_%H%M%S).sql
```

**To restore from Django backup:**
```bash
python manage.py loaddata ../backups/alonovo_full_YYYYMMDD_HHMMSS.json
```

**Back up before:** schema changes, data imports, any management command that writes data.

---

## Architecture

- **Frontend**: SvelteKit (Svelte 5 runes mode — uses `$state()`, `$derived`, not `let` reactivity)
- **Backend**: Django 4.2 + Django REST Framework
- **Database**: Postgres (local, no Docker)
- **Auth**: Google OAuth via django-allauth + dj-rest-auth
- **Serving**: nginx → Vite dev server (frontend, port 5173) + gunicorn (backend, port 8000)

## Operations

```bash
# All commands run from /home/ec2-user/alonovo2/backend
cd /home/ec2-user/alonovo2/backend
source venv/bin/activate

# Restart gunicorn (Django backend)
# NOTE: pkill exits 144 — this is normal. Run the start command separately after.
sudo pkill -f gunicorn
sleep 2
gunicorn alonovo.wsgi:application --bind 127.0.0.1:8000 --workers 3 --daemon

# Restart Vite dev server (frontend)
# Check if running first:
ps aux | grep vite | grep -v grep
# If not running:
cd /home/ec2-user/alonovo2/frontend
nohup npx vite dev --host 0.0.0.0 --port 5173 > /tmp/vite-dev.log 2>&1 &

# Run Django management command
python manage.py <command>

# Django shell
python manage.py shell
```

## Data Model

```
Value (slug PK)              — ethical criterion (e.g., "esg_score", "ice_contracts")
  ├── ScoringRule            — thresholds/mappings for grading
  ├── CompanyValueSnapshot   — computed grade per company per value
  └── CompanyBadge           — display badges on cards

Company (uri unique)         — company with ticker, name, sector
Claim (uri unique)           — immutable source fact with provenance
```

**Key flags on Value:**
- `is_disqualifying`: F on this value = F overall (ice_detention, ice_collaborator)
- `is_fixed`: user cannot set weight to zero (ice_contracts, ice_detention, ice_collaborator)

**Overall grade** is computed client-side in `frontend/src/lib/utils.ts:computeOverallGrade()`:
- If any disqualifying value has grade F → overall F
- Otherwise average all value scores: A >= 0.8, B >= 0.3, C >= -0.1, D >= -0.5, F < -0.5

**Current values (7):** corporate_lobbying, cage_free_eggs, farm_animal_welfare, ice_contracts, ice_detention, ice_collaborator, esg_score, stood_up

## Adding New Data

Use management commands in `backend/core/management/commands/`. See existing examples:
- `import_initial_data.py` — lobbying, BBFAW, EggTrack, ICE data
- `import_esg_data.py` — ESG scores from CSV and S&P Global

Pattern for adding data:
1. Create/update a `Value` and `ScoringRule`
2. Create `Company` entries (dedup by ticker using `get_or_create_company()`)
3. Create `Claim` entries (check URI doesn't exist first — claims are immutable)
4. Compute `CompanyValueSnapshot` from claims using scoring rules
5. Create `CompanyBadge` entries from snapshots
6. Restart gunicorn: `sudo pkill -f gunicorn; sleep 2; gunicorn ...`

## Key Files

| What | Where |
|------|-------|
| Django settings | `backend/alonovo/settings.py` |
| Models | `backend/core/models.py` |
| API views | `backend/core/views.py` |
| Serializers | `backend/core/serializers.py` |
| API URLs | `backend/core/urls.py` |
| Frontend types | `frontend/src/lib/types.ts` |
| API client | `frontend/src/lib/api.ts` |
| Grade logic | `frontend/src/lib/utils.ts` |
| Main page | `frontend/src/routes/+page.svelte` |
| Company detail | `frontend/src/routes/company/[ticker]/+page.svelte` |
| Profile page | `frontend/src/routes/profile/+page.svelte` |
| Global styles | `frontend/src/app.css` |
| Nginx config | `/etc/nginx/conf.d/alonovo.conf` |
| Vite config | `frontend/vite.config.ts` |
| DB backups | `backups/` |

## Tickets

- **Local tickets:** `tickets/` directory in this repo (Claude Code can read these)
- **Taiga board:** https://marten.linkedtrust.us/board (additional tickets, requires login — ask team lead for access)

Check both places before picking up work.

## Team & Git Attribution

See `.claude/team.md` for contributor info and commit attribution rules. That file is not checked in.

## Coding Standards

- 4-space indentation, never tabs
- Never write manual migration files — use `python manage.py makemigrations`
- Keep serializers simple — basic ModelSerializer
- Svelte 5 runes: use `$state()`, `$derived`, not legacy `let` reactivity
- `{@const}` must be inside a block tag (`{#if}`, `{#each}`, etc.)
- Frontend API URL in `.env.development` must be a full URL (not relative like `/api`) — `getLoginUrl()` in `api.ts` uses `new URL()` which breaks on relative paths. The actual API calls use `window.location.origin` at runtime so both domains work.

## Data Philosophy

**Claims are the source of truth.** We ingest LinkedClaims (signed, URI-addressable statements with provenance). Django models are digested views of claim data, always pointing back to source claims via `claim_uris`.

**Authoritative spec:** https://identity.foundation/labs-linkedclaims/

## References

- LinkedClaims SDK: `~/parent/linked-trust/LinkedClaims/sdk/`
- trust_claim_backend: `~/parent/linked-trust/trust_claim_backend/`
- live.linkedtrust.us for working example
