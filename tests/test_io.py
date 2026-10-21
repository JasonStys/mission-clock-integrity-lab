"""Strict inputs, worker failures, immutable reports, CLI and HTTP security by Jason Stys. Index: docs/CODE_INDEX.md."""

import copy
import hashlib
import http.client
import io
import json
import sqlite3
import subprocess
import sys
import threading
from contextlib import closing
from types import SimpleNamespace

import pytest

from clocklab import __main__ as cli
from clocklab import engine
from clocklab.engine import analyze, build_run, canonical
from clocklab.model import Settings, configuration, load_input, unique_object, validate
from clocklab.reports import export_report, save_history
from clocklab.server import WorkbenchServer, make_server


@pytest.fixture(scope="module")
def run():
    """Use actual independently checked native evidence for integration fixtures."""
    return build_run(Settings())


@pytest.mark.parametrize(
    "key,value",
    [("scenario", "unknown"), ("policy", True), ("gate", -1), ("duration", 601), ("tolerance", 0)],
)
def test_settings(key, value):
    """Reject unsupported UI states including bool pretending to be an integer."""
    with pytest.raises(ValueError):
        Settings(**{key: value})


@pytest.mark.parametrize(
    "mutation",
    [
        lambda d: d.update(schema=True),
        lambda d: d.update(name="<script>"),
        lambda d: d.update(reverse_arrival=1),
        lambda d: d.update(nodes=[]),
        lambda d: d.update(nodes=[[0, 0, 0, 0, 1]]),
        lambda d: d["config"].update(gap_end=0),
        lambda d: d["config"].update(duration=True),
        lambda d: d.update(extra=0),
        lambda d: d.update(config={}),
        lambda d: d.update(name=None),
        lambda d: d.update(nodes=[None]),
    ],
)
def test_strict_schema(mutation):
    """Unknown fields, invalid shapes and incompatible bounded values reject."""
    data = configuration(Settings())
    mutation(data)
    with pytest.raises(ValueError):
        validate(data)


@pytest.mark.parametrize(
    "body", [b"{", b"\xff", b"{" * 1800, b"{}" * 8193, b'{"schema":1,"schema":1}', b"[]", b"null"]
)
def test_input_files(tmp_path, body):
    """Malformed, nested, duplicate, non-UTF8 and excessive local JSON fails safely."""
    path = tmp_path / "input.json"
    path.write_bytes(body)
    with pytest.raises(ValueError):
        load_input(path)


def test_input_roundtrip(tmp_path):
    """A custom supported input roundtrips without coercion."""
    data = configuration(Settings())
    path = tmp_path / "input.json"
    path.write_bytes(canonical(data))
    assert load_input(path) == data
    assert unique_object([("a", 1)]) == {"a": 1}
    with pytest.raises(ValueError):
        validate(None)


def test_worker_failure_gates(monkeypatch):
    """Bad worker JSON, exit/timeout errors and reference disagreement never produce a report."""
    for output in ("not json", "x" * 2000001):
        monkeypatch.setattr(
            engine.subprocess, "run", lambda *a, output=output, **k: SimpleNamespace(stdout=output)
        )
        with pytest.raises(RuntimeError):
            engine.execute("clock_core", "")
    monkeypatch.undo()
    for error in (OSError(), subprocess.TimeoutExpired("worker", 1)):

        def fail(*a, error=error, **k):
            """Inject only the documented process boundary failure."""
            raise error

        monkeypatch.setattr(engine.subprocess, "run", fail)
        with pytest.raises(RuntimeError):
            engine.execute("clock_core", "")
    monkeypatch.undo()
    monkeypatch.setattr(engine, "execute", lambda *a: [])
    with pytest.raises(RuntimeError, match="Clock reference"):
        analyze(configuration(Settings()))
    monkeypatch.undo()
    original = engine.execute
    monkeypatch.setattr(
        engine, "execute", lambda name, text: original(name, text) if name == "clock_core" else {}
    )
    with pytest.raises(RuntimeError, match="Order reference"):
        analyze(configuration(Settings()))


def test_worker_paths(monkeypatch, tmp_path):
    """Unknown/missing workers fail, and frozen builds resolve only their bundled paths."""
    with pytest.raises(ValueError):
        engine.binary("shell")
    monkeypatch.setattr(engine, "ROOT", tmp_path)
    with pytest.raises(RuntimeError):
        engine.binary("clock_core")
    monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path), raising=False)
    path = tmp_path / "native" / ("clock_core.exe" if sys.platform == "win32" else "clock_core")
    path.parent.mkdir()
    path.touch()
    assert engine.binary("clock_core") == path


def test_reports_and_identity(run, tmp_path):
    """Exports preserve all samples and escape HTML; history verifies full identities."""
    import csv

    for kind in ("json", "input", "html", "csv"):
        body, mime = export_report(run, kind)
        assert body and "/" in mime
    assert (
        len(list(csv.reader(io.StringIO(export_report(run, "csv")[0].decode()))))
        == len(run["samples"]) + 1
    )
    hostile = copy.deepcopy(run)
    hostile["name"] = "<script>"
    assert b"<script>" not in export_report(hostile, "html")[0]
    with pytest.raises(ValueError):
        export_report(run, "exe")
    path = tmp_path / "private.sqlite3"
    save_history(path, run)
    save_history(path, run)
    with closing(sqlite3.connect(path)) as connection:
        assert connection.execute("SELECT count(*) FROM runs").fetchone()[0] == 1
        for sql in ("UPDATE runs SET report_json='bad'", "DELETE FROM runs"):
            with pytest.raises(sqlite3.IntegrityError):
                connection.execute(sql)
        for i in range(99):
            connection.execute("INSERT INTO runs VALUES(?,?)", (str(i), "{}"))
        connection.commit()
    new = copy.deepcopy(run)
    new["name"] = "new"
    new.pop("id")
    new["id"] = hashlib.sha256(canonical(new)).hexdigest()
    with pytest.raises(ValueError, match="History full"):
        save_history(path, new)
    with pytest.raises(ValueError):
        save_history(path, {"id": "bad"})
    with pytest.raises(ValueError):
        canonical(float("nan"))


