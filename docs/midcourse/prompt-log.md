# Prompt Log

## Feature 0: Codebase Review

### Prompt F0-P1: Implementation map

#### Prompt purpose

Understand the existing FastAPI + vanilla JS Task Tracker before proposing any
changes, and scope the smallest files that would need to change for due dates
and text search.

#### Prompt

```
Role / Context:
You are a senior FastAPI and vanilla JavaScript developer reviewing an existing
Task Tracker created during an AI-assisted coding course.
...
Task:
Inspect only the attached files and explain the current implementation before
suggesting changes.

For each relevant file, identify:
1. Existing task fields.
2. Existing Pydantic create, update, and response models.
3. Existing storage helper functions.
4. Current GET /tasks filtering behavior.
5. Current frontend form fields.
6. The functions that render task cards.
7. The frontend functions that fetch, create, and update tasks.
8. Current automated test structure.

Constraints:
- Do not edit or generate code yet.
- Do not invent files, helpers, routes, fields, or libraries.
- If something is not present, say "not present."
- Preserve the current architecture.
- Do not suggest a database, authentication, framework migration, or new
  frontend library.

Output format:
Return a structured implementation map followed by a short list of the smallest
files that would need to change for:
A. optional due dates and an overdue filter;
B. text search and combined filters.
```

#### AI response summary

Produced a full field-by-field map of `app/models.py`, `app/storage.py`,
`app/main.py`, `app/business_rules.py`, `tests/`, and the frontend (found at
`app/frontend/index.html`, not `frontend/index.html` as stated). Identified a
vestigial `LegacyTaskCreate`/`Task` block in `main.py` as dead code, and listed
the smallest files to touch for due dates (models, storage, main, frontend)
and for search (storage, main, frontend).

#### Accepted

- Full implementation map used as the shared reference for all later work.
- File-path correction (`app/frontend/index.html`) carried forward.

#### Edited

- None — pure analysis, no code produced at this stage.

#### Rejected

- None.

#### Verification

- Manual read-through of the listed files against the summary; no automated
  checks applicable (no code changed).

---

## Feature 1: Due Dates and Overdue Filter

### Prompt F1-P1: Mini-ADR

#### Prompt purpose

Record the design decision for due dates + overdue filtering as a short
architecture decision record before implementing it.

#### Prompt

```
Role / Context:
You are a senior software developer helping me write a concise architecture
decision record for an educational FastAPI Task Tracker.
...
Chosen decisions:
- due_date is an optional Python date represented in JSON as YYYY-MM-DD.
- A task is overdue when due_date is earlier than the backend's current local
  date and status is not Done.
- GET /tasks accepts an optional overdue boolean query parameter.
- Search is case-insensitive and checks title and description.
- All supplied filters use AND logic.
- Existing in-memory storage and architecture remain unchanged.
- The frontend uses existing vanilla JavaScript patterns.
- No database, timezone-aware datetime, notification system, recurring tasks,
  React migration, or external search library will be added.

Task:
Write a short mini-ADR explaining:
1. The chosen design.
2. Why it fits the current architecture.
3. Alternatives an AI assistant might reasonably suggest.
4. Which alternatives were rejected and why.
5. One limitation to reconsider if the project grows.
```

#### AI response summary

Wrote `docs/midcourse/mini-adr.md` (~340 words) covering the chosen design,
why it fits the existing architecture, alternatives an AI might suggest
(timezone-aware datetimes, separate endpoints, a filter DSL, an external
search library), why each was rejected, and flagged naive local-date overdue
comparison as the limitation to revisit if the project supports multiple
timezones.

#### Accepted

- All five sections as drafted, written directly to `docs/midcourse/mini-adr.md`.

#### Edited

- None.

#### Rejected

- None.

#### Verification

- Manual read-through only; this is a documentation artifact, no code to test.

---

### Prompt F1-P2: Model and storage changes

#### Prompt purpose

Add `due_date` to the Pydantic models and the in-memory storage flow.

#### Prompt

