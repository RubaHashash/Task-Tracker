# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Setup
python -m venv venv
venv\Scripts\Activate.ps1        # Windows PowerShell
source venv/bin/activate         # macOS/Linux
pip install -r requirements.txt

# Run backend (serves the API)
uvicorn app.main:app --reload --port 8000
# -> http://localhost:8000, interactive docs at http://localhost:8000/docs

# Run frontend (separate static server; not served by FastAPI)
python -m http.server 5500 --directory app/frontend
# -> http://localhost:5500, expects the backend at localhost:8000

# Tests
pytest                              # full suite
pytest tests/test_tasks.py::test_name -v   # single test
```

`tests/verify_a.py` is a standalone ad-hoc script (prints PASS/FAIL), not part of the
pytest suite — run it directly with `python tests/verify_a.py` if referenced.

## Architecture

FastAPI backend (`app/`) + a single-file vanilla HTML/CSS/JS frontend
(`app/frontend/index.html`), with **in-memory storage only** (a plain dict in
`app/storage.py`) — all data is lost on backend restart, and there is no database.

- `app/models.py` — Pydantic models. `TaskCreate`/`TaskUpdate` use
  `model_config = ConfigDict(extra="forbid")`, so unknown fields 422 rather than
  being silently ignored. `TaskStatus` (`ToDo`/`InProgress`/`Done`) and
  `TaskPriority` (`Low`/`Medium`/`High`) are string enums — invalid values 422
  automatically via FastAPI/Pydantic.
- `app/storage.py` — all task CRUD and filtering (`get_all_tasks` applies
  `status`, `priority`, `overdue`, `assignee`, `search` filters, all combined with
  AND logic). `_reset()` clears storage between tests (used by the autouse
  fixture in `tests/conftest.py`).
- `app/business_rules.py` — `validate_status_transition` enforces the task
  status state machine via the `VALID_TRANSITIONS` frozenset. Notably,
  transitions are one step at a time: `ToDo -> Done` and `Done -> ToDo` directly
  are both invalid (must pass through `InProgress`), and a "transition" to the
  same status is also rejected. **The frontend duplicates this same state
  machine** as `ALLOWED_TRANSITIONS` in `app/frontend/index.html` — keep both in
  sync if the rules change.
- `app/main.py` — routes are thin wrappers around `storage`/`business_rules`.
  Note the unused `LegacyTaskCreate`/`Task`/`tasks` list defined above the
  routes — dead code left from an earlier iteration, not part of the live
  request path (all endpoints use `storage`/`app/models.py` types).
- Overdue rule (backend and frontend independently implement this): a task is
  overdue when `due_date < today` (strict `<`, not `<=`) **and** `status !=
  Done`.
- CORS in `app/main.py` allows only specific hardcoded origins
  (`localhost:5500`, `127.0.0.1:5500`, `localhost:5173`, `null`) — add new
  frontend ports there if serving from elsewhere.

## Docs

`docs/` contains course-assignment artifacts documenting the AI-assisted
development process for this branch (mini-ADR, user stories, prompt log,
verification notes, reflection) — read `docs/midcourse/mini-adr.md` and
`docs/user-stories.md` for the intent behind the due-date/overdue and
search/filter features before changing that behavior.
