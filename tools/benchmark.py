"""Exact integer metric contracts and measured workload by Jason Stys. Fields: docs/CODE_INDEX.md."""

import argparse
import json
import statistics
import time
import tracemalloc
from pathlib import Path

from clocklab.engine import build_run
from clocklab.model import CASES, Settings


def main() -> None:
    """Check all six reviewed summaries; write only explicitly, measure Python allocations not native RSS."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    actual = {name: build_run(Settings(name))["summary"] for name in CASES}
    path = Path(__file__).resolve().parents[1] / "docs/reports/benchmark.json"
    if args.write:
        path.parent.mkdir(exist_ok=True)
        path.write_text(json.dumps(actual, indent=2) + "\n", encoding="utf-8")
    elif actual != json.loads(path.read_text(encoding="utf-8")):
        raise SystemExit("Integer benchmark contracts changed; investigate before refreshing")
    timings = []
    tracemalloc.start()
    for _ in range(5):
        start = time.perf_counter()
        build_run(Settings())
        timings.append((time.perf_counter() - start) * 1000)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(
        json.dumps(
            {
                "case_contracts": len(actual),
                "median_ms": round(statistics.median(timings), 3),
                "traced_python_peak_bytes": peak,
                "workload": "3 clocks / 241 ticks / 27 events / 351 interval pairs; includes native process launch and independent Python verification",
                "caveat": "Python allocation peak excludes native worker RSS; no hard latency or hardware-clock accuracy claim",
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