```
Role / Context:
You are a senior FastAPI developer making a small change to an existing Task
Tracker.
...
Task:
Add optional due-date support to the task models and existing in-memory storage
flow.

Requirements:
- Add `due_date` as an optional Python `date`.
- TaskCreate should accept it and default it to None.
- TaskUpdate should allow it to be omitted for no change.
- TaskUpdate should also allow explicit null to clear an existing due date.
- TaskResponse should include it.
- JSON input uses the standard ISO date format YYYY-MM-DD.
- Invalid dates must be rejected by Pydantic with HTTP 422 when used through the
  API.
- Existing storage helpers must continue to work.
- Unrelated partial updates must preserve the current due date.

Constraints:
- Use Pydantic v2 syntax only.
- Do not add a database.
- Do not add datetime or timezone handling.
- Do not add an `is_overdue` stored field.
- Do not rename existing models, enums, fields, or helper functions.
- Do not rewrite unrelated code.
- Do not modify app/main.py or frontend files in this step.
- Do not add try/except blocks that hide Pydantic validation errors.
```

#### AI response summary

Proposed adding `due_date: date | None` to `TaskCreate`, `TaskUpdate`, and
`TaskResponse`, and passing `due_date=payload.due_date` through in
`storage.add_task`. Relied on the existing `model_dump(exclude_unset=True)` +
`model_copy(update=changes)` pattern in `storage.update_task` to handle
omit-vs-null semantics automatically, without any new special-casing.

#### Accepted

- Python `date` type (no datetime/timezone handling).
- ISO `YYYY-MM-DD` serialization via Pydantic's native `date` support.
- Optional field on create, update, and response models, no renames.

#### Edited

- None beyond the initial proposal — the `exclude_unset=True` behavior already
  in `storage.update_task` gave "omit = no change" and "explicit null = clear"
  for free, so no extra logic was written or needed.

#### Rejected

- Rejected a stored `is_overdue` field — overdue-ness is derived from
  `due_date` + `status` + "today," and storing it would let it go stale.

#### Verification

- Initially only a diff was shown (not applied) per the requested output
  format.
- Later applied directly and confirmed via `pytest`: all 23 existing tests
  passed unchanged.

---

### Prompt F1-P3: Backend overdue query filter

#### Prompt purpose

Add an `overdue` boolean query parameter to `GET /tasks`.

#### Prompt

```
Role / Context:
You are a senior FastAPI developer extending an existing GET /tasks route.
...
Business rule:
A task is overdue when:
- due_date is not None;
- due_date is earlier than `date.today()`;
- status is not TaskStatus.Done.

Requirements:
- `GET /tasks?overdue=true` returns only overdue tasks.
- `GET /tasks?overdue=false` returns only tasks that are not overdue.
- Omitting `overdue` preserves the current behavior.
- Existing status and priority filters must continue working.
- When multiple filters are provided, apply AND logic.
- No matches return HTTP 200 with [].

Constraints:
- Use the existing FastAPI app and storage helpers.
- Do not create a new FastAPI instance.
- Do not store an is_overdue field.
- Do not change status-transition rules.
- Do not modify frontend files yet.
- Do not rename existing route functions or helpers unless strictly necessary.
- Make the smallest focused change.
- Preserve Pydantic v2 patterns.
```

#### AI response summary

Added `overdue: bool | None = None` to `storage.get_all_tasks` and
`main.list_tasks`, computing `date.today()` once per call and filtering
in-memory — no stored derived field, no new route, filters applied as
sequential AND stages consistent with the existing `status`/`priority`
filtering style.

#### Accepted

- Sequential AND-filter design (status → priority → overdue), matching the
  existing code's style exactly.
- `overdue` computed on the fly from `due_date`/`status`/`date.today()`.

#### Edited

- None — the diff was accepted as proposed.

#### Rejected

- None.

#### Verification

- Diff shown but not yet applied to disk in this turn (per output format).
- Applied directly afterward and curl-verified against a running `uvicorn`
  instance.

---

### Prompt F1-P4: Frontend due-date modal, card display, and filter

#### Prompt purpose

Wire the already-built backend due-date/overdue support into the Kanban
frontend: the create/edit modal, the task cards, and a filter control.

