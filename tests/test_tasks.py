def test_create_task_valid_returns_201_with_full_body(client):
	response = client.post(
		"/tasks",
		json={
			"title": "Write tests",
			"description": "Module 2 coverage",
			"status": "ToDo",
			"priority": "High",
			"assignee": "Ruba",
		},
	)

	assert response.status_code == 201
	body = response.json()
	assert body["id"]
	assert body["title"] == "Write tests"
	assert body["description"] == "Module 2 coverage"
	assert body["status"] == "ToDo"
	assert body["priority"] == "High"
	assert body["assignee"] == "Ruba"
	assert body["created_at"]
	assert body["updated_at"]


def test_create_task_missing_title_returns_422(client):
	response = client.post("/tasks", json={})

	assert response.status_code == 422


def test_create_task_blank_title_returns_422(client):
	response = client.post("/tasks", json={"title": "   "})

	assert response.status_code == 422


def test_create_task_invalid_priority_returns_422(client):
	response = client.post("/tasks", json={"title": "x", "priority": "Urgent"})

	assert response.status_code == 422


def test_create_task_unknown_field_returns_422(client):
	response = client.post("/tasks", json={"title": "x", "made_up": "value"})

	assert response.status_code == 422


def test_list_tasks_empty_returns_200_and_empty_list(client):
	response = client.get("/tasks")

	assert response.status_code == 200
	assert response.json() == []


def test_list_tasks_filter_by_status_no_match_returns_200_and_empty_list(client):
	client.post("/tasks", json={"title": "todo task", "status": "ToDo"})

	response = client.get("/tasks", params={"status": "Done"})

	assert response.status_code == 200
	assert response.json() == []


def test_list_tasks_filter_by_priority_returns_only_matches(client):
	client.post("/tasks", json={"title": "high task", "priority": "High"})
	client.post("/tasks", json={"title": "low task", "priority": "Low"})

	response = client.get("/tasks", params={"priority": "High"})

	assert response.status_code == 200
	body = response.json()
	assert len(body) == 1
	assert body[0]["title"] == "high task"
	assert body[0]["priority"] == "High"


def test_get_task_by_id_returns_task(client, created_task):
	response = client.get(f"/tasks/{created_task['id']}")

	assert response.status_code == 200
	body = response.json()
	assert body["id"] == created_task["id"]
	assert body["title"] == "fixture task"


def test_get_task_by_id_not_found_returns_404_with_detail(client):
	task_id = "missing-id"
	response = client.get(f"/tasks/{task_id}")

	assert response.status_code == 404
	assert response.json() == {"detail": f"Task with id {task_id} not found"}


def test_patch_partial_update_keeps_other_fields(client, created_task):
	response = client.patch(
		f"/tasks/{created_task['id']}",
		json={"description": "updated description"},
	)

	assert response.status_code == 200
	body = response.json()
	assert body["id"] == created_task["id"]
	assert body["title"] == created_task["title"]
	assert body["description"] == "updated description"
	assert body["status"] == created_task["status"]
	assert body["priority"] == created_task["priority"]
	assert body["assignee"] == created_task["assignee"]


def test_patch_not_found_returns_404(client):
	task_id = "missing-id"
	response = client.patch(f"/tasks/{task_id}", json={"title": "new"})

	assert response.status_code == 404
	assert response.json() == {"detail": f"Task with id {task_id} not found"}


def test_patch_missing_task_id_with_status_payload_should_return_not_found(client):
	task_id = "missing-id"
	response = client.patch(f"/tasks/{task_id}", json={"status": "InProgress"})

	assert response.status_code == 404
	assert response.json() == {"detail": f"Task with id {task_id} not found"}


def test_patch_valid_transition_todo_to_inprogress_returns_200(client, created_task):
	response = client.patch(f"/tasks/{created_task['id']}", json={"status": "InProgress"})

	assert response.status_code == 200
	assert response.json()["status"] == "InProgress"


def test_patch_task_from_inprogress_to_done_should_succeed_and_persist_the_new_status(client):
	create_response = client.post(
		"/tasks",
		json={
			"title": "Move to done",
			"status": "InProgress",
			"priority": "Medium",
		},
	)
	assert create_response.status_code == 201
	task_id = create_response.json()["id"]

	response = client.patch(f"/tasks/{task_id}", json={"status": "Done"})

	assert response.status_code == 200
	assert response.json()["status"] == "Done"


def test_patch_task_from_done_back_to_inprogress_should_succeed_and_persist_the_rollback_status(client):
	create_response = client.post(
		"/tasks",
		json={
			"title": "Reopen completed task",
			"status": "Done",
			"priority": "Medium",
		},
	)
	assert create_response.status_code == 201
	task_id = create_response.json()["id"]

	response = client.patch(f"/tasks/{task_id}", json={"status": "InProgress"})

	assert response.status_code == 200
	assert response.json()["status"] == "InProgress"


def test_patch_task_from_done_directly_to_todo_should_be_rejected_as_an_invalid_transition(client):
	create_response = client.post(
		"/tasks",
		json={
			"title": "Attempt invalid rollback",
			"status": "Done",
			"priority": "Medium",
		},
	)
	assert create_response.status_code == 201
	task_id = create_response.json()["id"]

	response = client.patch(f"/tasks/{task_id}", json={"status": "ToDo"})

	assert response.status_code == 422
	assert "Invalid status transition from Done to ToDo" in response.json()["detail"]


def test_patch_invalid_transition_todo_to_done_returns_422(client, created_task):
	response = client.patch(f"/tasks/{created_task['id']}", json={"status": "Done"})

	assert response.status_code == 422


def test_patch_same_status_returns_422(client, created_task):
	response = client.patch(f"/tasks/{created_task['id']}", json={"status": "ToDo"})

	assert response.status_code == 422


def test_patch_with_whitespace_only_title_should_fail_validation(client, created_task):
	response = client.patch(f"/tasks/{created_task['id']}", json={"title": " "})

	assert response.status_code == 422
	assert "title must not be blank" in response.text


def test_patch_with_empty_json_object_should_behave_as_no_op_update_and_return_existing_task(client, created_task):
	response = client.patch(f"/tasks/{created_task['id']}", json={})

	assert response.status_code == 200
	body = response.json()
	assert body["id"] == created_task["id"]
	assert body["title"] == created_task["title"]
	assert body["description"] == created_task["description"]
	assert body["status"] == created_task["status"]
	assert body["priority"] == created_task["priority"]
	assert body["assignee"] == created_task["assignee"]


def test_delete_existing_returns_204_no_body(client, created_task):
	response = client.delete(f"/tasks/{created_task['id']}")

	assert response.status_code == 204
	assert response.content == b""


def test_delete_missing_returns_404(client):
	task_id = "missing-id"
	response = client.delete(f"/tasks/{task_id}")

	assert response.status_code == 404
	assert response.json() == {"detail": f"Task with id {task_id} not found"}