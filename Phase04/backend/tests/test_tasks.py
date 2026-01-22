# Tests for Task CRUD API endpoints

import pytest


class TestTasksAuth:
    """Tests for authentication requirements."""

    def test_get_tasks_without_auth(self, client, test_user_id):
        """Test that GET /tasks requires authentication."""
        response = client.get(f"/api/{test_user_id}/tasks")
        assert response.status_code == 403
        assert "Not authenticated" in response.json()["detail"]

    def test_get_tasks_with_invalid_token(self, client, test_user_id, invalid_jwt_token):
        """Test that invalid JWT token is rejected."""
        headers = {"Authorization": f"Bearer {invalid_jwt_token}"}
        response = client.get(f"/api/{test_user_id}/tasks", headers=headers)
        assert response.status_code == 401
        assert "Invalid authentication token" in response.json()["detail"]

    def test_get_tasks_with_expired_token(self, client, test_user_id, expired_jwt_token):
        """Test that expired JWT token is rejected."""
        headers = {"Authorization": f"Bearer {expired_jwt_token}"}
        response = client.get(f"/api/{test_user_id}/tasks", headers=headers)
        assert response.status_code == 401
        assert "Token has expired" in response.json()["detail"]

    def test_create_task_without_auth(self, client, test_user_id):
        """Test that POST /tasks requires authentication."""
        task_data = {"title": "Test Task", "description": "Test Description"}
        response = client.post(f"/api/{test_user_id}/tasks", json=task_data)
        assert response.status_code == 403


class TestGetTasks:
    """Tests for GET /api/{user_id}/tasks endpoint."""

    def test_get_tasks_empty_list(self, client, test_user_id, auth_headers):
        """Test getting tasks when no tasks exist."""
        response = client.get(f"/api/{test_user_id}/tasks", headers=auth_headers)
        assert response.status_code == 200
        assert response.json() == []

    def test_get_tasks_wrong_user_id(self, client, auth_headers):
        """Test that users cannot access other users' tasks."""
        wrong_user_id = "different-user-456"
        response = client.get(f"/api/{wrong_user_id}/tasks", headers=auth_headers)
        assert response.status_code == 404
        assert "Resource not found" in response.json()["detail"]

    def test_get_tasks_with_status_filter_all(self, client, test_user_id, auth_headers):
        """Test getting tasks with status filter 'all'."""
        # First create some tasks
        client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Task 1", "description": "Description 1"},
            headers=auth_headers
        )
        client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Task 2", "description": "Description 2"},
            headers=auth_headers
        )

        response = client.get(
            f"/api/{test_user_id}/tasks?status=all",
            headers=auth_headers
        )
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 2

    def test_get_tasks_with_status_filter_pending(self, client, test_user_id, auth_headers):
        """Test getting tasks with status filter 'pending'."""
        # Create a pending task
        client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Pending Task", "description": "Pending Description"},
            headers=auth_headers
        )

        # Create a completed task
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Completed Task", "description": "Completed Description"},
            headers=auth_headers
        )
        task_id = create_response.json()["id"]
        client.put(
            f"/api/{test_user_id}/tasks/{task_id}",
            json={"completed": True},
            headers=auth_headers
        )

        # Get only pending tasks
        response = client.get(
            f"/api/{test_user_id}/tasks?status=pending",
            headers=auth_headers
        )
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 1
        assert tasks[0]["title"] == "Pending Task"
        assert tasks[0]["completed"] is False

    def test_get_tasks_with_status_filter_completed(self, client, test_user_id, auth_headers):
        """Test getting tasks with status filter 'completed'."""
        # Create a pending task
        client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Pending Task", "description": "Pending Description"},
            headers=auth_headers
        )

        # Create a completed task
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Completed Task", "description": "Completed Description"},
            headers=auth_headers
        )
        task_id = create_response.json()["id"]
        client.put(
            f"/api/{test_user_id}/tasks/{task_id}",
            json={"completed": True},
            headers=auth_headers
        )

        # Get only completed tasks
        response = client.get(
            f"/api/{test_user_id}/tasks?status=completed",
            headers=auth_headers
        )
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 1
        assert tasks[0]["title"] == "Completed Task"
        assert tasks[0]["completed"] is True


