"""Small, strict request contracts for a single-owner record workspace."""

from datetime import date
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

KINDS = Literal["visit", "medication", "lab", "allergy", "other"]


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class RecordInput(Strict):
    title: str = Field(min_length=1, max_length=120)
    date: date
    kind: KINDS
    text: str = Field(min_length=1, max_length=6000)
    synthetic: bool = False

    @field_validator("title", "text")
    @classmethod
    def nonblank(cls, value):
        if not value.strip():
            raise ValueError("Content cannot be blank")
        return value.strip()


class BriefRequest(Strict):
    patient_id: str = Field(default="ava_demo", min_length=1, max_length=80)
    question: str = Field(default="", max_length=1000)
    provider: Literal["local", "nebius", "fireworks"] = "local"
    # This grants record-text consent for this request only. Wellness preferences
    # and a prior request's consent never substitute for this explicit field.
    cloud_consent: bool = Field(default=False, strict=True)
    record_ids: list[str] | None = Field(default=None, min_length=1, max_length=10)

    @field_validator("record_ids")
    @classmethod
    def bounded_ids(cls, value):
        if value is not None and (
            len(value) != len(set(value)) or any(not 1 <= len(item) <= 80 for item in value)
        ):
            raise ValueError("Select distinct record IDs")
        return value


class AgendaInput(Strict):
    expected_revision: int = Field(ge=0, strict=True)
    priorities: list[Annotated[str, Field(min_length=1, max_length=300)]] = Field(
        default_factory=list, max_length=3
    )
    questions: list[Annotated[str, Field(min_length=1, max_length=300)]] = Field(
        default_factory=list, max_length=3
    )
    approved: bool = Field(default=False, strict=True)

    @field_validator("priorities", "questions")
    @classmethod
    def clear_distinct_text(cls, values):
        values = [value.strip() for value in values]
        if any(not value for value in values) or len({value.casefold() for value in values}) != len(values):
            raise ValueError("Use distinct, nonblank agenda items")
        return values

    @model_validator(mode="after")
    def meaningful_approval(self):
        if self.approved and not (self.priorities or self.questions):
            raise ValueError("Add a priority or question before approval")
        return self