@pytest.fixture
def server(tmp_path):
    """Own an ephemeral loopback service and close/join it even when assertions fail."""
    (tmp_path / "index.html").write_text("CHRONICLE", encoding="utf-8")
    (tmp_path / "assets").mkdir()
    (tmp_path / "assets/app.js").write_text("// fixture", encoding="utf-8")
    instance = make_server(tmp_path)
    thread = threading.Thread(target=instance.serve_forever, daemon=True)
    thread.start()
    try:
        yield instance
    finally:
        instance.shutdown()
        instance.server_close()
        thread.join(timeout=5)


def request(server, path="/", method="GET", headers=None):
    """Return response status/headers/body with explicit connection closure."""
    connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=20)
    try:
        connection.request(method, path, headers=headers or {})
        response = connection.getresponse()
        return response.status, dict(response.getheaders()), response.read()
    finally:
        connection.close()


@pytest.mark.parametrize(
    "path",
    [
        "/",
        "/assets/app.js",
        "/api/health",
        "/api/catalog",
        "/api/run",
        "/api/report?format=csv",
        "/api/report?format=html",
        "/api/report?format=input",
    ],
)
def test_http_valid(server, path):
    """Real protected service serves inert reports and exact assets with restrictive headers."""
    status, headers, body = request(server, path)
    assert status == 200 and body
    assert "frame-ancestors 'none'" in headers["Content-Security-Policy"]
    assert headers["Cache-Control"] == "no-store" and "Access-Control-Allow-Origin" not in headers


@pytest.mark.parametrize(
    "path,code",
    [
        ("/api/run?policy=2", 400),
        ("/api/run?scenario=bad", 400),
        ("/api/run?format=json", 400),
        ("/api/run?x=1", 400),
        ("/api/run?gate=1&gate=1", 400),
        ("/api/run?" + "x=1&" * 9, 400),
        ("/api/report?format=exe", 400),
        ("/source.py", 404),
        ("/.git/config", 404),
        ("/assets/../pyproject.toml", 404),
        ("/assets/%2e%2e", 404),
        ("/assets/missing.js", 404),
        ("/assets/app.js?x=1", 404),
        ("/assets/a.txt", 404),
        ("/" + "x" * 1024, 414),
    ],
)
def test_http_reject(server, path, code):
    """Unknown, duplicated, oversized and traversal inputs cannot expose files or run commands."""
    assert request(server, path)[0] == code


@pytest.mark.parametrize(
    "headers",
    [{"Host": "evil.test"}, {"Origin": "https://evil.test"}, {"Sec-Fetch-Site": "cross-site"}],
)
def test_origins(server, headers):
    """Loopback DNS rebinding and cross-origin browser reads are denied."""
    assert request(server, headers=headers)[0] == 403


@pytest.mark.parametrize("method", ["POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"])
def test_read_only(server, method):
    """No HTTP mutation or upload endpoint is provided."""
    assert request(server, method=method)[0] == 405


def test_http_resource_failure(server, monkeypatch):
    """Worker failures return generic errors, not host paths or exception details."""
    import clocklab.server as http_server

    def broken(settings):
        """Model a failed local worker without exposing its private error text."""
        raise RuntimeError("private path")

    monkeypatch.setattr(http_server, "build_run", broken)
    status, _, body = request(server, "/api/run")
    assert status == 500 and b"private" not in body


def test_cli(run, tmp_path, monkeypatch):
    """Real custom-input export/history, overwrite protection and launch/teardown paths work."""
    source = tmp_path / "input.json"
    source.write_bytes(canonical(run["input"]))
    destination = tmp_path / "report.json"
    args = [
        "export",
        "--input",
        str(source),
        "--output",
        str(destination),
        "--history",
        str(tmp_path / "history.sqlite3"),
    ]
    assert cli.main(args) == 0 and json.loads(destination.read_bytes())["samples"] == run["samples"]
    assert cli.main(args) == 1
    assert cli.main(["export", "--output", str(tmp_path / "preset.json")]) == 0
    assert (
        cli.main(
            ["export", "--input", str(tmp_path / "missing"), "--output", str(tmp_path / "bad.json")]
        )
        == 1
    )
    monkeypatch.setattr(cli, "ROOT", tmp_path)
    assert cli.main(["serve", "--no-browser"]) == 1
    (tmp_path / "web/dist").mkdir(parents=True)
    (tmp_path / "web/dist/index.html").touch()

    def stop(self, **kwargs):
        """End the owned serve loop immediately through its normal Ctrl+C path."""
        raise KeyboardInterrupt

    monkeypatch.setattr(WorkbenchServer, "serve_forever", stop)
    monkeypatch.setattr(cli.webbrowser, "open", lambda url: True)
    assert cli.main(["serve"]) == 0
