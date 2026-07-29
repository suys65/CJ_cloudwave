from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

class CommandRecommendation(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
    )

    purpose: str = Field(
        min_length=3,
        max_length=300,
    )
    command: str = Field(
        min_length=2,
        max_length=500,
    )
    action_type: Literal[
        "read_only",
        "change",
        "destructive",
        "unknown",
    ]
    approval_required: bool

class SecureAnalysis(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
    )

    category: Literal[
        "normal",
        "availability",
        "performance",
        "security",
        "unknown",
    ]
    severity: Literal[
        "low",
        "medium",
        "high",
        "critical",
        "unknown",
    ]
    summary: str = Field(
        min_length=5,
        max_length=300,
    )
    facts: list[str] = Field(
        min_length=1,
        max_length=10,
    )
    commands: list[CommandRecommendation] = Field(
        default_factory=list,
        max_length=10,
    )
    sensitive_information_detected: bool
    manual_review_required: bool
