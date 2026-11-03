"""Start both development servers on temporary ports and verify HTTP integration."""
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import tempfile
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def read(url):
    with urllib.request.urlopen(url, timeout=2) as response:
        return response.read()


def wait_for(url, process):
    for _ in range(100):
        if process.poll() is not None:
            raise RuntimeError("Development server exited before becoming ready")
        try:
            return read(url)
        except (urllib.error.URLError, TimeoutError):
            time.sleep(0.2)
    raise RuntimeError("Timed out waiting for " + url)


def main():
    backend_port, frontend_port = free_port(), free_port()
    while frontend_port == backend_port:
        frontend_port = free_port()
    backend_url = f"http://127.0.0.1:{backend_port}"
    frontend_url = f"http://127.0.0.1:{frontend_port}"
    processes = []
    with tempfile.TemporaryFile() as log:
        try:
            backend = subprocess.Popen(
                ["uv", "run", "--locked", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(backend_port)],
                cwd=ROOT / "backend", stdout=log, stderr=log, start_new_session=True,
            )
            processes.append(backend)
            expected = {"status": "ok", "service": "harness-api"}
            assert json.loads(wait_for(backend_url + "/api/v1/health", backend)) == expected
            frontend = subprocess.Popen(
                ["npm", "run", "dev", "--", "--port", str(frontend_port)],
                cwd=ROOT / "frontend", env={**os.environ, "API_PROXY_TARGET": backend_url},
                stdout=log, stderr=log, start_new_session=True,
            )
            processes.append(frontend)
            assert b'id="root"' in wait_for(frontend_url, frontend)
            assert json.loads(read(frontend_url + "/api/v1/health")) == expected
            print("PASS: FastAPI health, Vite HTML, Vite-to-FastAPI proxy")
        except Exception:
            log.seek(0)
            print(log.read().decode(errors="replace"))
            raise
        finally:
            for process in reversed(processes):
                try:
                    os.killpg(process.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()


if __name__ == "__main__":
    main()
