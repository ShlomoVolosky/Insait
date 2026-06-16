import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_found_returns_success_with_correct_data():
    response = client.post("/vehicle-info", json={"license_plate": "12345678"})
    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "data": {
            "license_plate": "12345678",
            "manufacturer": "טויוטה",
            "model": "קורולה",
            "year": 2020,
            "color": "לבן",
        },
    }


def test_not_found_returns_404_envelope():
    response = client.post("/vehicle-info", json={"license_plate": "00000000"})
    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VEHICLE_NOT_FOUND"


@pytest.mark.parametrize("plate", ["abc", "", "123"])
def test_invalid_format_returns_422_validation_error(plate):
    response = client.post("/vehicle-info", json={"license_plate": plate})
    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"


def test_missing_license_plate_key_returns_422():
    response = client.post("/vehicle-info", json={})
    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"
    # The default FastAPI error shape must not leak through.
    assert "detail" not in body


def test_success_envelope_shape():
    response = client.post("/vehicle-info", json={"license_plate": "12345678"})
    body = response.json()
    assert set(body.keys()) == {"success", "data"}
    assert set(body["data"].keys()) == {
        "license_plate",
        "manufacturer",
        "model",
        "year",
        "color",
    }


def test_error_envelope_shape():
    response = client.post("/vehicle-info", json={"license_plate": "00000000"})
    body = response.json()
    assert set(body.keys()) == {"success", "error"}
    assert set(body["error"].keys()) == {"code", "message"}
