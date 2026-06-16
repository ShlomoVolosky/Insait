"""HTTP routes."""

from fastapi import APIRouter, Depends

from app.api.dependencies import get_use_case
from app.api.schemas import SuccessResponse, VehicleData, VehicleInfoRequest
from app.domain.ports import GetVehicleInfo

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/vehicle-info", response_model=SuccessResponse)
def get_vehicle_info(
    request: VehicleInfoRequest,
    use_case: GetVehicleInfo = Depends(get_use_case),
) -> SuccessResponse:
    vehicle = use_case.execute(request.license_plate)
    return SuccessResponse(data=VehicleData(**vehicle.model_dump()))
