from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, field_validator


class TaskStatus(str, Enum):
	TODO = "ToDo"
	IN_PROGRESS = "InProgress"
	DONE = "Done"


class TaskPriority(str, Enum):
	LOW = "Low"
	MEDIUM = "Medium"
	HIGH = "High"


class TaskCreate(BaseModel):
	model_config = ConfigDict(extra="forbid")

	title: str
	description: str | None = ""
	due_date: date | None = None
	status: TaskStatus = TaskStatus.TODO
	priority: TaskPriority = TaskPriority.MEDIUM
	assignee: str | None = None

	@field_validator("title")
	@classmethod
	def validate_title(cls, value: str) -> str:
		stripped_value = value.strip()
		if not stripped_value:
			raise ValueError("title must not be blank")
		if len(stripped_value) > 200:
			raise ValueError("title must be 200 characters or fewer")
		return stripped_value


class TaskUpdate(BaseModel):
	model_config = ConfigDict(extra="forbid")

	title: str | None = None
	description: str | None = None
	due_date: date | None = None
	status: TaskStatus | None = None
	priority: TaskPriority | None = None
	assignee: str | None = None

	@field_validator("title")
	@classmethod
	def validate_title(cls, value: str | None) -> str | None:
		if value is None:
			return value
		stripped_value = value.strip()
		if not stripped_value:
			raise ValueError("title must not be blank")
		if len(stripped_value) > 200:
			raise ValueError("title must be 200 characters or fewer")
		return stripped_value


class TaskResponse(BaseModel):
	model_config = ConfigDict(extra="forbid")

	id: str
	title: str
	description: str
	due_date: date | None
	status: TaskStatus
	priority: TaskPriority
	assignee: str | None
	created_at: datetime
	updated_at: datetime