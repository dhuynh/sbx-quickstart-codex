# Project Guidance: sbx-quickstart

## Workflow Rules

- **Never `git push` without explicit user confirmation.** Always stage and commit as requested, then stop and ask before pushing.

## What This Repo Is

A hands-on guide for new users of Docker Sandboxes (`sbx`), using **DevBoard** — a full-stack Next.js + FastAPI issue tracker — as the exercise app. The guide lives in `README.md`.

## Reference Documentation

Official Docker Sandboxes docs: **https://docs.docker.com/ai/sandboxes/**

Key sub-pages:
- Get started / usage
- Agents (codex, copilot, gemini, docker-agent, kiro, opencode, custom-environments)
- Architecture, security, credentials
- Troubleshooting / FAQ

## Key sbx CLI Facts (from docs, for verification)

- `sbx create` requires explicit workspace path: `sbx create --name=foo codex .`
- `sbx run` infers current dir: `sbx run codex` or reconnect with `sbx run <sandbox-name>`
- Codex auth should use `sbx secret set -g openai` or `sbx secret set -g openai --oauth`
- Worktrees stored at `.sbx/<sandbox-name>-worktrees/<branch>/`
- Multiple workspaces: first path = primary (rw), extras append `:ro` for read-only
- `sbx policy deny` — confirmed valid (allow, deny, log, ls, reset, rm, set-default all confirmed via `sbx policy --help`)
- Global secrets inject at creation time; sandbox-scoped secrets inject immediately
- Services must bind to `0.0.0.0` (not `127.0.0.1`) for port forwarding to work
- `host.docker.internal` to reach host services from inside sandbox
- `SBX_NO_TELEMETRY=1` to disable telemetry

---

# DevBoard

A developer issue and project tracker — demo application for the Docker Sandboxes guide.

## Stack

- **Backend**: FastAPI + SQLAlchemy + PostgreSQL
- **Frontend**: Next.js 14 (App Router) + Tailwind CSS
- **Infrastructure**: Docker Compose

## Quick start (local)

```bash
# Start everything
docker compose up --build

# API docs
open http://localhost:8000/docs

# Frontend
open http://localhost:3000
```

## Running backend tests

```bash
cd backend
pip install -r requirements.txt
pytest tests/ -v
```

## Known issues

This codebase contains a few intentional bugs and unfinished features — they're
the basis for exercises in the Docker Sandboxes guide:

1. **Pagination bug** — `list_issues` uses the wrong `skip` value (`page * page_size`
   instead of `(page - 1) * page_size`), so page 1 always skips items.
2. **`updated_at` never updates** — the SQLAlchemy `updated_at` columns are missing
   `onupdate=datetime.utcnow`, so they stay frozen at creation time.
3. **Missing authorization on issue update** — any project member can edit any issue,
   regardless of whether they're the reporter or assignee.
4. **Search not implemented** — `GET /projects/{id}/issues/search` returns `501`.
5. **Email notifications are stubs** — `services/notifications.py` logs but doesn't send.

See the Docker Sandboxes guide for step-by-step exercises that use Codex to find
and fix each of these.

## Project structure

```
devboard/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app, CORS, router registration
│   │   ├── models.py        # SQLAlchemy models (User, Project, Issue, Comment)
│   │   ├── schemas.py       # Pydantic request/response schemas
│   │   ├── auth.py          # JWT helpers, password hashing
│   │   ├── config.py        # Settings (pydantic-settings)
│   │   ├── database.py      # Engine, session, Base
│   │   ├── routers/
│   │   │   ├── auth.py      # /auth/register, /auth/login, /auth/me
│   │   │   ├── projects.py  # /projects CRUD
│   │   │   ├── issues.py    # /projects/{id}/issues CRUD + search
│   │   │   └── comments.py  # /projects/{id}/issues/{id}/comments CRUD
│   │   └── services/
│   │       └── notifications.py  # Stub email service (TODO)
│   └── tests/
│       ├── conftest.py      # SQLite test DB, fixtures
│       ├── test_auth.py
│       └── test_issues.py   # Tests that expose the known bugs
├── frontend/
│   └── src/
│       ├── app/             # Next.js App Router pages
│       ├── components/      # Shared UI components
│       └── lib/api.ts       # Axios API client
└── docker-compose.yml
```
