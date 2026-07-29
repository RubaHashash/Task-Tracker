from fastapi import HTTPException, status

from app.models import TaskStatus


VALID_TRANSITIONS: frozenset[tuple[TaskStatus, TaskStatus]] = frozenset(
	{
		(TaskStatus.TODO, TaskStatus.IN_PROGRESS),
		(TaskStatus.IN_PROGRESS, TaskStatus.TODO),
		(TaskStatus.IN_PROGRESS, TaskStatus.DONE),
		(TaskStatus.DONE, TaskStatus.IN_PROGRESS),
		(TaskStatus.IN_PROGRESS, TaskStatus.TODO),
	}
)


def validate_status_transition(current: TaskStatus, new: TaskStatus) -> None:
	"""Validate that a task status transition is allowed.

	Enforces a one-step-at-a-time state machine: only the exact
	``(current, new)`` pairs listed in ``VALID_TRANSITIONS`` are
	permitted. Transitioning to the same status, or skipping a step
	(e.g. ``ToDo`` -> ``Done`` directly), is rejected.

	Args:
		current: The task's current status.
		new: The status being transitioned to.

	Returns:
		None. Returns normally if the transition is allowed.

	Raises:
		HTTPException: With status code 422 if ``(current, new)`` is
			not in ``VALID_TRANSITIONS``. The ``detail`` message lists
			the allowed transitions.
	"""
	if (current, new) not in VALID_TRANSITIONS:
		allowed = sorted({f"{from_status.value}->{to_status.value}" for from_status, to_status in VALID_TRANSITIONS})
		raise HTTPException(
			status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
			detail=f"Invalid status transition from {current.value} to {new.value}. Allowed transitions: {allowed}",
		)