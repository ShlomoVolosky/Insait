import json

import httpx
import pytest

from app.domain.models import Vehicle
from app.infrastructure.config import Settings
from app.infrastructure.repositories.http_proxy import (
    DataGovVehicleRepository,
    HttpVehicleRepository,
)
from app.infrastructure.repositories.in_memory import InMemoryVehicleRepository


class TestInMemoryRepository:
    def test_returns_seeded_vehicle(self):
        repo = InMemoryVehicleRepository()
        vehicle = repo.find_by_plate("12345678")
        assert isinstance(vehicle, Vehicle)
        assert vehicle.manufacturer == "טויוטה"
        assert vehicle.model == "קורולה"
        assert vehicle.year == 2020
        assert vehicle.color == "לבן"

    @pytest.mark.parametrize(
        "plate, manufacturer",
        [
            ("11111111", "יונדאי"),
            ("87654321", "טסלה"),
            ("22223333", "מאזדה"),
        ],
    )
    def test_all_seeds_present(self, plate, manufacturer):
        repo = InMemoryVehicleRepository()
        vehicle = repo.find_by_plate(plate)
        assert vehicle is not None
        assert vehicle.manufacturer == manufacturer

    def test_absent_plate_returns_none(self):
        repo = InMemoryVehicleRepository()
        assert repo.find_by_plate("00000000") is None


def _mock_client(handler) -> httpx.Client:
    return httpx.Client(
        transport=httpx.MockTransport(handler),
        base_url="https://upstream.example",
    )


class TestHttpRepository:
    def test_maps_upstream_success_to_vehicle(self):
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/vehicle-info"
            body = json.loads(request.content)
            assert body == {"license_plate": "12345678"}
            return httpx.Response(
                200,
                json={
                    "success": True,
                    "data": {
                        "license_plate": "12345678",
                        "manufacturer": "טויוטה",
                        "model": "קורולה",
                        "year": 2020,
                        "color": "לבן",
                    },
                },
            )

        repo = HttpVehicleRepository("https://upstream.example", client=_mock_client(handler))
        vehicle = repo.find_by_plate("12345678")
        assert isinstance(vehicle, Vehicle)
        assert vehicle.manufacturer == "טויוטה"
        assert vehicle.year == 2020

    def test_upstream_404_returns_none(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(404, json={"success": False})

        repo = HttpVehicleRepository("https://upstream.example", client=_mock_client(handler))
        assert repo.find_by_plate("00000000") is None

    def test_upstream_success_false_returns_none(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json={"success": False, "error": {"code": "X"}})

        repo = HttpVehicleRepository("https://upstream.example", client=_mock_client(handler))
        assert repo.find_by_plate("00000000") is None


def _datagov_client(handler) -> httpx.Client:
    return httpx.Client(transport=httpx.MockTransport(handler))


_RESOURCE_ID = "053cea08-09bc-40ec-8f7a-156f0677aff3"


class TestDataGovRepository:
    def test_one_record_found_maps_to_vehicle(self):
        def handler(request: httpx.Request) -> httpx.Response:
            params = dict(request.url.params)
            assert params["resource_id"] == _RESOURCE_ID
            assert params["q"] == "12345678"
            return httpx.Response(
                200,
                json={
                    "success": True,
                    "result": {
                        "records": [
                            {
                                "mispar_rechev": 12345678,
                                "tozeret_nm": "טויוטה",
                                "kinuy_mishari": "קורולה",
                                "shnat_yitzur": 2020,
                                "tzeva_rechev": "לבן",
                            }
                        ]
                    },
                },
            )

        repo = DataGovVehicleRepository(_RESOURCE_ID, client=_datagov_client(handler))
        vehicle = repo.find_by_plate("12345678")
        assert isinstance(vehicle, Vehicle)
        assert vehicle.license_plate == "12345678"
        assert vehicle.manufacturer == "טויוטה"
        assert vehicle.model == "קורולה"
        assert vehicle.year == 2020
        assert vehicle.color == "לבן"

    def test_empty_result_returns_none(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json={"success": True, "result": {"records": []}})

        repo = DataGovVehicleRepository(_RESOURCE_ID, client=_datagov_client(handler))
        assert repo.find_by_plate("00000000") is None

    def test_malformed_record_is_handled(self):
        def handler(request: httpx.Request) -> httpx.Response:
            # Missing tozeret_nm and a non-numeric year.
            return httpx.Response(
                200,
                json={
                    "success": True,
                    "result": {
                        "records": [
                            {
                                "mispar_rechev": 12345678,
                                "kinuy_mishari": "קורולה",
                                "shnat_yitzur": "NA",
                                "tzeva_rechev": "לבן",
                            }
                        ]
                    },
                },
            )

        repo = DataGovVehicleRepository(_RESOURCE_ID, client=_datagov_client(handler))
        assert repo.find_by_plate("12345678") is None


class TestSettings:
    def test_defaults(self):
        settings = Settings()
        assert settings.repository == "memory"
        assert settings.resource_id is None
        assert settings.upstream_url is None
        assert settings.app_name == "insurance-vehicle-api"

    def test_env_override(self, monkeypatch):
        monkeypatch.setenv("REPOSITORY", "http")
        monkeypatch.setenv("UPSTREAM_URL", "https://example.test")
        settings = Settings()
        assert settings.repository == "http"
        assert settings.upstream_url == "https://example.test"
