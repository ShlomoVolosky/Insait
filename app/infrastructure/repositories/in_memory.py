"""In-memory vehicle repository — the default outbound adapter.

Seed data uses Hebrew values to match the domain and the assignment demo.
`00000000` is intentionally absent to drive the not-found demo path.
"""

from app.domain.models import Vehicle
from app.domain.ports import VehicleRepository


def _default_seed() -> dict[str, Vehicle]:
    return {
        "12345678": Vehicle(
            license_plate="12345678",
            manufacturer="טויוטה",
            model="קורולה",
            year=2020,
            color="לבן",
        ),
        "11111111": Vehicle(
            license_plate="11111111",
            manufacturer="יונדאי",
            model="i20",
            year=2019,
            color="שחור",
        ),
        "87654321": Vehicle(
            license_plate="87654321",
            manufacturer="טסלה",
            model="Model 3",
            year=2022,
            color="אדום",
        ),
        "22223333": Vehicle(
            license_plate="22223333",
            manufacturer="מאזדה",
            model="3",
            year=2021,
            color="כסף",
        ),
    }


class InMemoryVehicleRepository(VehicleRepository):
    """Looks up vehicles from an in-memory dict."""

    def __init__(self, vehicles: dict[str, Vehicle] | None = None) -> None:
        self._vehicles = vehicles if vehicles is not None else _default_seed()

    def find_by_plate(self, plate: str) -> Vehicle | None:
        return self._vehicles.get(plate)
