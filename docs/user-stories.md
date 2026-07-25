# User Stories

## Feature 1: Due Dates and Overdue Filter

### US1.1 — Set an optional due date when creating a task

As a task owner, I want to optionally set a due date when creating a task, so
that I can track when it needs to be finished.

**Acceptance criteria**
- The due date field is optional; omitting it leaves `due_date` as `null`.
- The date must be submitted as `YYYY-MM-DD`; any other format returns `422`.
- The task's response includes `due_date` exactly as submitted.

### US1.2 — Update or clear a due date without disturbing other fields

As a task owner, I want to update or clear a task's due date independently of
its other fields, so that a date-only edit doesn't accidentally reset
anything else.

**Acceptance criteria**
- `PATCH` with a new `due_date` updates only that field; title, description,
  priority, and assignee remain unchanged.
- `PATCH` with `due_date: null` explicitly clears an existing due date.
- Omitting `due_date` from a `PATCH` body leaves the existing value untouched
  (it is not reset to `null`).

### US1.3 — See at a glance which tasks are overdue

As a user reviewing the board, I want overdue tasks to be visually obvious,
so that I can prioritize what's late without reading every due date.

**Acceptance criteria**
- A task shows an "Overdue" indicator when its `due_date` is before today
  **and** its status is not Done.
- A task shows its due date on the card when one is set.
- A task with a past due date but status Done does **not** show as overdue.
- A task with a due date of exactly today does **not** show as overdue.

### US1.4 — Filter the board to overdue or non-overdue tasks

As a user, I want to filter the task list to only overdue (or only
not-overdue) tasks, so that I can focus on what needs attention right now.

**Acceptance criteria**
- `GET /tasks?overdue=true` returns only tasks matching the overdue rule
  above.
- `GET /tasks?overdue=false` returns only tasks that don't match it.
- Omitting the `overdue` parameter returns tasks regardless of due date
  (existing behavior preserved).
- A filter combination that matches nothing returns `HTTP 200` with `[]`.

**AI assumption corrected:** When the due-date modal field was first wired
up, the AI carried over the existing pattern of resending every form field
(including the task's current, unchanged `status`) on every edit — an
assumption inherited from the pre-existing code, not questioned at the time.
This broke in practice: a user could not save a due-date-only edit because
the backend's status-transition rule rejects a "transition" to the same
status, so *any* edit 422'd unless the status dropdown was also changed. The
bug report ("I am not able to update the task to add the due date") corrected
this assumption — the fix now omits `status` from the `PATCH` body whenever
it hasn't actually changed.

---

## Feature 2: Text Search and Combined Filters

### US2.1 — Search tasks by keyword

As a user, I want to type a keyword and have the board show only matching
tasks, so that I can find something quickly without scrolling the whole
board.

**Acceptance criteria**
- `GET /tasks?search=<term>` matches a partial, case-insensitive substring in
  either the title or the description.
- Leading/trailing whitespace in the search term is ignored.
- An empty or whitespace-only search behaves exactly as if `search` were not
  provided at all.

### US2.2 — Filter tasks by assignee

As a user, I want to filter the board down to a specific assignee's tasks, so
that I can see just what's on my plate (or a teammate's).

**Acceptance criteria**
- `GET /tasks?assignee=<name>` matches case-insensitively after trimming
  whitespace from both the query value and the stored assignee.
- A task with no assignee never matches a non-empty assignee filter.
- An empty or whitespace-only assignee value behaves as if the filter were
  not provided.

### US2.3 — Combine multiple filters at once

As a user, I want to combine search, priority, assignee, and overdue filters
together, so that I can ask precise questions like "high-priority tasks
assigned to Ruba that are overdue."

**Acceptance criteria**
- All supplied filters combine using AND logic — a task must satisfy every
  active filter to be included.
- A filter combination that matches nothing returns `HTTP 200` with `[]`,
  not an error.
- Supplying an invalid value for `status` or `priority` (which are enum-typed)
  returns `422`.

### US2.4 — Use a compact filter bar without losing the board layout

As a user, I want a single filter bar above the board so I can search and
filter without leaving the main view, and I want the three Kanban columns to
stay put even when a filter matches nothing.

**Acceptance criteria**
- Search input, priority selector, assignee input, and overdue selector all
  appear together in one toolbar above the board.
- Changing any filter reloads the task list through the existing
  `GET /tasks` endpoint — no new endpoint is introduced.
- A "Clear Filters" action resets every filter control and reloads the full,
  unfiltered list.
- All three columns (ToDo / InProgress / Done) remain visible with their
  existing per-column empty state when a filter returns no matches for that
  column — columns are never hidden based on filter results.

### US2.5 — Get live search results without extra clicks

As a user typing a search term, I want the results to update shortly after I
stop typing, so that I don't need a separate "Search" button.

**Acceptance criteria**
- Typing in the search box triggers a reload roughly 300ms after the last
  keystroke (debounced), not on every keystroke.
- No dedicated Search button exists or is required to see results.
- Selecting priority, assignee (on blur/Enter), or overdue still reloads
  immediately on change, without a debounce delay.

**AI assumption corrected:** When asked to "extend `GET /tasks`" with search
and assignee support, the AI's first pass only produced a text diff and
stopped there, implicitly assuming that showing a diff satisfied the request.
It had not actually been written to `app/main.py` or `app/storage.py`. The
question "you added the apis in the project?" corrected this assumption —
the AI now applies the change to the real files and verifies it (tests,
live `curl` checks) rather than treating a displayed diff as done.
