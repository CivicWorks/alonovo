# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

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

## Architecture

### Three-Platform System

1. **Web (frontend/)**: SvelteKit app for browsing company ratings
2. **Mobile (mobile/)**: Flutter app with barcode scanner for on-the-go product lookups
3. **Backend (backend/)**: Django REST API serving both platforms

### Stack Details

- **Frontend**: SvelteKit (Svelte 5 runes mode — uses `$state()`, `$derived`, not `let` reactivity)
- **Mobile**: Flutter 3.2+ with mobile_scanner, provider for state, http for API calls
- **Backend**: Django 4.2 + Django REST Framework
- **Database**: Postgres (local, no Docker)
- **Auth**: Google OAuth via django-allauth + dj-rest-auth (web only; mobile is read-only anonymous)
- **Serving**: nginx → Vite dev server (frontend, port 5173) + gunicorn (backend, port 8000)

### Data Flow

```
LinkedClaims (immutable source facts)
  ↓
Claim model (stores provenance + values)
  ↓
ScoringRule (defines thresholds: A/B/C/D/F)
  ↓
CompanyValueSnapshot (pre-computed grades per value)
  ↓
Frontend/Mobile (aggregates snapshots into overall grade)
```

**Overall grade computation** (client-side in `frontend/src/lib/utils.ts:computeOverallGrade()`):
- If any disqualifying value has grade F → overall F
- Otherwise weighted average: A ≥ 0.8, B ≥ 0.3, C ≥ -0.1, D ≥ -0.5, F < -0.5
- Plus/minus grades: Each letter has 3 tiers (e.g., A+/A/A-)

### Product Lookup System (Mobile Scanner)

**Barcode scan flow:**
1. Mobile app scans UPC/EAN barcode
2. Calls `/api/scan/?barcode=012345678901`
3. Backend checks `BarcodeCache` (local cache of external API results)
4. If not cached, queries provider chain (`barcode_providers.py`):
   - Open Food Facts → Open Beauty Facts → Open Pet Food Facts
5. Extracts brand names from product data
6. Matches brand to parent company via `BrandMapping` table
7. Returns company + rating + product alternatives

**Models:**
- `Product`: Consumer products with brand, category, barcode
- `BrandMapping`: Maps brand names to parent companies (e.g., "Tide" → Procter & Gamble)
- `BarcodeCache`: Caches external API responses to avoid repeated lookups

---

## Local Development Setup

### Backend Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Copy .env.example to .env and configure:
cp .env.example .env
# Edit .env: set DB_NAME, DB_USER, DB_PASSWORD, SECRET_KEY

# Create Postgres database
createdb alonovo_dev  # or use your DB_NAME from .env

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load initial data (optional, if you have fixtures)
# python manage.py loaddata ../backups/alonovo_full_YYYYMMDD_HHMMSS.json

# Run dev server
python manage.py runserver
# Backend runs on http://localhost:8000
```

### Frontend Setup

```bash
cd frontend
npm install

# Create .env.development with:
# VITE_API_URL=https://alonovo.cooperation.org/api
# (or http://localhost:8000/api for local backend)

npm run dev
# Frontend runs on http://localhost:5173
```

### Mobile Setup

```bash
cd mobile
flutter pub get

# iOS simulator (requires Xcode on macOS)
flutter run

# Android emulator (requires Android Studio)
flutter run

# Physical device
flutter devices  # list connected devices
flutter run -d <device-id>
```

**Mobile API endpoint:** Edit `mobile/lib/config.dart` to point to your backend:
```dart
static const String apiBaseUrl = 'http://localhost:8000/api';  // local
// or 'https://alonovo.cooperation.org/api' for production
```

---

## Common Commands

### Backend (Django)

```bash
cd backend
source venv/bin/activate

# Run dev server
python manage.py runserver

# Create migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Django shell (interactive Python with models loaded)
python manage.py shell

# Run tests
python manage.py test

# Import data (custom management commands)
python manage.py import_initial_data     # lobbying, BBFAW, EggTrack, ICE
python manage.py import_esg_data         # ESG scores
python manage.py import_peta_data        # PETA data
python manage.py load_products           # seed 345 grocery products
python manage.py seed_brand_mappings     # brand→company mappings

# Admin interface
# Visit http://localhost:8000/admin after running server
```

### Frontend (SvelteKit)

```bash
cd frontend

# Run dev server (with hot reload)
npm run dev

# Type checking
npm run check

# Type checking (watch mode)
npm run check:watch

# Build for production (DO NOT run on live server — see DO NOT section)
npm run build

# Preview production build
npm run preview
```

### Mobile (Flutter)

```bash
cd mobile

# Install dependencies
flutter pub get

# Run app (debug mode, hot reload enabled)
flutter run

# Run on specific device
flutter run -d <device-id>

# Build APK (Android)
flutter build apk

# Build iOS (requires macOS + Xcode)
flutter build ios

# Run tests
flutter test

# Analyze code
flutter analyze
```

---

## Production Operations (EC2 Server)

**WARNING:** These commands apply to `/home/ec2-user/alonovo2/` on the EC2 server, NOT local development.

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

---

## Backups

Database backups live in `/home/ec2-user/alonovo2/backups/` on production server.

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

## Data Model

```
Value (slug PK)              — ethical criterion (e.g., "esg_score", "ice_contracts")
  ├── ScoringRule            — thresholds/mappings for grading
  ├── CompanyValueSnapshot   — computed grade per company per value
  └── CompanyBadge           — display badges on cards

Company (uri unique)         — company with ticker, name, sector
  ├── Product                — consumer products (for mobile barcode scanner)
  └── BrandMapping           — maps brand names to parent companies

Claim (uri unique)           — immutable source fact with provenance
BarcodeCache                 — cached barcode lookup results from external APIs

