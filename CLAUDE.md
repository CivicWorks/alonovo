# Alonovo

Consumer-facing app for ethical company ratings. Know before you buy, know before you invest.

## Architecture

- **Frontend**: SvelteKit
- **Backend**: Django + Django REST Framework
- **Database**: Postgres (local install, no Docker)
- **Auth**: OAuth (dj-rest-auth or django-oauth-toolkit)
- **Deployment**: Ansible → Ubuntu (NixOS later)

## Stack Rationale

- **Django** chosen because we need Django Admin for data management
- **DRF** for pagination, OAuth, standard API patterns
- **Keep serializers simple** — basic ModelSerializer, no complex nesting
- **Lightweight** — should run on any Ubuntu server, future NixOS deployment

## Development Setup

**No Docker.** Local development only:

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# Frontend
cd frontend
npm install
npm run dev
```

## Deployment (Ansible)

See `ansible/` directory.

### Ansible Principles

1. **One role = one concern** — `roles/nodejs`, `roles/postgres`, `roles/nginx`, not one big `roles/app`
2. **Document packages explicitly** — list actual packages needed, not just `build-essential`
3. **Env vars in one place** — `vars/env.yml` for non-sensitive config
4. **Secrets separate** — use `ansible-vault` or CI secrets for passwords/keys, never plaintext in repo
5. **Avoid Ansible magic** — no complex Jinja2, no dynamic inventory wizardry
6. **Minimal templating** — service files can have 2-3 variables (`deploy_path`, `app_user`), not 50
7. **Systemd service files in repo** — actual files in `ansible/files/`, minimal templating

### CI/CD

GitHub Actions runs Ansible on push to main:
```bash
ansible-playbook -i ansible/inventory/prod.yml ansible/playbook.yml
```

## Data Philosophy

**Claims are the source of truth.**

We ingest LinkedClaims (signed, URI-addressable statements with provenance). Django models are digested, queryable views of claim data — fully populated for app display, but always pointing back to source claims.

```
[external claims] → ingest/digest → [Django models] → serve → [app]
                                           ↓
                                   source_claim_uris (provenance)
```

When we compute scores, we emit our own LinkedClaims. Alonovo is both a consumer and producer in the web of trust.

## LinkedClaims Spec

**Authoritative specification:** https://identity.foundation/labs-linkedclaims/

A LinkedClaim:
- **MUST** have a `subject` that is a valid URI
- **MUST** have an `id` that is a well-formed URI
- **MUST** be cryptographically signed
- **SHOULD** include a date in signed data
- **SHOULD** contain evidence/source, optionally hashlinked
- **MAY** have an `object` (for "A rated B" style claims)
- **MAY** have a narrative statement

## Key Documentation

- `FIRST_MIGRATION.md` — Phase 1 tasks, getting from current state to working Django+SvelteKit
- `data_models.md` — Complete model definitions and scoring logic
- `ansible/README.md` — Deployment documentation

## Project Structure

```
alonovo/
├── ansible/
│   ├── inventory/
│   │   ├── dev.yml
│   │   └── prod.yml
│   ├── roles/
│   │   ├── common/
│   │   ├── postgres/
│   │   ├── backend/
│   │   ├── frontend/
│   │   └── nginx/
│   ├── vars/
│   │   └── env.yml
│   ├── files/
│   │   ├── alonovo-backend.service
│   │   └── alonovo-frontend.service
│   ├── playbook.yml
│   └── README.md
├── backend/
│   ├── alonovo/          # Django settings, urls
│   └── core/             # Main app - models, views, serializers
├── frontend/             # SvelteKit app
├── data/                 # Legacy static JSON (reference only)
├── data_models.md
├── FIRST_MIGRATION.md
└── CLAUDE.md
```

## Coding Standards

- 4-space indentation always, never 3 spaces or tabs
- Never write manual migration files — use `python manage.py makemigrations`
- Keep serializers simple — basic ModelSerializer
- Concise code, minimal comments

## References

- **LinkedClaims spec (authoritative):** https://identity.foundation/labs-linkedclaims/
- LinkedClaims SDK: `~/parent/linked-trust/LinkedClaims/sdk/`
- trust_claim_backend (reference implementation): `~/parent/linked-trust/trust_claim_backend/`
- live.linkedtrust.us for working example
