"""Check direct and literal dynamic imports; also review nonliteral indirection."""

import ast
from pathlib import Path


def violations(root):
    found = []
    for file in sorted((Path(root) / "validator").rglob("*.py")):
        for node in ast.walk(ast.parse(file.read_text())):
            names = []
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or ""]
            elif isinstance(node, ast.Call) and node.args:
                name = getattr(node.func, "id", getattr(node.func, "attr", ""))
                if name in {"__import__", "import_module"}:
                    arg = node.args[0]
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        names = [arg.value]
            if any(n.split(".")[0] in {"engine", "harness_app", "app"} for n in names):
                found.append(f"{file}:{node.lineno}: generator/app import")
    return found


if __name__ == "__main__":
    errors = violations(Path(__file__).resolve().parents[1])
    if errors:
        raise SystemExit("\n".join(errors))
    print("정적 검증기 의존성 검사 통과. 동적·간접 참조는 코드 검토도 필요합니다.")
