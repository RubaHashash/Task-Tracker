from datetime import date, datetime, timezone
from uuid import uuid4

from app.models import TaskCreate, TaskPriority, TaskResponse, TaskStatus, TaskUpdate


_tasks: dict[str, TaskResponse] = {}


def add_task(payload: TaskCreate) -> TaskResponse:
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
	return _tasks.get(task_id)


def update_task(task_id: str, payload: TaskUpdate) -> TaskResponse | None:
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
	return _tasks.pop(task_id, None) is not None


def _reset() -> None:
	_tasks.clear()