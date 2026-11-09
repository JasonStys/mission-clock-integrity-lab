"""Native orchestration and independently gated evidence by Jason Stys.

Functions: binary, execute, canonical, analyze, build_run. Fields/variables: docs/CODE_INDEX.md.
Workers are fixed reviewed local binaries; no shell, network requests or host-clock mutation.
"""

import hashlib
import json
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

from clocklab.model import Settings, configuration, validate, wire
from clocklab.ordering import order_review
from clocklab.reference import audit_reference, simulate_reference

ROOT = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
COLUMNS = [
    "second",
    "node",
    "wall_ns",
    "offset_ns",
    "bound_ns",
    "age_s",
    "remaining_ns",
    "accepted",
    "within_envelope",
    "qualified",
    "wall_regression",
    "mode",
]


def binary(name: str) -> Path:
    """Resolve only allowlisted native names from source build roots or the frozen bundle."""
    if name not in ("clock_core", "clock-audit"):
        raise ValueError("Unknown worker")
    suffix = ".exe" if sys.platform == "win32" else ""
    if hasattr(sys, "_MEIPASS"):
        path = ROOT / "native" / (name + suffix)
    elif name == "clock_core":
        path = (
            ROOT / "native-build" / ("Release" if sys.platform == "win32" else "") / (name + suffix)
        )
    else:
        path = ROOT / "auditor/target/release" / (name + suffix)
    if not path.is_file():
        raise RuntimeError("Build the reviewed native workers first")
    return path


def execute(name: str, request: str) -> Any:
    """Bound worker time and output; parse JSON only after a successful fixed process exits."""
    try:
        result = subprocess.run(
            [str(binary(name))],
            input=request,
            text=True,
            capture_output=True,
            check=True,
            timeout=10,
        )
        if len(result.stdout) > 2000000:
            raise RuntimeError("Worker response too large")
        return json.loads(result.stdout)
    except (subprocess.SubprocessError, OSError, ValueError) as error:
        raise RuntimeError("Native verification worker failed") from error


def canonical(value: Any) -> bytes:
    """Produce stable finite ASCII JSON used for content identity and explicit exports."""
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
    ).encode()


def analyze(data: dict[str, Any], settings: Settings | None = None) -> dict[str, Any]:
    """Require exact C++/Python sample and Rust/Python order agreement before releasing evidence."""
    validate(data)
    rows = execute("clock_core", wire(data))
    expected = simulate_reference(data)
    if rows != expected:
        raise RuntimeError("Clock reference disagreement")
    events = [
        [index, row[1], row[0], row[2], row[4], row[9]]
        for index, row in enumerate(row for row in rows if row[0] % 30 == 0)
    ]
    if data["reverse_arrival"]:
        events.reverse()
    request = (
        "EVENTS1\n"
        + str(len(events))
        + "\n"
        + "\n".join(" ".join(map(str, event)) for event in events)
        + "\n"
    )
    audit = execute("clock-audit", request)
    if audit != audit_reference(events):
        raise RuntimeError("Order reference disagreement")
    counts = [sum(pair[2] == code for pair in audit["pairs"]) for code in range(4)]
    identities = {e[0]: e for e in events}
    false_claims = 0
    for left, right, code in audit["pairs"]:
        a, b = identities[left], identities[right]
        if (code == 0 and not a[2] < b[2]) or (code == 1 and not b[2] < a[2]):
            false_claims += 1
    if false_claims:
        raise RuntimeError("Definite order contradicts simulated truth")
    run: dict[str, Any] = {
        "schema": 1,
        "name": data["name"],
        "author": "Jason Stys",
        "settings": asdict(settings) if settings else None,
        "input": data,
        "columns": COLUMNS,
        "samples": rows,
        "events": events,
        "audit": audit,
        "order_review": order_review(events, audit["pairs"]),
        "summary": {
            "samples": len(rows),
            "events": len(events),
            "pairs": sum(counts),
            "definite_pairs": counts[0] + counts[1],
            "ambiguous_pairs": counts[2],
            "unqualified_pairs": counts[3],
            "arrival_disorder": audit["arrival_disorder"],
            "wall_regressions": sum(row[10] for row in rows),
            "envelope_violations": sum(not row[8] for row in rows),
            "max_abs_offset_ns": max(abs(row[3]) for row in rows),
            "peak_bound_ns": max(row[4] for row in rows),
            "unqualified_events": sum(not e[5] for e in events),
            "false_definite_claims": false_claims,
        },
        "method": {
            "clock_reference_verified": True,
            "order_reference_verified": True,
            "clock": "C++20 integer nanoseconds; one-second ticks",
            "ordering": "Rust closed intervals; strict separation; no causal claim",
            "truth": "Synthetic elapsed-time reference only; no UTC/TAI/TT/leap-second conversion",
            "qualification": "Uses known simulation truth to flag envelope violations; not a real-world fault detector",
            "limits": "Invented deterministic oscillators, no NTP/PTP implementation, random noise, oscillator calibration, authentication, device control or operational qualification",
        },
    }
    run["id"] = hashlib.sha256(canonical(run)).hexdigest()
    return run


def build_run(settings: Settings) -> dict[str, Any]:
    """Evaluate one finite browser experiment; CLI custom inputs use analyze directly."""
    return analyze(configuration(settings), settings)
