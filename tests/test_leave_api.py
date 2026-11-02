import pytest

from app import create_app
from total_leave import LeaveManagement


@pytest.fixture
def client():
    application = create_app(LeaveManagement(default_balance=10))
    application.config.update(TESTING=True)
    return application.test_client()


def test_dashboard_and_api_catalog_are_leave_management_pages(client):
    assert b"Employee Leave Management" in client.get("/").data
    catalog = client.get("/api").get_json()
    assert catalog["service"] == "employee-leave-management"
    assert "apply_for_leave" in catalog["endpoints"]


def test_employee_can_check_initial_leave_balance(client):
    response = client.get("/api/leave-balance?employee_id=alex")

    assert response.status_code == 200
    assert response.get_json() == {
        "employee_id": "alex",
        "total_days": 10,
        "approved_days": 0,
        "pending_days": 0,
        "available_days": 10,
    }


def test_employee_can_apply_for_leave_and_pending_days_are_reserved(client):
    response = client.post(
        "/api/leave-requests",
        json={
            "employee_id": "alex",
            "requested_days": 3,
            "reason": "Family event",
        },
    )

    assert response.status_code == 201
    assert response.get_json()["status"] == "pending"
    assert client.get("/api/leave-balance?employee_id=alex").get_json()[
        "available_days"
    ] == 7


@pytest.mark.parametrize(
    "payload",
    [
        {"employee_id": "alex", "requested_days": 0, "reason": "Rest"},
        {"employee_id": "alex", "requested_days": 11, "reason": "Trip"},
        {"employee_id": "alex", "requested_days": 1, "reason": ""},
        {"employee_id": "alex", "requested_days": 1.5, "reason": "Rest"},
    ],
)
def test_invalid_leave_applications_are_rejected(client, payload):
    response = client.post("/api/leave-requests", json=payload)

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_manager_can_approve_leave_and_balance_updates(client):
    created = client.post(
        "/api/leave-requests",
        json={"employee_id": "alex", "requested_days": 4, "reason": "Vacation"},
    ).get_json()

    response = client.post(
        f"/api/leave-requests/{created['id']}/decision",
        json={"decision": "approved"},
    )

    assert response.status_code == 200
    assert response.get_json()["status"] == "approved"
    assert client.get("/api/leave-balance?employee_id=alex").get_json() == {
        "employee_id": "alex",
        "total_days": 10,
        "approved_days": 4,
        "pending_days": 0,
        "available_days": 6,
    }


def test_manager_can_reject_leave_and_release_reserved_balance(client):
    created = client.post(
        "/api/leave-requests",
        json={"employee_id": "alex", "requested_days": 4, "reason": "Vacation"},
    ).get_json()
    response = client.post(
        f"/api/leave-requests/{created['id']}/decision",
        json={"decision": "rejected"},
    )

    assert response.status_code == 200
    assert response.get_json()["status"] == "rejected"
    assert client.get("/api/leave-balance?employee_id=alex").get_json()[
        "available_days"
    ] == 10


def test_request_cannot_be_decided_twice(client):
    created = client.post(
        "/api/leave-requests",
        json={"employee_id": "alex", "requested_days": 2, "reason": "Appointment"},
    ).get_json()
    url = f"/api/leave-requests/{created['id']}/decision"
    client.post(url, json={"decision": "approved"})

    response = client.post(url, json={"decision": "rejected"})

    assert response.status_code == 400