#### Prompt

```
for the backend:
Add optional due_date validation. Support create/update. Decide whether overdue
is computed in the backend or UI. Optional query filter for overdue

for the frontend:
Add due date to the modal. Show due date or overdue pill on cards. Add an
overdue filter or visual indicator.
```

#### AI response summary

Confirmed the backend requirements were already satisfied (validation via
Pydantic's `date` type, overdue computed in the backend not stored, query
filter already wired). Added a due-date `<input type="date">` to the
create/edit modal (populate/reset/payload/error-mapping), a due-date chip +
red "Overdue" pill on task cards (`isTaskOverdue()` mirroring the backend
rule), and an "Overdue only" checkbox in the header wired to
`GET /tasks?overdue=true`.

#### Accepted

- Modal field, card chip/pill, and checkbox filter as designed.
- Client-side `isTaskOverdue()` computed from the task's own `due_date`/
  `status` fields rather than an extra request per card.

#### Edited

- None in this turn — proposal matched what was implemented.

#### Rejected

- None.

#### Verification

- `pytest -q` → 23 passed (backend untouched this turn).
- Explicitly noted the limitation that no browser was actually driven this
  turn (no headless-browser tool available); manual visual verification
  happened later once the app was launched and used directly, including a
  live curl smoke test of create-with-due-date and the `overdue=true` filter.

---

### Prompt F1-P5: Bug report — can't add a due date via edit

#### Prompt purpose

Fix a real bug the user hit while using the running app.

#### Prompt

```
I am not able to update the task to add the due date
```

#### AI response summary

Reproduced the exact PATCH payload the edit modal sends against the live
backend and got `422 Invalid status transition from ToDo to ToDo`. Root
cause: the edit modal always resent the task's current, unchanged `status`
in every PATCH body, and `business_rules.py`'s transition rule intentionally
rejects a status "transition" to itself (`test_patch_same_status_returns_422`
already encodes this as desired backend behavior) — so _any_ modal edit
(not just due dates) 422'd unless the user also changed the status dropdown.

#### Accepted

- Frontend-only fix: remember the task's status when the edit modal opens
  (`editingTaskStatus`), and omit `status` from the PATCH body in
  `submitTaskForm` when it's unchanged, letting the backend's existing
  partial-update (`exclude_unset`) logic leave it alone.

#### Edited

- None — the fix was verified correct on the first pass via direct curl
  reproduction before and after.

#### Rejected

- Did not touch `business_rules.py` or weaken the same-status rejection rule
  — that behavior is intentional and tested; the bug was entirely in what
  the frontend chose to send, not in the rule itself.

#### Verification

- Replayed the exact fixed payload (status omitted) against the live
  backend → `200`, `due_date` updated, status untouched.
- Re-tested a genuine valid transition (`InProgress → Done`) → `200`.
- Re-tested a genuine invalid transition (`Done → ToDo`) → still `422` as
  expected.
- `pytest -q` → 23 passed (backend untouched).

---

### Prompt F1-P6: Modernize the task card

#### Prompt purpose

Improve the task card's visual layout/hierarchy.

#### Prompt

```
arrange the card of the task to be moderized
```

#### Weak prompt → stronger rewrite

This prompt is a good example of a weak one: it has a typo ("moderized"),
gives no file reference, and "modernize" is ambiguous against a board that
already uses gradients, shadows, and dark mode — modernize *what*, exactly
(colors? layout? new affordances)? Because of that ambiguity, the AI had to
stop and ask a clarifying question before writing any code, instead of
acting on the request directly.

A stronger version of the same intent, written up front, would have been:

```
Role / Context:
You are a senior vanilla JavaScript developer refining the visual hierarchy of
an existing Kanban task card.

Attached file:
- app/frontend/index.html (renderTaskCard function and its CSS)

Current card layout:
Title, then description, then one flat wrapped row containing the priority
badge, overdue pill, due-date chip, and assignee chip, then an Edit button
right-aligned below.

Task:
Reorganize the existing card's markup and CSS into a clearer visual
hierarchy: group the title with the priority badge, group the due-date/
overdue signals together, and group the assignee with the Edit action.
Same information as today, just regrouped — no new fields.

Constraints:
- Do not add new task fields or change any backend code.
- Do not add a frontend framework or icon library.
- Preserve existing functionality: drag-and-drop, the Edit button, and the
  overdue/priority computation logic.

Output format:
1. Show the new card markup structure.
2. Show the CSS changes.
```

