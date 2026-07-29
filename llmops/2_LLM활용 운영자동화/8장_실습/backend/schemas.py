from typing import Literal
from pydantic import BaseModel, Field

class RouteDecision(BaseModel):
    category: Literal[
        "overall_status",
        "ec2_status",
        "asg_status",
        "alb_status",
        "metric_analysis",
        "log_analysis",
        "incident_analysis",
        "command_generation",
        "report_generation",
        "unsupported",
    ]
    confidence: float = Field(ge=0, le=1)
    reason: str
    time_range_minutes: int = Field(default=10, ge=1, le=1440)

class Evidence(BaseModel):
    source: str
    observation: str

class IncidentAnalysis(BaseModel):
    severity: Literal[
        "normal",
        "low",
        "medium",
        "high",
        "critical",
        "unknown",
    ]
    summary: str
    current_impact: str
    evidence: list[Evidence]
    possible_causes: list[str]
    recommended_checks: list[str]
    recommended_actions: list[str]
    requires_human_approval: bool
    uncertainty: str

class CommandProposal(BaseModel):
    description: str
    command: str
    risk_level: Literal[
        "read_only",
        "low",
        "medium",
        "high",
        "prohibited",
    ]
    requires_approval: bool
    expected_result: str
    rollback: str
