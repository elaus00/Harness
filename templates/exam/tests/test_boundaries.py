import ast
from pathlib import Path

import pytest

import validator
from contracts import ValidationReport
from scripts.check_boundaries import violations


def test_default_validator_is_explicitly_unimplemented():
    with pytest.raises(NotImplementedError):
        validator.validate({}, {})
    assert violations(Path(__file__).resolve().parents[1]) == []


@pytest.mark.parametrize(
    "source",
    [
        "from engine import generate",
        "import engine.helpers",
        "__import__('engine')",
        "importlib.import_module('engine.helpers')",
        "from harness_app.jobs import run_job",
    ],
)
def test_boundary_check_detects_forbidden_imports(tmp_path, source):
    folder = tmp_path / "validator"
    folder.mkdir()
    (folder / "bad.py").write_text(source)
    assert violations(tmp_path)


def test_validator_can_import_neutral_contracts():
    source = Path(validator.__file__).read_text()
    assert any(
        isinstance(node, ast.ImportFrom) and node.module == "contracts"
        for node in ast.walk(ast.parse(source))
    )
    assert ValidationReport("not_implemented").status != "passed"
