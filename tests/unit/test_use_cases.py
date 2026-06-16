import pytest

from app.application.use_cases import GetVehicleInfoUseCase
from app.domain.exceptions import InvalidPlateError, VehicleNotFoundError
from app.domain.models import Vehicle
from app.domain.ports import VehicleRepository


class FakeRepository(VehicleRepository):
    """In-memory fake that records whether it was queried."""

    def __init__(self, vehicles: dict[str, Vehicle] | None = None) -> None:
        self._vehicles = vehicles or {}
        self.calls: list[str] = []

    def find_by_plate(self, plate: str) -> Vehicle | None:
        self.calls.append(plate)
        return self._vehicles.get(plate)


def _vehicle(plate: str = "12345678") -> Vehicle:
    return Vehicle(
        license_plate=plate,
        manufacturer="טויוטה",
        model="קורולה",
        year=2020,
        color="לבן",
    )


def test_returns_vehicle_when_present():
    vehicle = _vehicle()
    repo = FakeRepository({"12345678": vehicle})
    use_case = GetVehicleInfoUseCase(repo)

    result = use_case.execute("12345678")

    assert result is vehicle
    assert repo.calls == ["12345678"]


def test_raises_not_found_when_absent():
    repo = FakeRepository({})
    use_case = GetVehicleInfoUseCase(repo)

    with pytest.raises(VehicleNotFoundError) as exc:
        use_case.execute("00000000")

    assert exc.value.plate == "00000000"
    assert repo.calls == ["00000000"]


@pytest.mark.parametrize("bad_plate", ["abc", "", "123", "123456789"])
def test_raises_invalid_plate_and_does_not_call_repo(bad_plate):
    repo = FakeRepository({})
    use_case = GetVehicleInfoUseCase(repo)

    with pytest.raises(InvalidPlateError):
        use_case.execute(bad_plate)

    # Validation must short-circuit before the repository is touched.
    assert repo.calls == []


def test_normalizes_plate_before_lookup():
    vehicle = _vehicle()
    repo = FakeRepository({"12345678": vehicle})
    use_case = GetVehicleInfoUseCase(repo)

    result = use_case.execute("  12345678  ")

    assert result is vehicle
    assert repo.calls == ["12345678"]
