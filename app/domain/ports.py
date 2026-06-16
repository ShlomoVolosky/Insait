"""Ports (abstract interfaces) for the hexagonal architecture.

Outbound port: how the application reaches a data source.
Inbound port: how the outside world drives the application.

Concrete adapters live in `infrastructure` (outbound) and `application`
(inbound); the domain only defines the contracts.
"""

from abc import ABC, abstractmethod

from app.domain.models import Vehicle


class VehicleRepository(ABC):
    """Outbound port: a source of vehicle data."""

    @abstractmethod
    def find_by_plate(self, plate: str) -> Vehicle | None:
        """Return the vehicle for ``plate``, or ``None`` if not present."""
        raise NotImplementedError


class GetVehicleInfo(ABC):
    """Inbound port: the get-vehicle-info use case."""

    @abstractmethod
    def execute(self, plate: str) -> Vehicle:
        """Return the vehicle for ``plate`` or raise a domain error."""
        raise NotImplementedError
