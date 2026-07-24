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
	return {"status": "ok", "service": "task-tracker"}


@app.get("/tasks", response_model=list[TaskResponse], tags=["tasks"])
def list_tasks(
	status: TaskStatus | None = None,
	priority: TaskPriority | None = None,
) -> list[TaskResponse]:
	return storage.get_all_tasks(status=status, priority=priority)


@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, tags=["tasks"])
def create_task(payload: TaskCreate) -> TaskResponse:
	return storage.add_task(payload)


@app.patch("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def update_task(task_id: str, payload: TaskUpdate) -> TaskResponse:
	if payload.status is not None:
		existing_task = storage.get_task_by_id(task_id)
		if existing_task is None:
			raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
		if payload.status != existing_task.status:
			validate_status_transition(existing_task.status, payload.status)

	updated_task = storage.update_task(task_id, payload)
	if updated_task is not None:
		return updated_task
	raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["tasks"])
def delete_task(task_id: str) -> None:
	deleted = storage.delete_task(task_id)
	if deleted:
		return None
	raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
