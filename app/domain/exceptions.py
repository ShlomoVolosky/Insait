"""Domain-level exceptions.

These are framework-agnostic: the API layer maps them to HTTP responses, but the
domain itself knows nothing about HTTP.
"""


class DomainError(Exception):
    """Base class for all domain errors."""


class VehicleNotFoundError(DomainError):
    """Raised when no vehicle matches a (valid) license plate."""

    def __init__(self, plate: str) -> None:
        self.plate = plate
        super().__init__(f"No vehicle found for license plate '{plate}'.")


class InvalidPlateError(DomainError):
    """Raised when a license plate fails validation."""

    def __init__(self, plate: object, reason: str) -> None:
        self.plate = plate
        self.reason = reason
        super().__init__(f"Invalid license plate '{plate}': {reason}")
