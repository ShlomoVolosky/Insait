"""API request/response models — the wire contract.

These are deliberately separate from the domain `Vehicle`: the API envelope is a
transport concern. Deep plate validation lives in the domain, not here.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict


class VehicleInfoRequest(BaseModel):
    license_plate: str


class VehicleData(BaseModel):
    # `model` is a real field; opt out of Pydantic's protected-namespace warning.
    model_config = ConfigDict(protected_namespaces=())

    license_plate: str
    manufacturer: str
    model: str
    year: int
    color: str


class SuccessResponse(BaseModel):
    success: Literal[True] = True
    data: VehicleData


class ErrorBody(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    success: Literal[False] = False
    error: ErrorBody
