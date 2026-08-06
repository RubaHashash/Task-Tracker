# Task Tracker Architecture

## 1. What the app does

The application exposes a FastAPI JSON API for creating, listing, retrieving, partially updating, and deleting tasks. Tasks can be filtered by status, priority, overdue state, assignee, and text search. The API also provides a basic health-check endpoint.

## 2. Data model

The main entity is `TaskResponse`, containing:

- `id`: UUID-formatted string
- `title`: required, trimmed, nonblank, maximum 200 characters
- `description`: string
- `due_date`: optional date
- `status`: `ToDo`, `InProgress`, or `Done`
- `priority`: `Low`, `Medium`, or `High`
- `assignee`: optional string
- `created_at`, `updated_at`: UTC datetimes

`TaskCreate` supplies defaults of an empty description, no due date, `ToDo` status, `Medium` priority, and no assignee. `TaskUpdate` makes every field optional for partial updates.

## 3. Request flow

When a client sends `POST /tasks`, FastAPI parses the body as `TaskCreate`. Pydantic rejects unknown fields and validates and trims the title. The endpoint passes the validated model to `storage.add_task`, which generates a UUID, normalizes a missing description to an empty string, assigns equal UTC creation and update timestamps, constructs a `TaskResponse`, and stores it in the module-level `_tasks` dictionary. The API returns the stored task with HTTP 201.

## 4. Key files

- `app/main.py` — Configures FastAPI and CORS and defines health-check and task CRUD endpoints.
- `app/models.py` — Defines task status and priority enums plus create, update, and response models.
- `app/storage.py` — Implements in-memory task creation, querying, updating, deletion, and reset.
- `app/business_rules.py` — Provides status-transition validation; its implementation is **not visible from the files I read**.
- Frontend entry file — **not visible from the files I read**.
- Test files — **not visible from the files I read**.

## 5. Conventions

- **Validation:** Pydantic models forbid unknown request fields. Titles are trimmed, must not be blank, and may contain at most 200 characters. Enums constrain status and priority; date parsing follows the model’s date type.
- **Storage:** Tasks live in an in-process dictionary keyed by string UUID. Results retain insertion order. Restart persistence and concurrency behavior are **not visible from the files I read**.
- **Updates:** PATCH applies only explicitly supplied fields. An empty update is a no-op and preserves `updated_at`; applied changes receive a new UTC timestamp. A null description is stored as an empty string.
- **Errors:** Missing task IDs produce HTTP 404. Invalid request models produce validation errors; exact framework-generated response bodies are **not visible from the files I read**. Status-transition errors are delegated to `app/business_rules.py`.
- **Frontend/backend interaction:** CORS permits origins on local ports 5500 and 5173, plus a `null` origin, with all methods and headers. How the frontend calls or renders the API is **not visible from the files I read**.

## 6. Not visible or assumptions

Authentication, authorization, database use, deployment, frontend implementation, API tests, complete status-transition rules, configuration, dependency versions, and whether the legacy task classes in `app/main.py` are used elsewhere are **not visible from the files I read**.

## Files read

- `app/main.py`
- `app/models.py`
- `app/storage.py`

All three listed files existed; no substitution was needed.

## Items marked not visible

- Implementation of `app/business_rules.py`
- Frontend entry file and behavior
- Test files and coverage
- Restart persistence and concurrency behavior
- Exact framework-generated validation response bodies
- Authentication and authorization
- Database use
- Deployment and configuration
- Dependency versions
- Complete status-transition rules
- Use of the legacy task classes outside `app/main.py`

## What this targeted strategy likely missed

This strategy likely missed the implemented status-transition policy, frontend behavior, tests, documented operating assumptions, dependency configuration, and any discrepancies among documentation, implementation, and tests. No claims about those areas were inferred.

