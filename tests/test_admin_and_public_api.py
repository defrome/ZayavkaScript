from datetime import date

from models.masters import MasterTime

ADMIN_HEADERS = {"x-admin-token": "dev-admin-token"}


def test_admin_requires_token(client):
    response = client.get("/api/v1/admin/applications/actual")
    assert response.status_code == 401


def test_public_application_creation(client):
    service_resp = client.post(
        "/api/v1/admin/services",
        headers=ADMIN_HEADERS,
        json={
            "name": "Маникюр",
            "description": "Классический",
            "price": 2500,
            "photo_url": "https://example.com/svc.png",
        },
    )
    assert service_resp.status_code == 200
    service_id = service_resp.json()["data"]["id"]

    public_create = client.post(
        "/api/v1/public/applications",
        json={
            "service_id": service_id,
            "name": "Ирина",
            "telephone_number": "+79990000000",
            "appointment_date": date.today().isoformat(),
            "time_slot": "12:30",
            "comment": "Первый визит",
        },
    )

    assert public_create.status_code == 200
    payload = public_create.json()["data"]
    assert payload["source"] == "user"
    assert payload["status"] == "new"
    assert payload["master_id"] is None


def test_admin_application_flow_and_actual_tracking(client, db_session):
    service_resp = client.post(
        "/api/v1/admin/services",
        headers=ADMIN_HEADERS,
        json={
            "name": "Окрашивание",
            "description": "Полное",
            "price": 6000,
            "photo_url": None,
        },
    )
    assert service_resp.status_code == 200
    service_id = service_resp.json()["data"]["id"]

    master_resp = client.post(
        "/api/v1/admin/masters",
        headers=ADMIN_HEADERS,
        json={"name": "Мария"},
    )
    assert master_resp.status_code == 200
    master_id = master_resp.json()["data"]["id"]

    day = date.today().isoformat()
    slot_resp = client.post(
        f"/api/v1/admin/masters/{master_id}/times",
        headers=ADMIN_HEADERS,
        json={"day": day, "time_slot": "15:00"},
    )
    assert slot_resp.status_code == 200

    create_resp = client.post(
        "/api/v1/admin/applications",
        headers=ADMIN_HEADERS,
        json={
            "service_id": service_id,
            "master_id": master_id,
            "name": "Анна",
            "telephone_number": "+79991112233",
            "appointment_date": day,
            "time_slot": "15:00",
            "comment": None,
        },
    )
    assert create_resp.status_code == 200
    app_data = create_resp.json()["data"]
    app_id = app_data["id"]
    assert app_data["status"] == "in_progress"
    assert app_data["source"] == "admin"

    actual_resp = client.get("/api/v1/admin/applications/actual", headers=ADMIN_HEADERS)
    assert actual_resp.status_code == 200
    actual_items = actual_resp.json()["data"]
    assert len(actual_items) == 1
    assert actual_items[0]["id"] == app_id

    close_resp = client.patch(
        f"/api/v1/admin/applications/{app_id}/status",
        headers=ADMIN_HEADERS,
        json={"status": "completed"},
    )
    assert close_resp.status_code == 200
    assert close_resp.json()["data"]["status"] == "completed"

    slot = db_session.query(MasterTime).filter(MasterTime.master_id == master_id, MasterTime.time_slot == "15:00").first()
    assert slot is not None
    assert slot.is_available is True

    actual_after = client.get("/api/v1/admin/applications/actual", headers=ADMIN_HEADERS)
    assert actual_after.status_code == 200
    assert actual_after.json()["data"] == []
