"""Adversarial checks on the freshly instrumented C++ binary by Jason Stys. Index: docs/CODE_INDEX.md."""

import json
import random
import subprocess
from pathlib import Path

from clocklab.model import Settings, configuration, wire
from clocklab.reference import simulate_reference


def main() -> None:
    """Exercise actual sanitizer model and parser with deterministic valid/invalid requests."""
    root = Path(__file__).resolve().parents[1]
    binary = root / "native-sanitize/clock_core"
    randomizer = random.Random(9173)
    requests = []
    for _ in range(80):
        data = configuration(Settings("nominal"))
        data["config"].update(duration=randomizer.randint(1, 60), slew=randomizer.randint(0, 1))
        data["nodes"] = [
            [
                randomizer.randint(-5000000000, 5000000000),
                randomizer.randint(-1000000, 1000000),
                1000000,
                0,
                0,
            ]
        ]
        result = subprocess.run(
            [str(binary)], input=wire(data), text=True, capture_output=True, timeout=10
        )
        assert result.returncode == 0 and json.loads(result.stdout) == simulate_reference(data), (
            result.stderr
        )
    for _ in range(120):
        requests.append(
            "CLOCK1 "
            + " ".join(
                str(randomizer.randint(-(10**20), 10**20)) for _ in range(randomizer.randint(0, 32))
            )
        )
    for request in requests:
        result = subprocess.run(
            [str(binary)], input=request, text=True, capture_output=True, timeout=10
        )
        assert (
            result.returncode == 2 and result.stderr.strip() == "Invalid bounded clock request"
        ), result.stderr
    print("200 actual ASan/UBSan requests passed (80 valid oracle cases, 120 malformed)")


if __name__ == "__main__":
    main()
