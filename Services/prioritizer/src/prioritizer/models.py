from pydantic import BaseModel, field_validator
from typing import Literal


class Action(BaseModel):
    action: str
    solution: str
    solution_classification: str | None = None
    mode: str | None = None
    sector: str | None = None
    cluster: str | None = None
    adoption_unit: str | None = None
    effectiveness: str | None = None
    adoption_current: str | None = None
    adoption_achievable_range: str | None = None
    ghg_impact: str | None = None
    cost: float | None = None
    climate_pollutants_mitigated: str | None = None
    speed_of_action: str | None = None
    climate_adaptation_benefits: str | None = None
    environment_benefits: str | None = None
    human_wellbeing_benefits: str | None = None

    @field_validator("cost", mode="before")
    @classmethod
    def parse_cost(cls, v) -> float | None:
        if v is None:
            return None
        if isinstance(v, (int, float)):
            return float(v)
        v = str(v).strip()
        if not v:
            return None
        return float(v.replace(",", ""))


class UserProfile(BaseModel):
    city: str
    climate_zone: Literal["tropical", "temperate", "cold", "arid"]
    primary_transport: Literal["car", "motorcycle", "bicycle", "public_transit", "walking"]
    diet: Literal["heavy_meat", "moderate_meat", "vegetarian", "vegan"]
    housing_type: Literal["apartment", "house"]
    energy_source: Literal["grid", "solar", "generator"]
    income_level: Literal["low", "medium", "high"]