# Comments on Tasks — Feature Plan

## 1. Data Model

Add `CommentCreate` and `CommentResponse` to `app/models.py`, alongside the existing task models.

`CommentCreate` should accept only:

- `author`: required string, 1–100 characters.
- `body`: required string, 1–2000 characters.

It should follow the existing Pydantic convention of `ConfigDict(extra="forbid")`, so unknown fields return HTTP 422. Clients must not provide `id`, `task_id`, or `created_at` because those fields are controlled by the server.

`CommentResponse` should contain:

- `id`: UUID represented as a string.
- `task_id`: string reference to the parent task.
- `author`: validated author value.
- `body`: validated comment body.
- `created_at`: timezone-aware UTC datetime.

Generate identifiers and timestamps using the conventions already present in `app/storage.py`: `str(uuid4())` and `datetime.now(timezone.utc)`.

Keep comments outside `TaskResponse` initially. This preserves all current task response shapes and avoids adding comment data to every board request. Because the repository has no database, `task_id` is a logical reference whose parent must be checked through the existing task lookup.

The existing task title validator trims surrounding whitespace and rejects whitespace-only input. Applying that behavior to `author` and `body` would fit the current model style, but it remains an assumption because the comment requirements do not define whitespace normalization.

## 2. API Routes

Add the routes to `app/main.py`, where all current live API routes are defined. Do not extend the unused legacy task classes or list in that file.

### Create a comment

- Method: `POST`
- Path: `/tasks/{task_id}/comments`
- Request body: `CommentCreate`, containing `author` and `body`.
- Success status: HTTP 201.
- Response body: `CommentResponse` containing `id`, `task_id`, `author`, `body`, and `created_at`.
- Suggested OpenAPI tag: `comments`.

Error cases:

- HTTP 404 with `{"detail": "Task with id {task_id} not found"}` when the parent task does not exist, matching current task-route wording.
- HTTP 422 when either required field is missing or violates its length constraint.
- HTTP 422 for unknown fields, including client attempts to supply server-managed fields.
- HTTP 422 for whitespace-only values if trimming and blank-value rejection are approved.

The route must verify that the task exists before storing the comment.

### List comments for a task

- Method: `GET`
- Path: `/tasks/{task_id}/comments`
- Request body: none.
- Success status: HTTP 200.
- Response body: a JSON array of `CommentResponse` objects.

Recommended behavior:

- Return `[]` when an existing task has no comments.
- Return HTTP 404 with the existing task-not-found detail shape when the task does not exist.
- Return comments in insertion order, oldest first, matching the ordering convention used by `storage.get_all_tasks()`.

### Routes outside the initial scope

The feature description does not require editing, deleting, or retrieving an individual comment. Those routes should not be introduced until the team decides the relevant lifecycle rules.

### Interaction with task deletion

The existing `DELETE /tasks/{task_id}` contract must remain HTTP 204 with no response body. If comments are stored separately, its storage operation should remove associated comments so orphaned in-memory records are not retained. This behavior is subject to team confirmation.

## 3. Tests

Add focused coverage in a new `tests/test_comments.py`, reusing the `client` and `created_task` fixtures in `tests/conftest.py`. This follows the repository's flat test layout while keeping comment behavior separate from `tests/test_tasks.py`.

Tests should follow the current style: plain pytest functions, FastAPI `TestClient` requests, explicit status-code checks, and direct JSON response assertions.

### Happy path

- `test_create_comment_returns_201_with_full_body`
- `test_create_comment_generates_valid_uuid`
- `test_create_comment_uses_task_id_from_path`
- `test_create_comment_generates_utc_created_at`
- `test_list_comments_returns_comments_in_creation_order`
- `test_list_comments_returns_only_comments_for_requested_task`
- `test_list_comments_for_existing_task_with_no_comments_returns_200_and_empty_list`

The creation coverage should verify the complete five-field response. Parse the ID as a UUID and parse `created_at` to verify that it carries a UTC offset.

### Validation

- `test_create_comment_missing_author_returns_422`
- `test_create_comment_missing_body_returns_422`
- `test_create_comment_empty_author_returns_422`
- `test_create_comment_empty_body_returns_422`
- `test_create_comment_whitespace_only_author_returns_422`
- `test_create_comment_whitespace_only_body_returns_422`
- `test_create_comment_author_at_100_characters_returns_201`
- `test_create_comment_author_over_100_characters_returns_422`
- `test_create_comment_body_at_2000_characters_returns_201`
- `test_create_comment_body_over_2000_characters_returns_422`
- `test_create_comment_unknown_field_returns_422`
- `test_create_comment_server_managed_fields_return_422`

The whitespace-only tests depend on approval of the proposed normalization rule.

### Edge cases

