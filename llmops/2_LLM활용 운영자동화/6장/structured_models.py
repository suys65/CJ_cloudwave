from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)

Severity = Literal[
    "low",
    "medium",
    "high",
    "critical",
    "unknown",
]

RiskLevel = Literal[
    "read_only",
    "low",
    "medium",
    "high",
    "prohibited",
]

EvidenceType = Literal[
    "direct",
    "temporal",
    "correlation",
    "configuration",
    "general_knowledge",
]

class Cause(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
    )

    cause: str = Field(
        min_length=5,
        max_length=300,
        description="가능한 장애 원인",
    )
    evidence_type: EvidenceType
    evidence: str = Field(
        min_length=3,
        max_length=500,
        description="입력 데이터에서 확인한 근거",
    )
    confidence: Literal[
        "high",
        "medium",
        "low",
    ]
    verification: list[str] = Field(
        min_length=1,
        max_length=5,
    )

class RecommendedCheck(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
    )

    command: str = Field(
        min_length=2,
        max_length=500,
    )
    purpose: str = Field(
        min_length=3,
        max_length=300,
    )
    risk_level: RiskLevel
    approval_required: bool

    @field_validator("risk_level")
    @classmethod
    def check_read_only(cls, value: str) -> str:
        if value != "read_only":
            raise ValueError(
                "recommended_checks의 risk_level은 "
                "read_only여야 합니다."
            )
        return value

    @field_validator("approval_required")
    @classmethod
    def check_no_approval(cls, value: bool) -> bool:
        if value is not False:
            raise ValueError(
                "조회 작업의 approval_required는 "
                "false여야 합니다."
            )
        return value

class IncidentAnalysis(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
    )

    severity: Severity
    service: str = Field(
        min_length=1,
        max_length=100,
    )
    summary: str = Field(
        min_length=5,
        max_length=300,
    )
    facts: list[str] = Field(
        min_length=1,
        max_length=10,
    )
    possible_causes: list[Cause] = Field(
        min_length=1,
        max_length=3,
    )
    recommended_checks: list[RecommendedCheck] = Field(
        min_length=1,
        max_length=8,
    )
    approval_required: bool
    additional_information: list[str] = Field(
        default_factory=list,
        max_length=10,
    )
    error_code: str | None = None

class KubectlCheck(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
    )

    command: str
    purpose: str

class KubernetesIncident(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
    )

    namespace: str
    pod_name: str
    status: Literal[
        "Running",
        "Pending",
        "CrashLoopBackOff",
        "ImagePullBackOff",
        "Failed",
        "Unknown",
    ]
    severity: Severity
    summary: str = Field(
        min_length=5,
        max_length=300,
    )
    facts: list[str] = Field(
        min_length=1,
        max_length=10,
    )
    possible_causes: list[str] = Field(
        min_length=1,
        max_length=3,
    )
    recommended_checks: list[KubectlCheck] = Field(
        min_length=1,
        max_length=6,
    )
    change_required: bool
    approval_required: bool

class NetworkCheck(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
    )

    command: str
    purpose: str
    layer: Literal[
        "application",
        "transport",
        "network",
        "data_link",
        "unknown",
    ]

class NetworkIncident(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
    )

    source: str
    destination: str
    destination_port: int = Field(
        ge=1,
        le=65535,
    )
    symptom: str
    possible_causes: list[str] = Field(
        min_length=1,
        max_length=3,
    )
    recommended_checks: list[NetworkCheck] = Field(
        min_length=1,
        max_length=8,
    )
    confirmed_root_cause: bool
    additional_information: list[str] = Field(
        default_factory=list,
        max_length=10,
    )
