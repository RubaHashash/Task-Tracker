# Verification

This documents how the Mid-Course features (due dates/overdue filter, and
text search/combined filters) were actually verified, not just implemented.
Where evidence is a claim rather than something re-run for this document, it
is marked as such.

## Baseline check

Before Feature 1 (due dates) and Feature 2 (search/filters) work began
(`docs/midcourse/prompt-log.md`, F0-P1):

- `GET /tasks` supported only `status` and `priority` filters.
- No `due_date` field existed on any model; no `overdue`, `assignee`, or
  `search` query parameters existed.
- The frontend Kanban board had create/edit, drag-and-drop, and loading/
  empty/ready/error states, but no due-date UI and no filter toolbar.
- `tests/test_tasks.py` had **23 tests**, all passing, covering create,
  list+status/priority filters, get-by-id, patch (including status
  transitions), and delete.

This is the "before" state that every later diff and test addition is
measured against.

## Backend test results

Full-suite `pytest` counts at each milestone, re-run for this document where
noted:

| Point in the work | Count | Notes |
|---|---|---|
| Baseline (before Feature 1/2) | 23 passed | Pre-existing suite |
| After adding `due_date`/`overdue` tests (Feature 1) | 32 passed | +9 (8 required + 1 boundary break test) |
| After adding `search`/combined-filter tests (Feature 2) | 38 passed | +6 |
| Re-run for this document | **38 passed in 0.51s** | See below |

Re-run just now, current state:

```
$ .\venv\Scripts\python.exe -m pytest -q
......................................                                   [100%]
38 passed in 0.51s
```

## Manual browser checks

No headless-browser automation (Playwright/`chromium-cli`) was available in
this environment, so "manual browser checks" here means: the app was
actually launched (`uvicorn` on `:8000`, a static file server on `:5500` for
`app/frontend/index.html`), backend behavior was smoke-tested via `curl`/
`Invoke-RestMethod` against the live server, and the real browser was opened
via `Start-Process` for the user to interact with directly — this runs on
the user's actual Windows desktop, not a container, so it is a real browser,
not a simulated one.

What's actually confirmed vs. what's a checklist handed off:

- **Confirmed via live backend calls** (curl/`Invoke-RestMethod` against a
  running server, not mocked): creating a task with `due_date`, the
  `overdue=true`/`overdue=false` filter, the `search`/`assignee` filters
  (case-insensitive, trimmed), combined filters, and the `PATCH` fix for the
  same-status bug (before-and-after payload replay).
- **Confirmed via a real user interaction, not a script**: the due-date edit
  bug itself. The user tried to add a due date through the real UI and it
  failed — that's a genuine manual browser check that caught a real defect
  (F1-P5 in the prompt log), not a hypothetical one.
- **Provided as a checklist, not confirmed back in this conversation**: the
  full modal/card/toolbar walkthroughs given after the due-date frontend
  work (F1-P4) and the filter toolbar work (F2-P3) — e.g., visually
  confirming the due-date chip and Overdue pill render correctly, the
  toolbar's five controls behave as described, Clear Filters resets the UI,
  and per-column empty states show correctly with no matches. These
  checklists were handed to the user to run themselves; there is no message
  in this conversation confirming each item was walked through and passed.
  This is a real gap between "the backend proves the data is correct" and
  "a human confirmed the pixels are correct" — flagged here rather than
  claimed as done.

## Behavior contract before/after refactor

The one refactor in this project's history is the `buildTasksQuery()` dedup
in `app/frontend/index.html` (prompt-log F2-P5), which collapsed four
near-identical `if (value) { params.set(...) }` blocks into one loop.

**Before:**
```js
const params = new URLSearchParams();
const trimmedSearch = searchFilter.trim();
const trimmedAssignee = assigneeFilter.trim();

if (trimmedSearch) { params.set("search", trimmedSearch); }
if (priorityFilter) { params.set("priority", priorityFilter); }
if (trimmedAssignee) { params.set("assignee", trimmedAssignee); }
if (overdueFilter) { params.set("overdue", overdueFilter); }

const query = params.toString();
return query ? `?${query}` : "";
```

**After:**
```js
const filterParams = {
    search: searchFilter.trim(),
    priority: priorityFilter,
    assignee: assigneeFilter.trim(),
    overdue: overdueFilter
};

const params = new URLSearchParams();
for (const [name, value] of Object.entries(filterParams)) {
    if (value) {
        params.set(name, value);
    }
}

const query = params.toString();
return query ? `?${query}` : "";
```

**Contract preserved, mapped explicitly:**

| Contract item | Before | After | Why unchanged |
|---|---|---|---|
| AND logic across filters | Each filter set independently | Same | Loop still calls `params.set` per filter independently; combination logic lives in the backend, untouched either way |
| Empty values omitted | `if (value)` guard per block | `if (value)` guard in the loop | Identical guard, same falsy-string check |
| Trim on `search`/`assignee` only | `.trim()` called on those two only | Same two fields `.trim()`'d in the object literal | `priority`/`overdue` come from `<select>`s and were never trimmed before or after |
| Param names sent to API | `"search"`, `"priority"`, `"assignee"`, `"overdue"` | Same four strings, now as object keys | No renames |
| Param order in query string | search, priority, assignee, overdue | Same order (`Object.entries` preserves insertion order) | Byte-identical query string shape for the same inputs |
| Return value shape | `""` or `"?..."` | Identical last two lines, untouched | Not touched by the diff |

Verified by: `pytest -q` → 38 passed (backend untouched, as expected for a
frontend-only diff), plus a live `curl` check that the static server was
serving the refactored function.

## Break Test evidence (≥2 tests)

Evidence here means the test was proven to actually fail when the bug it
targets is reintroduced, not just asserted to be a good idea. Two tests were
re-verified this way, live, for this document: the mutation was applied,
the specific test was run and shown to fail, then the mutation was reverted
and the full suite re-confirmed green.

### 1. `test_list_tasks_due_today_is_not_overdue` — boundary (`<` vs `<=`)

Targets the exact overdue boundary: a task due *today* must not count as
overdue. Mutated `app/storage.py`'s comparison from `due_date < today` to
`due_date <= today`:

```
$ pytest tests/test_tasks.py::test_list_tasks_due_today_is_not_overdue -v
FAILED tests/test_tasks.py::test_list_tasks_due_today_is_not_overdue
AssertionError: assert [{'id': 'e243...', 'due_date': '2026-07-26', ...}] == []
```

Reverted the mutation:

```
$ pytest tests/test_tasks.py::test_list_tasks_due_today_is_not_overdue -v
PASSED
```

### 2. `test_list_tasks_done_task_with_past_due_date_is_not_overdue` — Done exclusion

Targets the `status != Done` clause: a completed task with a past due date
must not count as overdue. Mutated `app/storage.py` to drop the
`and task.status != TaskStatus.DONE` clause entirely:

```
$ pytest tests/test_tasks.py::test_list_tasks_done_task_with_past_due_date_is_not_overdue -v
FAILED tests/test_tasks.py::test_list_tasks_done_task_with_past_due_date_is_not_overdue
AssertionError: assert [{'id': '0e61...', 'due_date': '2026-07-25', 'status': 'Done', ...}] == []
```

Reverted the mutation:

```
$ pytest tests/test_tasks.py::test_list_tasks_done_task_with_past_due_date_is_not_overdue -v
PASSED
```

Full suite re-confirmed clean after both reverts:

```
$ pytest -q
......................................                                   [100%]
38 passed in 0.53s
```
