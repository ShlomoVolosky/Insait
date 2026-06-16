"""Application use cases.

Depends only on the domain (ports, models, exceptions). It wires no concrete
adapter: the repository is supplied via the constructor.
"""

from app.domain.exceptions import VehicleNotFoundError
from app.domain.models import PlateNumber, Vehicle
from app.domain.ports import GetVehicleInfo, VehicleRepository


class GetVehicleInfoUseCase(GetVehicleInfo):
    """Validate a plate, look it up in the repository, return the vehicle."""

    def __init__(self, repository: VehicleRepository) -> None:
        self._repository = repository

    def execute(self, plate: str) -> Vehicle:
        # Validate first: a bad plate must NOT reach the repository.
        normalized = PlateNumber.validate(plate)
        vehicle = self._repository.find_by_plate(normalized)
        if vehicle is None:
            raise VehicleNotFoundError(normalized)
        return vehicle
