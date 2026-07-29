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
		"""Validate and normalize a task title.

		Runs automatically as a Pydantic field validator whenever a
		``TaskCreate`` is constructed.

		Args:
			value: The raw title string supplied by the caller.

		Returns:
			The title with leading/trailing whitespace stripped.

		Raises:
			ValueError: If the stripped title is empty, or longer than
				200 characters. Pydantic surfaces this as a 422
				response when the model is used as a FastAPI request
				body.
		"""
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
		"""Validate and normalize an optional task title update.

		Same rules as ``TaskCreate.validate_title``, except ``None``
		(meaning "leave the title unchanged") is passed through
		without validation.

		Args:
			value: The raw title string, or ``None`` if the title is
				not being updated.

		Returns:
			The stripped title, or ``None`` if ``value`` was ``None``.

		Raises:
			ValueError: If ``value`` is not ``None`` and the stripped
				title is empty, or longer than 200 characters.
		"""
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