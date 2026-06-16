"""Domain models and value rules.

Pure domain: depends only on Pydantic for modelling, never on FastAPI/httpx or
any other layer.
"""

import re

from pydantic import BaseModel, ConfigDict

from app.domain.exceptions import InvalidPlateError

# Israeli license plate as used in this assignment: a 7–8 digit numeric string.
_PLATE_RE = re.compile(r"^\d{7,8}$")


class PlateNumber:
    """Validation helper for license plate numbers.

    Not a Pydantic field type — a small value rule the use case applies to raw
    input before touching the repository.
    """

    @staticmethod
    def validate(value: object) -> str:
        """Return the normalized plate, or raise ``InvalidPlateError``."""
        if not isinstance(value, str):
            raise InvalidPlateError(value, "plate must be a string")
        plate = value.strip()
        if not plate:
            raise InvalidPlateError(value, "plate must not be empty")
        if not _PLATE_RE.fullmatch(plate):
            raise InvalidPlateError(value, "plate must be a 7–8 digit numeric string")
        return plate


class Vehicle(BaseModel):
    """A vehicle as returned by the registry."""

    # `model` is a legitimate domain field; opt out of Pydantic's `model_`
    # protected-namespace warning since it does not collide with BaseModel APIs.
    model_config = ConfigDict(protected_namespaces=())

    license_plate: str
    manufacturer: str
    model: str
    year: int
    color: str
