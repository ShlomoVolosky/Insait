"""Exception handlers mapping every failure mode to one error envelope.

Every error response has the shape ``{"success": false, "error": {code, message}}``
so the Insait flow can branch on a single ``success`` field. No raw FastAPI /
Starlette error shapes are allowed to leak.
"""

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.schemas import ErrorBody, ErrorResponse
from app.domain.exceptions import InvalidPlateError, VehicleNotFoundError


def _envelope(code: str, message: str, status_code: int) -> JSONResponse:
    body = ErrorResponse(error=ErrorBody(code=code, message=message))
    return JSONResponse(status_code=status_code, content=body.model_dump())


async def vehicle_not_found_handler(
    request: Request, exc: VehicleNotFoundError
) -> JSONResponse:
    return _envelope("VEHICLE_NOT_FOUND", str(exc), status.HTTP_404_NOT_FOUND)


async def invalid_plate_handler(
    request: Request, exc: InvalidPlateError
) -> JSONResponse:
    return _envelope(
        "VALIDATION_ERROR", str(exc), status.HTTP_422_UNPROCESSABLE_ENTITY
    )


async def request_validation_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    parts = [
        f"{'.'.join(str(p) for p in err.get('loc', []))}: {err.get('msg')}"
        for err in exc.errors()
    ]
    message = "; ".join(parts) or "Request validation failed."
    return _envelope(
        "VALIDATION_ERROR", message, status.HTTP_422_UNPROCESSABLE_ENTITY
    )


async def unhandled_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    return _envelope(
        "INTERNAL_ERROR",
        "An unexpected error occurred.",
        status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(VehicleNotFoundError, vehicle_not_found_handler)
    app.add_exception_handler(InvalidPlateError, invalid_plate_handler)
    app.add_exception_handler(RequestValidationError, request_validation_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
