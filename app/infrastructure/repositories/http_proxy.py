"""HTTP proxy vehicle repository — OPTIONAL adapter.

Not wired by default. It exists to prove the outbound port lets us swap the data
source (mock → real registry) without touching the domain or api layers. It
calls an upstream service that honours the same contract and maps the response
into a domain `Vehicle`.
"""

import httpx

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