- `test_create_comment_for_missing_task_returns_404_with_detail`
- `test_list_comments_for_missing_task_returns_404_with_detail`
- `test_comment_body_preserves_internal_whitespace_and_line_breaks`
- `test_deleting_task_removes_associated_comments`
- `test_existing_task_response_does_not_include_comments`
- `test_deleting_task_with_comments_still_returns_204_no_body`
- `test_storage_reset_clears_comments_between_tests`

The reset behavior can be established through cross-test isolation instead of testing the private reset helper directly.

## 4. Frontend Changes

The confirmed frontend is entirely contained in `app/frontend/index.html`, including markup, CSS, JavaScript state, API requests, task-card rendering, modal handling, validation mapping, and drag-and-drop behavior. It is the only confirmed frontend file that would change.

Add a **Comments** button beside the existing **Edit** button on each task card. Selecting it should open a dedicated comments modal for that task.

The user should see:

- The parent task title for context.
- A loading state while comments are fetched.
- Existing comments showing author, body, and formatted creation time.
- A “No comments yet” state for an empty list.
- A retryable error state if loading fails.
- An author input with a 100-character limit.
- A comment textarea with a 2000-character limit.
- Field-level errors and a general error banner.
- A disabled submit button while a request is pending.

After successful creation, append or reload the comment list, clear the body field, and keep the comments view open.

Reuse existing frontend conventions:

- Extend the delegated board click handler that currently recognizes `.edit-btn`.
- Resolve the selected task through `.task-card[data-task-id]`.
- Use the existing `API_BASE` and `fetch` pattern.
- Reuse the current FastAPI error-detail parsing approach.
- Escape author and body with the existing `escapeHtml()` helper before interpolation.
- Preserve body line breaks without interpreting the body as HTML.
- Keep comment state separate from the global `tasks` array so filtering, sorting, and board rendering remain unchanged.

A separate modal is recommended because comments have their own loading, empty, error, and submission states. The desired UI placement is not specified in the current repository documentation and must be confirmed.

No automated frontend testing framework is visible. `docs/verification.md` describes manual browser verification for current frontend behavior, so the feature should include a manual checklist unless browser automation is approved separately.

## 5. Migration or Storage Notes

There is no database migration. `README.md` and `app/storage.py` confirm that tasks use in-memory storage and all data is lost when the backend restarts.

Recommended storage changes:

- Leave the existing `_tasks: dict[str, TaskResponse]` unchanged.
- Add a separate in-memory comments collection.
- Grouping comments by task ID would make ordered listing and cascade cleanup straightforward.
- Keying comments by comment ID would better support possible individual-comment routes but require filtering or a secondary index for task-based listing.
- Extend `storage._reset()` to clear comments so the autouse fixture in `tests/conftest.py` continues to isolate tests.
- Extend task deletion storage behavior to remove associated comments if cascade deletion is approved.

Existing task records require no conversion or backfill because comments are not embedded in `TaskResponse`. Existing task API responses remain unchanged.

Project documentation should state that comments share the application's current in-memory limitation and disappear whenever the backend restarts.

## 6. Open Questions

1. Should surrounding whitespace be trimmed from `author` and `body`, and should whitespace-only values be rejected?
2. Should length validation occur before or after trimming?
3. Should comments be returned oldest first or newest first?
4. Should deleting a task cascade-delete all of its comments?
5. Are comments immutable, or will update and delete operations be required?
6. Is `author` intentionally free-form given that the repository has no authentication?
7. Should comments use a separate modal, the existing edit modal, or inline card expansion?
8. Should task cards display comment counts? This could require changing task responses or issuing additional requests.
9. Is an unpaginated comment list sufficient for this course-project milestone?
10. Should the frontend show localized absolute timestamps or relative times?

## Files read

- `AGENTS.md`
- `README.md`
- `app/models.py`
- `app/main.py`
- `app/storage.py`
- `app/frontend/index.html`
- `tests/conftest.py`
- `tests/test_tasks.py`
- `tests/verify_a.py`
- `docs/user-stories.md`
- `docs/verification.md`
- `docs/midcourse/mini-adr.md`

## Assumptions to verify

- **Assumption:** Initial scope includes only comment creation and listing.
- **Assumption:** Author and body are trimmed, with whitespace-only values rejected.
- **Assumption:** Length validation occurs after trimming.
- **Assumption:** Comments are returned oldest first.
- **Assumption:** Deleting a task cascade-deletes its comments.
- **Assumption:** Comments remain separate from `TaskResponse`.
- **Assumption:** A dedicated comments modal is the preferred frontend interaction.
- **Assumption:** Free-form author names are acceptable without authentication.
- **Assumption:** Pagination is unnecessary for this course-project milestone.
- **Assumption:** Existing manual frontend verification conventions remain acceptable.

## Generic vs Repo-Grounded Codex Comparison

**Biggest difference:** TODO
**Plan I would hand to a teammate:** TODO
**Where the generic plan was still useful:** TODO
**Where repo grounding mattered most:** TODO