Sending this version first would have skipped the clarifying-question round
trip entirely — it names the exact file/function, describes the current
layout concretely, and states which elements should be grouped, which is
exactly what the AI ended up building anyway after the back-and-forth.

#### AI response summary

Asked a clarifying question first, since "modernize" was ambiguous against an
already-modern-looking board (gradients, shadows, dark mode). User picked
"reorganize layout/hierarchy." Restructured the card into three tiers: a top
row (title + priority badge together), a status row (Overdue pill + due-date
chip with a small inline SVG calendar icon, only rendered when relevant), and
a footer row (assignee left, Edit button right, `space-between`).

#### Accepted

- The three-tier reorganization as designed and implemented directly.
- Inline hand-authored SVG icon instead of an icon font/library (keeps the
  "no new frontend library" constraint intact).

#### Edited

- None — implemented in one pass after the clarifying question.

#### Rejected

- None (no alternative layout was proposed and turned down; the clarifying
  question narrowed scope before any code was written).

#### Verification

- Grepped the file to confirm no leftover references to the old `.task-meta`
  class.
- Confirmed via `curl` that the static server was serving the new markup
  (`task-card-top`, `task-status-row` present in the HTML response).

---

### Prompt F1-P7: Propose and add due-date/overdue pytest tests

#### Prompt purpose

Get focused test proposals for the due-date and overdue behavior, then turn
them into real, running tests.

#### Prompt

```
Role / Context:
You are a senior Python test engineer adding focused tests to an existing
FastAPI pytest suite.
...
Required tests:
1. Create a task with a valid due date and return it in the response.
2. Reject an invalid due-date format with HTTP 422.
3. Update an existing task's due date.
4. Preserve due_date after an unrelated partial update.
5. Clear due_date by sending null.
6. `overdue=true` returns an overdue ToDo task.
7. A Done task with a past date is not considered overdue.
8. `overdue=false` excludes overdue tasks.

Constraints:
- Follow the existing fixture and client style.
- Do not replace or weaken existing tests.
- Do not use fixed dates that may become invalid depending on when tests run.
- Use date.today() with timedelta to create past and future values.
- Assert status codes and response bodies.
- Keep each test focused on one behavior.
- Do not modify production code in this response.
```

(Sent twice, verbatim, in separate turns — the second run asked for the same
proposal again before a follow-up "add the tests to the test tasks" request
actually wrote them to the file.)

#### AI response summary

Proposed 8 required tests plus one recommended "break test"
(`test_list_tasks_due_today_is_not_overdue`, targeting the `<` vs `<=`
boundary), all using `date.today() + timedelta(...)` instead of fixed dates,
each mapped to the specific production bug it would catch. Once asked to add
them, appended all 9 verbatim to `tests/test_tasks.py`. A later prompt asked
to confirm five specific behaviors (valid due date, invalid format, overdue
detection, update due date, overdue-only filter) were covered; each mapped
cleanly to one of the 9 tests.

#### Accepted

- All 9 tests (8 required + the boundary break test), unchanged.
- The behavior-to-test mapping as given; no gaps found.

#### Edited

- None.

#### Rejected

- None.

#### Verification

- `pytest -v` → 32 passed (23 original + 9 new), and reconfirmed again on a
  later plain "run the tests" request.

---

## Feature 2: Text Search and Combined Filtering

### Prompt F2-P1: Backend search + assignee filter design

#### Prompt purpose

Design and (eventually) implement case-insensitive text search and an
assignee filter on `GET /tasks`, combined with the existing filters.

#### Prompt

