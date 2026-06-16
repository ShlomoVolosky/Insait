import pytest

from app.domain.exceptions import DomainError, InvalidPlateError, VehicleNotFoundError
from app.domain.models import PlateNumber, Vehicle


class TestPlateNumber:
    @pytest.mark.parametrize("plate", ["1234567", "12345678"])
    def test_valid_plate_accepted(self, plate):
        assert PlateNumber.validate(plate) == plate

    def test_valid_plate_is_stripped(self):
        assert PlateNumber.validate("  12345678  ") == "12345678"

    @pytest.mark.parametrize(
        "plate",
        ["", "   ", "123", "123456", "123456789", "abc", "1234abc", "12-34567"],
    )
    def test_invalid_plate_rejected(self, plate):
        with pytest.raises(InvalidPlateError):
            PlateNumber.validate(plate)

    def test_non_string_rejected(self):
        with pytest.raises(InvalidPlateError):
            PlateNumber.validate(12345678)  # type: ignore[arg-type]


class TestVehicle:
    def test_vehicle_constructs(self):
        vehicle = Vehicle(
            license_plate="12345678",
            manufacturer="טויוטה",
            model="קורולה",
            year=2020,
            color="לבן",
        )
        assert vehicle.license_plate == "12345678"
        assert vehicle.manufacturer == "טויוטה"
        assert vehicle.model == "קורולה"
        assert vehicle.year == 2020
        assert vehicle.color == "לבן"

    def test_year_coerced_to_int(self):
        vehicle = Vehicle(
            license_plate="12345678",
            manufacturer="x",
            model="y",
            year="2020",  # type: ignore[arg-type]
            color="z",
        )
        assert vehicle.year == 2020


class TestExceptions:
    def test_hierarchy(self):
        assert issubclass(InvalidPlateError, DomainError)
        assert issubclass(VehicleNotFoundError, DomainError)

    def test_not_found_carries_plate(self):
        err = VehicleNotFoundError("00000000")
        assert err.plate == "00000000"

    def test_invalid_plate_carries_context(self):
        err = InvalidPlateError("abc", "bad format")
        assert err.plate == "abc"
        assert err.reason == "bad format"
