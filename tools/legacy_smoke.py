"""Exercise only a freshly built/reviewed portable app by Jason Stys. Exact symbols: docs/CODE_INDEX.md.
Preserved domain acceptance; canonical process/version/browser proof is in smoke_app.py."""

import json
import queue
import subprocess
import sys
import tempfile
import threading
import urllib.request
from pathlib import Path

if __package__:
    from .release_contract import require
else:
    from release_contract import require


class RefuseRedirects(urllib.request.HTTPRedirectHandler):
    """A local application check never follows an HTTP redirect to another listener or origin."""

    def redirect_request(self, *args, **kwargs):
        """Abort before urllib can issue the redirected request."""
        raise ValueError("Local native acceptance refuses redirects")


OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}), RefuseRedirects())


def main(executable: Path) -> None:
    """Require real native/reference checks, regression scenario, SQL, notices and production HTTP assets."""
    executable = executable.resolve(strict=True)
    internal = executable.parent / "_internal"
    for name in (
        "project/LICENSE",
        "python/PYTHON.txt",
        "rust/RUST-MIT.txt",
        "rust/RUST-APACHE.txt",
        "pyinstaller/COPYING.txt",
        "vite/LICENSE.md",
    ):
        require(bool((internal / "licenses" / name).is_file()), name)
    with tempfile.TemporaryDirectory(prefix="clock-smoke-") as temporary:
        output = Path(temporary) / "report.json"
        subprocess.run(
            [
                str(executable),
                "export",
                "--scenario",
                "clock-step",
                "--output",
                str(output),
                "--history",
                str(Path(temporary) / "private.sqlite3"),
            ],
            check=True,
            timeout=30,
        )
        result = json.loads(output.read_bytes())
        require(
            bool(
                result["summary"]["wall_regressions"] == 1
                and result["method"]["order_reference_verified"]
            ),
            "Preserved native acceptance check failed",
        )
    process = subprocess.Popen(
        [str(executable), "serve", "--no-browser"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    lines: queue.Queue[str] = queue.Queue()

    def read_output() -> None:
        """Read process output off-thread with a finite startup wait."""
        require(bool(process.stdout), "Preserved native acceptance check failed")
        for line in process.stdout:
            lines.put(line.strip())

    reader = threading.Thread(target=read_output, daemon=True)
    reader.start()
    try:
        url = ""
        for _ in range(6):
            line = lines.get(timeout=15)
            if line.startswith("http://127.0.0.1:"):
                url = line
                break
        require(bool(url), "Preserved native acceptance check failed")
        for route in ("api/health", "", "api/run"):
            with OPENER.open(url + route, timeout=30) as response:
                body = response.read()
                if route == "":
                    require(
                        bool(b"CHRONICLE" in body and b"/assets/" in body),
                        "Preserved native acceptance check failed",
                    )
                elif route == "api/run":
                    require(
                        bool(json.loads(body)["summary"]["samples"] == 723),
                        "Preserved native acceptance check failed",
                    )
                else:
                    require(
                        bool(json.loads(body)["status"] == "ok"),
                        "Preserved native acceptance check failed",
                    )
        print("Frozen native workers, regression/SQL, runtime notices and actual HTTP UI passed")
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
        reader.join(timeout=3)
        if process.stdout:
            process.stdout.close()


if __name__ == "__main__":
    main(Path(sys.argv[1]))
