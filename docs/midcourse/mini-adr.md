# Mini-ADR: Optional Due Dates and Search/Filtering

## Status
Accepted for the current educational milestone. Not production-ready.

## 1. Chosen Design
Add an optional `due_date` field (Python `date`, serialized as `YYYY-MM-DD`) to
the existing `TaskCreate`, `TaskUpdate`, and `TaskResponse` models. A task is
**overdue** when `due_date` is earlier than the backend's current local date
*and* `status` is not `Done`. `GET /tasks` gains an optional `overdue: bool`
query parameter alongside a new `search: str` parameter that does a
case-insensitive substring match on `title` and `description`. All supplied
filters (`status`, `priority`, `assignee`, `overdue`, `search`) combine with
AND logic in `storage.get_all_tasks`. The frontend adds a due-date field to
the task form, an overdue badge on cards, and a search input, all using the
existing vanilla-JS render/fetch patterns already in `index.html`.

## 2. Why It Fits
Every piece slots into structures that already exist: one more optional model
field, one more filter branch in a storage function that already filters by
status and priority, one more query parameter on an existing route, and one
more form field in an existing modal. No new files, layers, or dependencies
are introduced, and in-memory storage is untouched.

## 3. Alternatives an AI Assistant Might Suggest
- Timezone-aware `datetime` for due dates instead of naive `date`.
- A dedicated `/tasks/search` or `/tasks/overdue` endpoint instead of query params.
- A generic filter/query DSL (e.g., JSON filter objects) instead of discrete params.
- An external full-text search library (e.g., Whoosh) for search.

## 4. Rejected Alternatives and Why
- **Timezone-aware datetimes**: adds complexity (client timezone handling)
  disproportionate to a course assignment; local-date comparison is simpler
  and sufficient.
- **Separate endpoints**: fragments filtering logic that already lives
  naturally in `GET /tasks`; violates "smallest change" goal.
- **Filter DSL**: over-engineered for four boolean/string filters.
- **Search library**: introduces a new dependency for a substring match that
  Python can do natively.

## 5. Limitation to Reconsider
Naive local-date "overdue" comparison ignores user timezones — if the app
ever supports multiple users in different regions, this will misclassify
tasks near the day boundary and should move to timezone-aware handling.
