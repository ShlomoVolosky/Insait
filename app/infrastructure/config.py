"""Application settings, loaded from environment / .env via pydantic-settings."""

from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Which outbound adapter to wire behind the VehicleRepository port.
    repository: Literal["memory", "http"] = "memory"
    # Required when repository == "http": the data.gov.il CKAN resource id.
    resource_id: str | None = None
    # Used only by the generic HttpVehicleRepository demo adapter.
    upstream_url: str | None = None

    app_name: str = "insurance-vehicle-api"
    version: str = "0.1.0"
