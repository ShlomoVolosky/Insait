"""HTTP-backed vehicle repositories — outbound adapters.

Two adapters live here, both implementing the `VehicleRepository` port so the
data source can be swapped without touching the domain or api layers:

- `DataGovVehicleRepository` — the real adapter, querying the public
  data.gov.il CKAN datastore (wired when `REPOSITORY=http`).
- `HttpVehicleRepository` — a generic proxy against any upstream that honours
  our own contract; kept as a demonstration of the port swap.
"""

import httpx
from pydantic import ValidationError

from app.domain.models import Vehicle
from app.domain.ports import VehicleRepository


class HttpVehicleRepository(VehicleRepository):
    """Fetches vehicle data from an upstream HTTP registry."""

    def __init__(
        self,
        upstream_url: str,
        client: httpx.Client | None = None,
        *,
        path: str = "/vehicle-info",
        timeout: float = 10.0,
    ) -> None:
        self._upstream_url = upstream_url.rstrip("/")
        self._path = path
        # An injected client is used as-is (tests pass a mocked one); otherwise
        # build one bound to the upstream base URL.
        self._client = client or httpx.Client(base_url=self._upstream_url, timeout=timeout)

    def find_by_plate(self, plate: str) -> Vehicle | None:
        response = self._client.post(self._path, json={"license_plate": plate})
        if response.status_code == httpx.codes.NOT_FOUND:
            return None
        response.raise_for_status()

        payload = response.json()
        if not payload.get("success"):
            return None

        data = payload["data"]
        return Vehicle(
            license_plate=data["license_plate"],
            manufacturer=data["manufacturer"],
            model=data["model"],
            year=data["year"],
            color=data["color"],
        )


class DataGovVehicleRepository(VehicleRepository):
    """Fetches vehicle data from the data.gov.il CKAN ``datastore_search`` API.

    Queries the configured resource by license plate and maps the Israeli
    registry field names onto the domain `Vehicle`:

    ``mispar_rechev`` → license_plate, ``tozeret_nm`` → manufacturer,
    ``kinuy_mishari`` → model, ``shnat_yitzur`` → year, ``tzeva_rechev`` → color.
    """

    DEFAULT_BASE_URL = "https://data.gov.il/api/3/action/datastore_search"

    def __init__(
        self,
        resource_id: str,
        client: httpx.Client | None = None,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 10.0,
    ) -> None:
        self._resource_id = resource_id
        self._base_url = base_url
        # An injected client is used as-is (tests pass a mocked one).
        self._client = client or httpx.Client(timeout=timeout)

    def find_by_plate(self, plate: str) -> Vehicle | None:
        response = self._client.get(
            self._base_url,
            params={"resource_id": self._resource_id, "q": plate, "limit": 1},
        )
        response.raise_for_status()

        payload = response.json()
        if not payload.get("success"):
            return None

        records = payload.get("result", {}).get("records", [])
        if not records:
            return None

        return self._to_vehicle(records[0])

    @staticmethod
    def _to_vehicle(record: dict) -> Vehicle | None:
        """Map a CKAN record to a `Vehicle`; return ``None`` if it is malformed."""
        try:
            return Vehicle(
                license_plate=str(record["mispar_rechev"]),
                manufacturer=record["tozeret_nm"],
                model=record["kinuy_mishari"],
                year=int(record["shnat_yitzur"]),
                color=record["tzeva_rechev"],
            )
        except (KeyError, TypeError, ValueError, ValidationError):
            return None
