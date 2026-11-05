from dataclasses import asdict

from fastapi.responses import JSONResponse

from contracts import Issue


class Fault(Exception):
    def __init__(self, status, code, reason, *, issues=None):
        self.status, self.code = status, code
        self.issues = issues or [Issue(reason=reason)]


def error_response(status, code, issues, headers=None):
    return JSONResponse(
        {"error": {"code": code, "issues": [asdict(i) for i in issues]}},
        status_code=status,
        headers=headers,
    )
