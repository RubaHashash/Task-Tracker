# Task Tracker (Module 4)

## 1. Project Overview

A FastAPI backend + vanilla HTML/CSS/JavaScript Kanban-style task tracker,
built incrementally as part of an AI-assisted coding course. Tasks are held
in a plain in-memory dict (`app/storage.py`) — **all data is lost on backend
restart, and there is no database.**

This milestone (Module 4 / mid-course) adds optional task due dates, overdue
filtering, and search/filter combinations on top of the base CRUD API. See
[Section 10](#10-technical-decisions) for the design note behind those
features.

This is a course project: there is no authentication, no persistent storage,
and no deployment or production configuration of any kind.

## 2. Prerequisites

- Python 3.11 [VERIFY: this matches the version pinned in `Dockerfile` and
  `.github/workflows/ci.yml`; no local-dev version requirement is stated
  elsewhere in the repo]
- pip
- (Optional) Docker, only needed for [Section 6](#6-run-with-docker)

## 3. Local setup

Run all commands from the repo root.

```bash
python -m venv venv
```

Activate the virtual environment:

```powershell
# Windows (PowerShell)
venv\Scripts\Activate.ps1
```

```bash
# macOS/Linux
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## 4. Run the app locally

Start the backend:

```bash
uvicorn app.main:app --reload --port 8000
```

The API is now available at `http://localhost:8000` (interactive docs at
`http://localhost:8000/docs`).

The frontend is a single static file (`app/frontend/index.html`) and is
**not** served by FastAPI. Serve it separately, in another terminal, from
the repo root:

```bash
python -m http.server 5500 --directory app/frontend
```

Then open `http://localhost:5500`. The frontend has the backend URL
hardcoded as `http://localhost:8000` (`app/frontend/index.html`), so the
backend must already be running there.

## 5. Run tests

```bash
pytest -v
```

Run a single test:

```bash
pytest tests/test_tasks.py::test_name -v
```

`tests/verify_a.py` is a standalone ad-hoc script (prints PASS/FAIL) and is
not part of the pytest suite — run it directly if you need it:

```bash
python tests/verify_a.py
```

## 6. Run with Docker

Build and run the backend only:

```bash
docker build -t task-tracker .
docker run --rm -p 8000:8000 task-tracker
```

The API is now available at `http://localhost:8000` (interactive docs at
`http://localhost:8000/docs`). In-memory storage means data is also lost
whenever the container stops.

The Docker image only runs the FastAPI backend (`uvicorn`, per the
`Dockerfile`'s `CMD`) — it does not serve the frontend. To use the frontend
against a containerized backend, run the static server from
[Section 4](#4-run-the-app-locally) separately, on the host.

## 7. CI workflow summary

`.github/workflows/ci.yml` runs on every push (any branch) and on pull
requests targeting `main`:

1. Check out the repo (`actions/checkout@v4`)
2. Set up Python 3.11 (`actions/setup-python@v5`)
3. Cache `~/.cache/pip`, keyed on `requirements.txt`'s hash
4. Upgrade pip, then `pip install -r requirements.txt`
5. Run `python -m pytest -v --tb=short`

There is currently no lint, type-check, build, or deploy step
[VERIFY: confirm whether this is intentional for the current milestone].

## 8. Project structure

```
app/
  main.py             FastAPI app instance, CORS config, route handlers
  models.py           Pydantic models (TaskCreate/TaskUpdate/TaskResponse,
                      TaskStatus/TaskPriority enums)
  storage.py          In-memory task CRUD + filtering (status/priority/
                      overdue/assignee/search, combined with AND logic)
  business_rules.py   Task status transition state machine
  frontend/
    index.html        Static vanilla HTML/CSS/JS frontend (not served by
                      FastAPI; duplicates the status transition rules)
tests/
  conftest.py         Shared fixtures (TestClient, storage reset)
  test_tasks.py       Pytest suite
  verify_a.py         Standalone ad-hoc script, not part of the pytest suite
docs/
  midcourse/
    mini-adr.md        Technical note for the due-date/overdue/search design
    prompt-log.md       AI prompt log for this milestone
  user-stories.md
  verification.md
  reflection.md
Dockerfile
requirements.txt
.github/workflows/ci.yml
```

## 9. Project conventions and current limitations

- **In-memory storage only.** `app/storage.py` holds tasks in a plain dict;
  all data is lost on backend restart. There is no database.
- **No authentication or authorization.**
- **Not configured or intended for production deployment.**
- **Status transitions are single-step.** `app/business_rules.py` only
  allows `ToDo <-> InProgress` and `InProgress <-> Done`; going directly from
  `ToDo` to `Done` (or back), or "transitioning" to the same status, is
  rejected with a 422.
- **Overdue is a strict, naive comparison.** A task is overdue when
  `due_date < today` (strict `<`) and `status != Done`, computed against the
  backend's local date — there is no timezone handling.
- **The frontend duplicates the status transition rules** as
  `ALLOWED_TRANSITIONS` in `app/frontend/index.html`. The backend and
  frontend copies must be kept in sync manually if the rules change.
- **CORS is a hardcoded allow-list**: `http://localhost:5500`,
  `http://127.0.0.1:5500`, `http://localhost:5173`, and `null` (see
  `app/main.py`). Add new origins there if serving the frontend elsewhere.
- **`app/main.py` contains unused dead code** (`LegacyTaskCreate`, `Task`,
  `tasks`) left over from an earlier iteration — not part of the live
  request path.
- **Two requirements may be unused:** `pydantic-settings` and
  `python-dotenv` are in `requirements.txt`, but no code in `app/` currently
  reads a `Settings` object or environment variables, and both `.env` and
  `.env.example` are empty [VERIFY: confirm whether these are placeholders
  for planned configuration or can be removed].

## 10. Technical decisions

See [`docs/midcourse/mini-adr.md`](docs/midcourse/mini-adr.md) for the
mini-ADR covering the due-date/overdue and search/filter design — including
rejected alternatives and a known limitation (naive local-date "overdue"
comparison) flagged for reconsideration if the app ever supports users in
different timezones.
