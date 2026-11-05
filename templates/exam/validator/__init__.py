from contracts import Dataset, Plan, ValidationReport


def validate(dataset: Dataset, plan: Plan) -> ValidationReport:
    """Independently check original inputs and a plan against the exam contract."""
    raise NotImplementedError("현장 요구사항에 맞는 독립 검증기를 구현해야 합니다.")
