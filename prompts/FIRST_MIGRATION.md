# First Migration: Phase 1

## Goal

Replace hardcoded frontend data with Django API serving the same 20 companies. Verify end-to-end before adding anything new.

## Architecture

- **Frontend**: SvelteKit
- **Backend**: Django + Django REST Framework
- **Database**: Postgres (local install, no Docker)
- **Auth**: OAuth (later — not in Phase 1)

## Project Structure

```
alonovo/
├── backend/
│   ├── alonovo/          # Django settings, urls
│   └── core/             # Main app - models, views, serializers
├── frontend/             # SvelteKit (replaces current vanilla JS)
├── data/                 # Legacy static JSON (reference only)
├── data_models.md        # Full model documentation
├── CLAUDE.md             # Project overview
└── FIRST_MIGRATION.md    # This file
```

## Current State

- Vanilla JS frontend in `/frontend` with hardcoded company data
- Static JSON in `/data/scored_companies.json` and `/data/lobbying_2024.json`
- No backend

## Phase 1 Models (Bare Minimum)

For Phase 1, use simplified models. See `data_models.md` for full model specs to be added later.

```python
class Claim(models.Model):
    """LinkedClaim storage - real fields, not JSONB
    
    Spec: https://identity.foundation/labs-linkedclaims/
    """
    uri = models.CharField(max_length=500, unique=True)
    subject = models.CharField(max_length=500, db_index=True)
    object = models.CharField(max_length=500, blank=True)  # for "A rated B" claims
    claim = models.CharField(max_length=100)  # e.g. "LOBBYING_SPEND"
    statement = models.TextField(blank=True)
    effective_date = models.DateField(null=True, blank=True)
    source_uri = models.CharField(max_length=500, blank=True)
    how_known = models.CharField(max_length=50, blank=True)
    date_observed = models.DateField(null=True, blank=True)
    digest_multibase = models.CharField(max_length=200, blank=True)
    score = models.FloatField(null=True, blank=True)
    aspect = models.CharField(max_length=100, blank=True)
    amt = models.FloatField(null=True, blank=True)
    unit = models.CharField(max_length=50, blank=True)
    author = models.CharField(max_length=300, blank=True)
    curator = models.CharField(max_length=300, blank=True)
    issuer_id = models.CharField(max_length=300, blank=True)
    issuer_id_type = models.CharField(max_length=20, blank=True)
    proof = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Company(models.Model):
    uri = models.CharField(max_length=500, unique=True)
    ticker = models.CharField(max_length=10, db_index=True)
    name = models.CharField(max_length=200)
    sector = models.CharField(max_length=100)


class CompanyScore(models.Model):
    """Simplified snapshot for Phase 1. Will become CompanyValueSnapshot later."""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='scores')
    score = models.FloatField()  # normalized -1 to 1
    grade = models.CharField(max_length=5)
    raw_value = models.FloatField()  # e.g. 18850000
    reason = models.TextField(blank=True)
    computed_at = models.DateTimeField(auto_now_add=True)
    source_claim_uris = models.JSONField(default=list)
```

## Phase 1 Tasks (In Order)

### 1. Set up Django project

```bash
cd /path/to/alonovo
mkdir backend
cd backend
python -m venv venv
source venv/bin/activate
pip install django djangorestframework psycopg2-binary django-cors-headers python-decouple
django-admin startproject alonovo .
python manage.py startapp core
```

Add to `INSTALLED_APPS`:
```python
INSTALLED_APPS = [
    ...
    'corsheaders',
    'rest_framework',
    'core',
]
```

Add CORS middleware (must be high in the list):
```python
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    ...
]
```

### 2. Configure local Postgres

Create database locally:

```bash
createdb alonovo_dev
```

Use environment variables in `settings.py`:

```python
from decouple import config

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='alonovo_dev'),
        'USER': config('DB_USER', default=''),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

# CORS - allow frontend dev server
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:5173,http://127.0.0.1:5173',
    cast=lambda v: [s.strip() for s in v.split(',')]
)
```

Create `.env` file (not committed):
```
DB_NAME=alonovo_dev
DB_USER=your_user
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=5432
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

### 3. Create models

Add models from above to `core/models.py`.

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Django Admin

Register all models in `core/admin.py`:

```python
from django.contrib import admin
from .models import Claim, Company, CompanyScore

admin.site.register(Claim)
admin.site.register(Company)
admin.site.register(CompanyScore)
```

Create superuser:

```bash
python manage.py createsuperuser
```

### 5. DRF API

Simple serializers in `core/serializers.py`:

```python
from rest_framework import serializers
from .models import Company, CompanyScore

class CompanyScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyScore
        fields = '__all__'

class CompanySerializer(serializers.ModelSerializer):
    scores = CompanyScoreSerializer(many=True, read_only=True)
    
    class Meta:
        model = Company
        fields = '__all__'
```

Views in `core/views.py`:

```python
from rest_framework import viewsets
from .models import Company
from .serializers import CompanySerializer

class CompanyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Company.objects.prefetch_related('scores')
    serializer_class = CompanySerializer
    lookup_field = 'ticker'
```

Wire up URLs.

### 6. Load existing data

Management command `core/management/commands/load_initial_data.py`:

- Read `/data/scored_companies.json`
- Create Company records
- Create Claim records (subject=company URI, claim="LOBBYING_SPEND", amt=lobbying_spend)
- Create CompanyScore records linking to Claim URIs

### 7. Set up SvelteKit

```bash
cd /path/to/alonovo
rm -rf frontend  # remove old vanilla JS
npm create svelte@latest frontend
cd frontend
npm install
```

Use environment variable for API URL in SvelteKit. Create `.env`:

```
PUBLIC_API_URL=http://localhost:8000/api
```

Use in code:
```javascript
import { PUBLIC_API_URL } from '$env/static/public';

const response = await fetch(`${PUBLIC_API_URL}/companies/`);
```

### 8. Verify end-to-end

- Start Django: `python manage.py runserver`
- Start SvelteKit: `npm run dev`
- Frontend displays 20 companies from API
- Filters work
- Detail view works
- Django admin shows all data

**Do NOT proceed to new features until Phase 1 is verified working.**

## Coding Standards

- 4-space indentation always, never 3 spaces or tabs
- Never write manual migration files — use `python manage.py makemigrations`
- Keep serializers simple — basic ModelSerializer
- Concise code, minimal comments

## Reference Data

- `/data/scored_companies.json` — 20 companies with lobbying grades
- `/data/lobbying_2024.json` — raw lobbying spend data