```
Role / Context:
You are a senior FastAPI developer extending the existing GET /tasks endpoint
of a Task Tracker.
...
Requirements:
- Add an optional query parameter named `search`.
- Search must match partial text in task title or description.
- Search must be case-insensitive.
- Leading and trailing whitespace in the search query must be ignored.
- An empty or whitespace-only search value should behave as though search was
  not provided.
- Preserve existing status, priority, and overdue filters.
- Add an optional assignee filter if the current endpoint does not already have
  one.
- Assignee filtering should be case-insensitive exact matching after trimming.
- When several filters are supplied, all conditions use AND logic.
- No matches return HTTP 200 with [].
- Existing task order must remain unchanged unless the project already defines
  sorting.

Constraints:
- Use the existing route and storage architecture.
- Do not add a database, full-text search engine, pagination, saved views, or
  new dependency.
- Do not create new routes.
- Do not move filtering to the frontend.
- Do not change existing response models.
- Do not weaken enum validation for status or priority.
- Make the smallest focused change.
```

#### AI response summary

Proposed adding `assignee: str | None` and `search: str | None` to
`storage.get_all_tasks` and `main.list_tasks`, normalizing both by
`.strip().lower()`, applied as two more sequential AND-filter stages after
the existing status/priority/overdue filters — `search` matching title OR
description substrings, `assignee` requiring an exact normalized match.
Flagged assumptions needing approval (empty-assignee-as-not-provided,
`.lower()` vs `.casefold()`, search-is-OR-not-AND-across-fields).

#### Accepted

- The filter design and normalization rules exactly as proposed, once applied
  (see F2-P2).
- All flagged assumptions were implicitly accepted (no pushback given).

#### Edited

- None beyond what was proposed.

#### Rejected

- None.

#### Verification

- Diff shown but not applied to disk in this turn, per the requested output
  format (pseudocode + diff + curl commands + assumptions only).

---

### Prompt F2-P2: Confirm and apply

#### Prompt purpose

Catch that the previous turn's diff was only proposed, not applied, and get
it onto disk.

#### Prompt

```
you added the apis in the project?
```

#### AI response summary

Grepped `app/main.py`/`app/storage.py` for `search`/`assignee`, found neither
present, and reported the diff had not been applied. Asked for confirmation,
then applied both edits.

#### Accepted

- Applying the exact diff from F2-P1 with no changes.

#### Edited

- None.

#### Rejected

- None.

#### Verification

- `pytest -q` → 32 passed.
- Live backend (already running with `--reload`) picked up the change
  automatically; confirmed via `/openapi.json` parameter list and live
  `curl` calls: case-insensitive `search=REPORT` match, trimmed
  case-insensitive `assignee` match, and a no-match query returning `[]`.

---

### Prompt F2-P3: Frontend filter/search toolbar

#### Prompt purpose

Expose search, priority, assignee, and the existing overdue filter as a
compact toolbar above the Kanban board.

#### Prompt

```
Role / Context:
You are a senior vanilla JavaScript developer extending an existing Task
Tracker Kanban board.
...
Requirements:
- Add a text search input.
- Add a priority selector with All, High, Medium, and Low.
- Add an assignee input or selector consistent with the existing UI.
- Preserve the existing overdue filter.
- Keep all three Kanban columns visible even when filters are active.
- Build the GET /tasks query string using URLSearchParams.
- Omit empty filter values from the request.
- Trim search and assignee values.
- Reload tasks when a selector changes.
- For the search input, use either an explicit Search button or a small debounce;
  choose the simpler approach for this project and explain the decision.
- Add a Clear Filters action.
- No results should preserve all columns and show their existing empty states.
- Preserve drag-and-drop, create/edit, loading, error handling, and status strings.

Constraints:
- Do not rewrite the full file.
- Do not add frameworks or external libraries.
- Do not hide columns based on the status filter.
- Do not perform a second independent client-side filtering pass.
- Do not change API paths or methods.
- Do not remove existing error handling.
- Keep the implementation readable and small.
```

#### AI response summary