UserValueWeight              — user's custom value weights (requires auth)
```

**Key flags on Value:**
- `is_disqualifying`: F on this value = F overall (ice_detention, ice_collaborator)
- `is_fixed`: user cannot set weight to zero (ice_contracts, ice_detention, ice_collaborator)
- `display_group`: groups related values (e.g., all ICE values collapse into one)

**Current values (8):** corporate_lobbying, cage_free_eggs, farm_animal_welfare, ice_contracts, ice_detention, ice_collaborator, esg_score, stood_up

---

## API Endpoints

### Web App Endpoints
- `GET /api/companies/` — list all companies with ratings
- `GET /api/companies/{ticker}/` — single company detail
- `GET /api/companies/{ticker}/claims/` — claims backing a company's ratings
- `GET /api/values/` — list all value definitions
- `GET /api/sectors/` — list distinct company sectors
- `GET /api/me/` — current user info (or 204 if not authenticated)
- `GET /api/me/weights/` — user's value weights
- `POST /api/me/weights/` — update user's value weights

### Mobile App Endpoints
- `GET /api/scan/?barcode={code}` — barcode lookup, returns company + rating
- `GET /api/alternatives/{ticker}/?category={category}` — better-rated alternatives in same category
- `GET /api/brands/` — list all brand→company mappings
- `GET /api/products/` — list all products
- `GET /api/products/categories/` — list distinct product categories

---

## Adding New Data

Use management commands in `backend/core/management/commands/`. See existing examples:
- `import_initial_data.py` — lobbying, BBFAW, EggTrack, ICE data
- `import_esg_data.py` — ESG scores from CSV and S&P Global
- `load_products.py` — seed grocery products from CSV

**Pattern for adding a new value:**
1. Create/update a `Value` and `ScoringRule`
2. Create `Company` entries (dedup by ticker using `Company.objects.get_or_create(ticker=...)`)
3. Create `Claim` entries (check URI doesn't exist first — claims are immutable)
4. Compute `CompanyValueSnapshot` from claims using scoring rules
5. Create `CompanyBadge` entries from snapshots (optional, for card display)
6. Restart gunicorn: `sudo pkill -f gunicorn; sleep 2; gunicorn ...`

**Pattern for adding products:**
1. Create `Company` if not exists
2. Create `BrandMapping` entries (brand name → company)
3. Create `Product` entries with barcode, category, brand
4. Mobile app will auto-match scanned products to companies via brand

---

## Key Files

| What | Where |
|------|-------|
| **Backend** | |
| Django settings | `backend/alonovo/settings.py` |
| Models | `backend/core/models.py` |
| API views (web) | `backend/core/views.py` |
| API views (mobile) | `backend/core/views_mobile.py` |
| Serializers (web) | `backend/core/serializers.py` |
| Serializers (mobile) | `backend/core/serializers_mobile.py` |
| API URLs | `backend/core/urls.py` |
| Barcode providers | `backend/core/barcode_providers.py` |
| Brand matching | `backend/core/brand_matcher.py` |
| Management commands | `backend/core/management/commands/` |
| **Frontend** | |
| Main page (company list) | `frontend/src/routes/+page.svelte` |
| Company detail | `frontend/src/routes/company/[ticker]/+page.svelte` |
| User profile | `frontend/src/routes/profile/+page.svelte` |
| API client | `frontend/src/lib/api.ts` |
| Type definitions | `frontend/src/lib/types.ts` |
| Grade computation | `frontend/src/lib/utils.ts` |
| Global state | `frontend/src/lib/stores.svelte.ts` |
| Global styles | `frontend/src/app.css` |
| Vite config | `frontend/vite.config.ts` |
| **Mobile** | |
| Main entry | `mobile/lib/main.dart` |
| Home screen | `mobile/lib/screens/home_screen.dart` |
| Scanner screen | `mobile/lib/screens/scanner_screen.dart` |
| Company detail | `mobile/lib/screens/company_screen.dart` |
| API service | `mobile/lib/services/api_service.dart` |
| Config (API URL) | `mobile/lib/config.dart` |
| **Other** | |
| Nginx config | `/etc/nginx/conf.d/alonovo.conf` (production only) |
| DB backups | `backups/` (production only) |
| Tickets | `tickets/` |

---

## Tickets

- **Local tickets:** `tickets/` directory in this repo (Claude Code can read these)
- **Taiga board:** https://marten.linkedtrust.us/board (additional tickets, requires login — ask team lead for access)

Check both places before picking up work.

---

## Team & Git Attribution

See `.claude/team.md` for contributor info and commit attribution rules. That file is not checked in.

---

## Coding Standards

- 4-space indentation, never tabs
- Never write manual migration files — use `python manage.py makemigrations`
- Keep serializers simple — basic ModelSerializer
- Svelte 5 runes: use `$state()`, `$derived`, not legacy `let` reactivity
- `{@const}` must be inside a block tag (`{#if}`, `{#each}`, etc.)
- Frontend API URL in `.env.development` must be a full URL (not relative like `/api`) — `getLoginUrl()` in `api.ts` uses `new URL()` which breaks on relative paths. The actual API calls use `window.location.origin` at runtime so both domains work.
- Dart/Flutter: follow official Dart style guide, use `const` constructors where possible

---

## Data Philosophy

**Claims are the source of truth.** We ingest LinkedClaims (signed, URI-addressable statements with provenance). Django models are digested views of claim data, always pointing back to source claims via `claim_uris`.

**Authoritative spec:** https://identity.foundation/labs-linkedclaims/

---

## References

- LinkedClaims SDK: `~/parent/linked-trust/LinkedClaims/sdk/`
- trust_claim_backend: `~/parent/linked-trust/trust_claim_backend/`
- live.linkedtrust.us for working example
