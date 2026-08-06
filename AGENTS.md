# Task Tracker - Codex Instructions

## Project summary

This repository contains an educational Kanban-style task tracker developed for an AI-assisted coding course.

It has a FastAPI backend, a vanilla HTML/CSS/JavaScript frontend, and pytest coverage. Tasks are stored in an in-memory dictionary in `app/storage.py`; there is no database, and all task data is lost when the backend restarts. The frontend is served separately from the API.

This is a course project, not a production application. Authentication, authorization, persistent storage, and production deployment are not included.

## Stack

Confirmed from `requirements.txt`, `Dockerfile`, `.github/workflows/ci.yml`, and the application source:

- Python 3.11
- FastAPI
- Pydantic V2
- pytest
- Vanilla JavaScript frontend
- Uvicorn
- HTTPX for FastAPI test-client support
- In-memory Python dictionary storage

Active use of `pydantic-settings` and `python-dotenv` is not confirmed.

## Run and test commands

Run commands from the repository root.

Install dependencies:

```bash
pip install -r requirements.txt
```

Server:

```bash
uvicorn app.main:app --reload
```

The README also documents an explicit port:

```bash
uvicorn app.main:app --reload --port 8000
```

Serve the frontend separately:

```bash
python -m http.server 5500 --directory app/frontend
```

Tests:

```bash
pytest -v
```

CI-equivalent test command:

```bash
python -m pytest -v --tb=short
```

Standalone validation script:

```bash
python tests/verify_a.py
```

`tests/verify_a.py` is not part of the pytest suite.

Supported lint, formatter, and static type-check commands are not confirmed.

## Project rules

### API and architecture

- Preserve existing API endpoints and response shapes unless explicitly asked to change them.
- FastAPI does not serve `app/frontend/index.html`; the frontend and backend run separately.
- Task persistence is an in-memory dictionary in `app/storage.py`.
- Do not add authentication or a database in Module 5 unless explicitly requested and approved.
- Do not treat the unused legacy task classes and list in `app/main.py` as the active task implementation.
- Missing task IDs return HTTP 404 for retrieve, update, and delete operations.
- Successful deletion returns HTTP 204 with no response body.
- A PATCH changes only explicitly supplied fields.
- An empty PATCH body is a successful no-op and does not update `updated_at`.
- Unknown request fields are rejected with HTTP 422.

### Task values and defaults

Status values are case-sensitive:

- `ToDo`
- `InProgress`
- `Done`

Priority values are case-sensitive:

- `Low`
- `Medium`
- `High`

Task defaults are:

- Status: `ToDo`
- Priority: `Medium`
- Description: empty string
- Due date: `null`
- Assignee: `null`

The spelling `toDo` is not confirmed and conflicts with `app/models.py`, which defines the value as `ToDo`.

### Validation rules

- A title is required when creating a task.
- Leading and trailing title whitespace is removed.
- A title cannot be empty or whitespace-only.
- A title cannot exceed 200 characters after trimming.
- Invalid status, priority, and due-date values return HTTP 422.
- Unknown creation or update fields return HTTP 422.
- Due dates use `YYYY-MM-DD`.
- Supplying `description: null` stores an empty string.
- Supplying `due_date: null` in a PATCH clears the due date.

### Status transitions

Allowed transitions are:

- `ToDo` -> `InProgress`
- `InProgress` -> `ToDo`
- `InProgress` -> `Done`
- `Done` -> `InProgress`

The following are rejected with HTTP 422:

- `ToDo` -> `Done`
- `Done` -> `ToDo`
- Updating a task to its current status

The frontend duplicates these rules in `app/frontend/index.html`. Any approved status-transition change must keep the backend and frontend copies synchronized.

### Filtering rules

`GET /tasks` supports these optional filters:

- `status`
- `priority`
- `overdue`
- `assignee`
- `search`

All active filters combine using AND logic.

Search is a case-insensitive substring match against the title or description. Assignee matching is case-insensitive and exact after whitespace is trimmed. Empty or whitespace-only search and assignee filters are ignored.

A task is overdue only when:

- It has a due date.
- Its due date is strictly before the backend's current local date.
- Its status is not `Done`.

A task due today is not overdue. User-timezone-aware overdue handling is not implemented.

## Module 5 guardrails

### Docs first

Before proposing or performing work:

1. Read `README.md`.
2. Read the relevant files under `docs/`.
3. Read the implementation and tests that govern the requested behavior.
4. Base conclusions on current repository evidence.

If documentation and implementation disagree, cite both and report the discrepancy. Do not invent a resolution.

### Read-only by default

Treat inspection, explanation, review, diagnosis, and status-report requests as read-only.

Do not edit files, install packages, start persistent services, or alter Git state unless the user explicitly requests the corresponding action.

### One task per thread

Keep each Codex task/thread focused on one clearly scoped objective.

Do not expand a request into unrelated cleanup, refactoring, dependency upgrades, or feature work. Recommend a separate task for a materially different objective.

### Protect application code

Do not modify any file under `app/` unless the user explicitly approves application-code changes.

Permission to edit documentation, tests, configuration, or `AGENTS.md` does not grant permission to edit `app/`.

Before requesting approval for an `app/` change, explain:

- The observed issue.
- The supporting file evidence.
- The smallest proposed change.
- The tests that would verify it.

## Security and governance

- Do not paste, expose, log, or commit secrets, credentials, API keys, tokens, or private data.
- Do not reproduce values from `.env` or other secret-bearing files.
- Do not run destructive commands or broad delete, reset, clean, overwrite, or history-rewriting operations.
- Do not use `git reset --hard`, destructive `git clean` commands, or recursive deletion.
- Preserve unrelated user changes.
- Cite repository files for technical claims and review findings.
- Clearly distinguish confirmed facts from assumptions or recommendations.
- Mark unsupported information as `not confirmed`.
- Do not invent findings, commands, requirements, vulnerabilities, business rules, or test results.
- Do not claim tests passed unless they were actually run successfully during the current task.
- Do not commit, push, create branches, or open pull requests unless explicitly requested.
- Follow the AI-Assisted Coding - Module 5 Prompt Library governance expectations while keeping all findings grounded in repository evidence.
