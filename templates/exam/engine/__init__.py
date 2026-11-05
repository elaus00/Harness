from typing import Any

from contracts import Dataset, Plan


def generate(dataset: Dataset, settings: dict[str, Any]) -> Plan:
    """Implement only after reading the actual requirements and data contract."""
    raise NotImplementedError("현장 요구사항에 맞는 생성기를 구현해야 합니다.")
