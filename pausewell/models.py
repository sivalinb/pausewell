from datetime import datetime
from typing import Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, field_validator, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class Reading(StrictModel):
    time: AwareDatetime
    bpm: float = Field(ge=30, le=220)


class Window(StrictModel):
    event_id: str = Field(pattern=r"^[a-zA-Z0-9_-]{8,80}$")
    source: Literal["synthetic", "healthkit"]
    readings: list[Reading] = Field(max_length=60)
    baseline_bpm: float = Field(ge=35, le=120)
    baseline_mad: float = Field(ge=0, le=40)
    baseline_days: int = Field(ge=0, le=28)
    baseline_samples: int = Field(ge=0, le=10000)
    baseline_updated: AwareDatetime
    workout: Literal["active", "inactive", "unknown"] = "unknown"
    workout_ended: AwareDatetime | None = None
    activity: Literal["stationary", "moving", "unknown"] = "unknown"
    asleep: bool = False
    hrv_ms: float | None = Field(default=None, gt=0, le=500)
    baseline_hrv_ms: float | None = Field(default=None, gt=0, le=500)
    hrv_time: AwareDatetime | None = None

    @model_validator(mode="after")
    def hrv_complete(self):
        if self.hrv_ms is not None and (self.hrv_time is None or self.baseline_hrv_ms is None):
            raise ValueError("HRV requires its timestamp and personal baseline")
        return self


class Preferences(StrictModel):
    enabled: bool = True
    timezone: str = "America/Denver"
    quiet_start: int = Field(default=21, ge=0, le=23)
    quiet_end: int = Field(default=8, ge=0, le=23)
    daily_limit: int = Field(default=3, ge=0, le=6)
    cooldown_minutes: int = Field(default=120, ge=30, le=1440)
    cloud_consent: bool = False
    synthetic_traces: bool = False
    provider: Literal["local", "nebius", "fireworks"] = "local"
    fluid_restriction: bool = False
    movement_ok: bool = True

    @field_validator("timezone")
    @classmethod
    def valid_zone(cls, value):
        try:
            ZoneInfo(value)
        except ZoneInfoNotFoundError:
            raise ValueError("Unknown timezone") from None
        return value


class Reply(StrictModel):
    feeling: Literal["overwhelmed", "frustrated", "worried", "tired", "okay", "unsure"] = "unsure"
    context: Literal["work", "relationship", "caffeine", "illness", "exercise", "other", "private"] = (
        "private"
    )
    note: str = Field(default="", max_length=1000)
    choice: Literal["suggest", "move", "hydrate", "name", "breathe", "skip", "snooze"] = "suggest"
    symptoms: Literal["none", "urgent", "crisis"] = "none"


class Feedback(StrictModel):
    helpful: bool
    completed: bool
    felt_stressed: bool | None = None


def utcnow() -> datetime:
    from datetime import timezone

    return datetime.now(timezone.utc)
