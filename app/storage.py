from datetime import date, datetime, timezone
from uuid import uuid4

from app.models import TaskCreate, TaskPriority, TaskResponse, TaskStatus, TaskUpdate


_tasks: dict[str, TaskResponse] = {}


def add_task(payload: TaskCreate) -> TaskResponse:
	"""Create and persist a new task.

	Args:
		payload: Validated task creation data. A ``description`` of
			``None`` is stored as an empty string.

	Returns:
		The newly created task, including a generated ``id`` and
		``created_at``/``updated_at`` timestamps (UTC).
	"""
	now = datetime.now(timezone.utc)
	task = TaskResponse(
		id=str(uuid4()),
		title=payload.title,
		description=payload.description or "",
		due_date=payload.due_date,
		status=payload.status,
		priority=payload.priority,
		assignee=payload.assignee,
		created_at=now,
		updated_at=now,
	)
	_tasks[task.id] = task
	return task


def get_all_tasks(
	status: TaskStatus | None = None,
	priority: TaskPriority | None = None,
	overdue: bool | None = None,
	assignee: str | None = None,
	search: str | None = None,
) -> list[TaskResponse]:
	"""Return tasks matching all of the given filters.

	Filters are combined with AND logic: a task must satisfy every
	filter that is provided to be included. Leaving a filter at its
	default ``None`` (or passing an empty/whitespace-only string for
	``assignee``/``search``) skips that check entirely.

	Args:
		status: Only include tasks with this exact status.
		priority: Only include tasks with this exact priority.
		overdue: If ``True``, only include tasks whose ``due_date`` is
			strictly before today and whose status is not ``Done``.
			If ``False``, only include tasks that do *not* meet that
			condition.
		assignee: Only include tasks whose assignee matches this
			value, compared case-insensitively after stripping
			whitespace.
		search: Only include tasks whose ``title`` or ``description``
			contains this value as a substring, compared
			case-insensitively after stripping whitespace.

	Returns:
		The list of tasks matching all active filters, in insertion
		order.
	"""
	tasks = list(_tasks.values())
	if status is not None:
		tasks = [task for task in tasks if task.status == status]
	if priority is not None:
		tasks = [task for task in tasks if task.priority == priority]
	if overdue is not None:
		today = date.today()
		tasks = [
			task
			for task in tasks
			if (
				task.due_date is not None
				and task.due_date < today
				and task.status != TaskStatus.DONE
			)
			== overdue
		]
	normalized_assignee = assignee.strip().lower() if assignee else ""
	if normalized_assignee:
		tasks = [
			task
			for task in tasks
			if (task.assignee or "").strip().lower() == normalized_assignee
		]
	normalized_search = search.strip().lower() if search else ""
	if normalized_search:
		tasks = [
			task
			for task in tasks
			if normalized_search in task.title.lower()
			or normalized_search in task.description.lower()
		]
	return tasks


def get_task_by_id(task_id: str) -> TaskResponse | None:
	"""Look up a task by its id.

	Args:
		task_id: The task's unique id.

	Returns:
		The matching task, or ``None`` if no task with that id exists.
	"""
	return _tasks.get(task_id)


def update_task(task_id: str, payload: TaskUpdate) -> TaskResponse | None:
	"""Apply a partial update to an existing task.

	Only fields explicitly set on ``payload`` are changed; unset
	fields are left untouched. If ``payload`` has no fields set, the
	existing task is returned unchanged (``updated_at`` is not
	touched). Explicitly setting ``description`` to ``None`` clears it
	to an empty string rather than storing ``None``.

	Args:
		task_id: The id of the task to update.
		payload: The fields to change. Fields not explicitly set are
			ignored (via ``exclude_unset``).

	Returns:
		The updated task, or ``None`` if no task with ``task_id``
		exists. When changes are applied, ``updated_at`` is set to the
		current UTC time.
	"""
	existing_task = _tasks.get(task_id)
	if existing_task is None:
		return None

	changes = payload.model_dump(exclude_unset=True)
	if not changes:
		return existing_task

	if "description" in changes and changes["description"] is None:
		changes["description"] = ""

	changes["updated_at"] = datetime.now(timezone.utc)
	updated_task = existing_task.model_copy(update=changes)
	_tasks[task_id] = updated_task
	return updated_task


def delete_task(task_id: str) -> bool:
	"""Delete a task by its id.

	Args:
		task_id: The id of the task to delete.

	Returns:
		``True`` if a task was found and deleted, ``False`` if no task
		with that id existed.
	"""
	return _tasks.pop(task_id, None) is not None


def _reset() -> None:
	_tasks.clear()