from typing import List

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app import storage
from app.business_rules import validate_status_transition
from app.models import TaskCreate, TaskPriority, TaskResponse, TaskStatus, TaskUpdate

app = FastAPI(title="Task Tracker API")

app.add_middleware(
	CORSMiddleware,
	allow_origins=[
		"http://localhost:5500",
		"http://127.0.0.1:5500",
		"http://localhost:5173",
		"null",
	],
	allow_methods=["*"],
	allow_headers=["*"],
)


class LegacyTaskCreate(BaseModel):
	title: str


class Task(LegacyTaskCreate):
	id: int
	done: bool = False


tasks: List[Task] = []


@app.get("/")
def healthcheck() -> dict[str, str]:
	"""Report basic service liveness.

	Returns:
		A dict with the service status and name.

	Example:
		GET /
		-> 200 {"status": "ok", "service": "task-tracker"}
	"""
	return {"status": "ok", "service": "task-tracker"}


@app.get("/tasks", response_model=list[TaskResponse], tags=["tasks"])
def list_tasks(
	status: TaskStatus | None = None,
	priority: TaskPriority | None = None,
	overdue: bool | None = None,
	assignee: str | None = None,
	search: str | None = None,
) -> list[TaskResponse]:
	"""List tasks, optionally filtered.

	All provided filters are combined with AND logic; see
	``storage.get_all_tasks`` for exact filter semantics.

	Args:
		status: Only include tasks with this exact status.
		priority: Only include tasks with this exact priority.
		overdue: If set, only include tasks whose overdue state (due
			date strictly before today and status not ``Done``)
			matches this value.
		assignee: Only include tasks assigned to this value
			(case-insensitive, whitespace-trimmed).
		search: Only include tasks whose title or description
			contains this substring (case-insensitive,
			whitespace-trimmed).

	Returns:
		The list of matching tasks.

	Example:
		GET /tasks?status=ToDo&priority=High
		-> 200 [{"id": "...", "title": "...", "status": "ToDo", ...}]
	"""
	return storage.get_all_tasks(
		status=status,
		priority=priority,
		overdue=overdue,
		assignee=assignee,
		search=search,
	)


@app.get("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def get_task(task_id: str) -> TaskResponse:
	"""Retrieve a single task by id.

	Args:
		task_id: The task's unique id.

	Returns:
		The matching task.

	Raises:
		HTTPException: 404 if no task with ``task_id`` exists.

	Example:
		GET /tasks/{task_id}
		-> 200 {"id": "...", "title": "...", ...}
		-> 404 {"detail": "Task with id ... not found"}
	"""
	task = storage.get_task_by_id(task_id)
	if task is not None:
		return task
	raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")


@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, tags=["tasks"])
def create_task(payload: TaskCreate) -> TaskResponse:
	"""Create a new task.

	Args:
		payload: The task fields to create. Unknown fields are
			rejected with a 422, since ``TaskCreate`` forbids extras.

	Returns:
		The newly created task, with status code 201.

	Example:
		POST /tasks {"title": "Write docs"}
		-> 201 {"id": "...", "title": "Write docs", "status": "ToDo", ...}
	"""
	return storage.add_task(payload)


@app.patch("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def update_task(task_id: str, payload: TaskUpdate) -> TaskResponse:
	"""Apply a partial update to an existing task.

	If ``payload.status`` is set, the task must already exist and the
	transition from its current status to the new status must be
	valid (see ``business_rules.validate_status_transition``); this is
	checked before any fields are written.

	Args:
		task_id: The id of the task to update.
		payload: The fields to change. Only fields explicitly set are
			applied.

	Returns:
		The updated task.

	Raises:
		HTTPException: 404 if no task with ``task_id`` exists.
		HTTPException: 422 if ``payload.status`` is set and the
			transition from the task's current status is not allowed.

	Example:
		PATCH /tasks/{task_id} {"status": "InProgress"}
		-> 200 {"id": "...", "status": "InProgress", ...}
		-> 422 {"detail": "Invalid status transition from ToDo to Done. ..."}
	"""
	if payload.status is not None:
		existing_task = storage.get_task_by_id(task_id)
		if existing_task is None:
			raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
		validate_status_transition(existing_task.status, payload.status)

	updated_task = storage.update_task(task_id, payload)
	if updated_task is not None:
		return updated_task
	raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["tasks"])
def delete_task(task_id: str) -> None:
	"""Delete a task by id.

	Args:
		task_id: The id of the task to delete.

	Returns:
		None, with status code 204 on success.

	Raises:
		HTTPException: 404 if no task with ``task_id`` exists.

	Example:
		DELETE /tasks/{task_id}
		-> 204 (no body)
		-> 404 {"detail": "Task with id ... not found"}
	"""
	deleted = storage.delete_task(task_id)
	if deleted:
		return None
	raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
