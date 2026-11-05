"""Neutral transport contracts; domain fields are defined during the exam."""

from dataclasses import dataclass, field
from typing import Any, Literal

Dataset = dict[str, str]
Plan = dict[str, Any]


@dataclass(frozen=True)
class Issue:
    reason: str
    file: str | None = None
    row: int | None = None
    column: str | int | None = None
    rule_id: str | None = None


@dataclass(frozen=True)
class ValidationReport:
    status: Literal["passed", "failed", "not_implemented"]
    issues: list[Issue] = field(default_factory=list)

    def __post_init__(self):
        if self.status not in {"passed", "failed", "not_implemented"}:
            raise ValueError("Unknown validation status")
        if self.status == "passed" and self.issues:
            raise ValueError("A passed report cannot contain violations")
