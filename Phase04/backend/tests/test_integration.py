# Integration tests for backend API
# These tests use the real database and run against a live server

import requests
import jwt
from datetime import datetime, timedelta
from app.config import settings


# Backend base URL (assumes server is running)
BASE_URL = "http://localhost:8000"


def generate_test_token(user_id="test-user-integration"):
    """Generate a valid JWT token for testing."""
    payload = {
        "sub": user_id,
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, settings.better_auth_secret, algorithm="HS256")


def test_server_is_running():
    """Test that the server is running and responsive."""
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Todo Backend API"
    assert data["status"] == "running"


def test_health_check():
    """Test the health check endpoint."""
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_api_docs_available():
    """Test that API documentation is accessible."""
    response = requests.get(f"{BASE_URL}/docs")
    assert response.status_code == 200


def test_authentication_required():
    """Test that protected endpoints require authentication."""
    response = requests.get(f"{BASE_URL}/api/test-user/tasks")
    # FastAPI HTTPBearer returns 403 for missing credentials
    assert response.status_code in [401, 403], f"Expected 401 or 403, got {response.status_code}"
    data = response.json()
    # Accept either "Not authenticated" or "not authenticated" (case insensitive)
    assert "authenticated" in data["detail"].lower()


def test_full_crud_workflow():
    """Test complete CRUD workflow with authentication."""
    user_id = "test-user-integration"
    token = generate_test_token(user_id)
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create a task
    task_data = {"title": "Integration Test Task", "description": "Testing CRUD"}
    create_response = requests.post(
        f"{BASE_URL}/api/{user_id}/tasks",
        json=task_data,
        headers=headers
    )
    assert create_response.status_code == 201
    created_task = create_response.json()
    task_id = created_task["id"]
    assert created_task["title"] == "Integration Test Task"
    assert created_task["completed"] is False

    # 2. Get all tasks
    get_response = requests.get(
        f"{BASE_URL}/api/{user_id}/tasks",
        headers=headers
    )
    assert get_response.status_code == 200
    tasks = get_response.json()
    assert any(task["id"] == task_id for task in tasks)

    # 3. Update the task
    update_data = {"completed": True}
    update_response = requests.put(
        f"{BASE_URL}/api/{user_id}/tasks/{task_id}",
        json=update_data,
        headers=headers
    )
    assert update_response.status_code == 200
    updated_task = update_response.json()
    assert updated_task["completed"] is True

    # 4. Delete the task
    delete_response = requests.delete(
        f"{BASE_URL}/api/{user_id}/tasks/{task_id}",
        headers=headers
    )
    assert delete_response.status_code == 204

    # 5. Verify deletion
    get_deleted_response = requests.get(
        f"{BASE_URL}/api/{user_id}/tasks",
        headers=headers
    )
    assert get_deleted_response.status_code == 200
    remaining_tasks = get_deleted_response.json()
    assert not any(task["id"] == task_id for task in remaining_tasks)


if __name__ == "__main__":
    print("Running integration tests...")
    print("Make sure the backend server is running on http://localhost:8000")
    print()

    try:
        test_server_is_running()
        print("[PASS] Server is running")

        test_health_check()
        print("[PASS] Health check passed")

        test_api_docs_available()
        print("[PASS] API docs available")

        test_authentication_required()
        print("[PASS] Authentication check passed")

        test_full_crud_workflow()
        print("[PASS] Full CRUD workflow passed")

        print("\nAll integration tests passed!")
    except AssertionError as e:
        import traceback
        print(f"\n[FAIL] Test failed: {e}")
        traceback.print_exc()
    except Exception as e:
        import traceback
        print(f"\n[ERROR] Error: {e}")
        traceback.print_exc()