class TestCreateTask:
    """Tests for POST /api/{user_id}/tasks endpoint."""

    def test_create_task_success(self, client, test_user_id, auth_headers):
        """Test creating a task successfully."""
        task_data = {
            "title": "New Task",
            "description": "Task Description"
        }
        response = client.post(
            f"/api/{test_user_id}/tasks",
            json=task_data,
            headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New Task"
        assert data["description"] == "Task Description"
        assert data["completed"] is False
        assert data["user_id"] == test_user_id
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_task_without_description(self, client, test_user_id, auth_headers):
        """Test creating a task without description."""
        task_data = {"title": "Task Without Description"}
        response = client.post(
            f"/api/{test_user_id}/tasks",
            json=task_data,
            headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Task Without Description"
        assert data["description"] is None

    def test_create_task_wrong_user_id(self, client, auth_headers):
        """Test that users cannot create tasks for other users."""
        wrong_user_id = "different-user-456"
        task_data = {"title": "Test Task"}
        response = client.post(
            f"/api/{wrong_user_id}/tasks",
            json=task_data,
            headers=auth_headers
        )
        assert response.status_code == 404

    def test_create_task_empty_title(self, client, test_user_id, auth_headers):
        """Test that empty title is rejected."""
        task_data = {"title": "", "description": "Some description"}
        response = client.post(
            f"/api/{test_user_id}/tasks",
            json=task_data,
            headers=auth_headers
        )
        assert response.status_code == 422

    def test_create_task_title_too_long(self, client, test_user_id, auth_headers):
        """Test that title exceeding max length is rejected."""
        task_data = {"title": "x" * 201, "description": "Some description"}
        response = client.post(
            f"/api/{test_user_id}/tasks",
            json=task_data,
            headers=auth_headers
        )
        assert response.status_code == 422

    def test_create_task_description_too_long(self, client, test_user_id, auth_headers):
        """Test that description exceeding max length is rejected."""
        task_data = {"title": "Valid Title", "description": "x" * 1001}
        response = client.post(
            f"/api/{test_user_id}/tasks",
            json=task_data,
            headers=auth_headers
        )
        assert response.status_code == 422


class TestUpdateTask:
    """Tests for PUT /api/{user_id}/tasks/{id} endpoint."""

    def test_update_task_success(self, client, test_user_id, auth_headers):
        """Test updating a task successfully."""
        # Create a task first
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Original Title", "description": "Original Description"},
            headers=auth_headers
        )
        task_id = create_response.json()["id"]

        # Update the task
        update_data = {
            "title": "Updated Title",
            "description": "Updated Description",
            "completed": True
        }
        response = client.put(
            f"/api/{test_user_id}/tasks/{task_id}",
            json=update_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["description"] == "Updated Description"
        assert data["completed"] is True

    def test_update_task_partial(self, client, test_user_id, auth_headers):
        """Test partial update of a task."""
        # Create a task first
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Original Title", "description": "Original Description"},
            headers=auth_headers
        )
        task_id = create_response.json()["id"]

        # Update only title
        update_data = {"title": "Updated Title Only"}
        response = client.put(
            f"/api/{test_user_id}/tasks/{task_id}",
            json=update_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title Only"
        assert data["description"] == "Original Description"
        assert data["completed"] is False

    def test_update_task_not_found(self, client, test_user_id, auth_headers):
        """Test updating a non-existent task."""
        update_data = {"title": "Updated Title"}
        response = client.put(
            f"/api/{test_user_id}/tasks/99999",
            json=update_data,
            headers=auth_headers
        )
        assert response.status_code == 404

    def test_update_task_wrong_user(self, client, test_user_id, auth_headers):
        """Test that users cannot update other users' tasks."""
        # Create a task
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Original Title"},
            headers=auth_headers
        )
        task_id = create_response.json()["id"]

        # Try to update with wrong user_id
        wrong_user_id = "different-user-456"
        update_data = {"title": "Updated Title"}
        response = client.put(
            f"/api/{wrong_user_id}/tasks/{task_id}",
            json=update_data,
            headers=auth_headers
        )
        assert response.status_code == 404


class TestDeleteTask:
    """Tests for DELETE /api/{user_id}/tasks/{id} endpoint."""

    def test_delete_task_success(self, client, test_user_id, auth_headers):
        """Test deleting a task successfully."""
        # Create a task first
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Task to Delete"},
            headers=auth_headers
        )
        task_id = create_response.json()["id"]

        # Delete the task
        response = client.delete(
            f"/api/{test_user_id}/tasks/{task_id}",
            headers=auth_headers
        )
        assert response.status_code == 204

        # Verify task is deleted
        get_response = client.get(f"/api/{test_user_id}/tasks", headers=auth_headers)
        assert len(get_response.json()) == 0

    def test_delete_task_not_found(self, client, test_user_id, auth_headers):
        """Test deleting a non-existent task."""
        response = client.delete(
            f"/api/{test_user_id}/tasks/99999",
            headers=auth_headers
        )
        assert response.status_code == 404

    def test_delete_task_wrong_user(self, client, test_user_id, auth_headers):
        """Test that users cannot delete other users' tasks."""
        # Create a task
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Task to Delete"},
            headers=auth_headers
        )
        task_id = create_response.json()["id"]

        # Try to delete with wrong user_id
        wrong_user_id = "different-user-456"
        response = client.delete(
            f"/api/{wrong_user_id}/tasks/{task_id}",
            headers=auth_headers
        )
        assert response.status_code == 404

        # Verify task still exists
        get_response = client.get(f"/api/{test_user_id}/tasks", headers=auth_headers)
        assert len(get_response.json()) == 1
