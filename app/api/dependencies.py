"""Dependency injection wiring: settings -> repository -> use case.

This is the only place that knows which concrete adapter is active; routes
depend on the inbound port (`GetVehicleInfo`), not on any concrete type.
"""

from functools import lru_cache

from fastapi import Depends

from app.application.use_cases import GetVehicleInfoUseCase
from app.domain.ports import GetVehicleInfo, VehicleRepository
from app.infrastructure.config import Settings
from app.infrastructure.repositories.http_proxy import HttpVehicleRepository
from app.infrastructure.repositories.in_memory import InMemoryVehicleRepository


@lru_cache
def get_settings() -> Settings:
    return Settings()


@lru_cache
def _build_repository(repository: str, upstream_url: str | None) -> VehicleRepository:
    if repository == "http":
        if not upstream_url:
            raise RuntimeError("upstream_url must be set when repository='http'")
        return HttpVehicleRepository(upstream_url)
    return InMemoryVehicleRepository()


def get_repository(settings: Settings = Depends(get_settings)) -> VehicleRepository:
    # Cached on the hashable settings values so the seed isn't rebuilt per request.
    return _build_repository(settings.repository, settings.upstream_url)


def get_use_case(
    repository: VehicleRepository = Depends(get_repository),
) -> GetVehicleInfo:
    return GetVehicleInfoUseCase(repository)