Relocated the existing overdue `<select>` into a new `.filter-toolbar`
section (search input, priority select, assignee input, overdue select,
Clear Filters button) between the header and the board. Added
`buildTasksQuery()` using `URLSearchParams`, omitting empty values. Chose a
300ms debounce on `input` for search (fewer DOM elements for a "compact"
toolbar, standard live-search UX) and a `change`-event reload for assignee
(exact-match filter, so per-keystroke requests would mostly return nothing
useful).

#### Accepted

- Debounced search vs. `change`-triggered assignee/priority/overdue, with the
  reasoning given.
- Relocating (not duplicating) the overdue control into the new toolbar.

#### Edited

- None — implemented as planned in one pass.

#### Rejected

- An explicit Search button was considered and rejected in favor of the
  debounce, for the stated compactness/consistency reasons.

#### Verification

- Grepped for leftover `initOverdueFilter`/old markup references — none
  found.
- Confirmed live via `curl` against the static server that all five toolbar
  control IDs were present in the served HTML.
- Provided (and later manually walked through) a verification checklist:
  per-filter reload behavior, AND-combination, Clear Filters, no-match empty
  states per column, and drag-and-drop/modal regressions.

---

### Prompt F2-P4: Add tests for search and combined filters

#### Prompt purpose

Cover the new search/assignee/combined-filter behavior with pytest, after
confirming no such tests existed yet.

#### Prompt

```
did you add tests for the search ?
Search title/description, combine status + priority, no matches returns 200
with [], invalid filter value returns 422 if backend validates it.
```

#### AI response summary

Grepped `tests/test_tasks.py` for "search", found nothing, and added 6 new
tests: search-matches-title, search-matches-description, combined
status+priority AND filter, search-no-matches-returns-empty-list, and two
invalid-enum-filter 422 tests (`status`, `priority` — the only two filters
with enum validation; `search`/`assignee` are plain strings with no invalid
form to test).

#### Accepted

- All 6 tests as written, appended to the end of the file.

#### Edited

- None.

#### Rejected

- None (an invalid-`search`/`assignee`-value test wasn't added, since
  explained: those params are unvalidated strings with no way to be
  "invalid").

#### Verification

- `pytest -v` → 38 passed (32 previous + 6 new).

---

### Prompt F2-P5: Refactor filter-state and query-building code

#### Prompt purpose

Reduce duplication in the frontend's filter-state/query-construction code
without changing behavior.

#### Prompt

```
Role / Context:
You are a senior vanilla JavaScript developer reviewing one selected section
of an existing Task Tracker frontend.
...
Task:
Refactor only the selected filter-state and query-construction section to
reduce duplication and improve readability.

Constraints:
- Preserve behavior exactly.
- Do not modify unrelated rendering, modal, drag-and-drop, or CSS code.
- Do not change selectors, API paths, parameter names, status values, or HTTP
  methods.
- Do not add a library.
- Do not rewrite the full file.
- Keep the solution understandable to an intermediate developer.
- Explain every behavior-sensitive line changed.
```

#### AI response summary

Identified the duplication: four near-identical `if (value) { params.set(...) }`
blocks in `buildTasksQuery()`, and an undocumented trim/no-trim asymmetry
between text filters and select filters. Collapsed the four blocks into a
single `filterParams` object plus one loop over `Object.entries(...)`,
preserving exact param names, trim behavior, and param order. Deliberately
left the four separate `let` filter variables and `initFilterToolbar()`
untouched, since consolidating them would ripple into event-wiring code
outside the selected scope.

#### Accepted

- The `filterParams` object + loop refactor of `buildTasksQuery()` only.
- The explicit decision _not_ to also merge the `let` filter-state variables
  into an object, to avoid touching out-of-scope wiring code.

#### Edited

- None — applied as proposed in one pass.

#### Rejected

- A broader refactor that would have merged all filter state into a single
  object (and touched `initFilterToolbar()`'s listeners/Clear-Filters
  handler) — rejected as out of scope for "filter-state and query-building
  functions only," and as unnecessary risk for a purely cosmetic gain.

#### Verification

- Confirmed via `curl` against the live static server that the refactored
  function was being served correctly.
- `pytest -v` → 38 passed (frontend-only change, backend suite unaffected).
