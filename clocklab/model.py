"""Strict synthetic scenario and wire contracts by Jason Stys.

Types: Settings. Functions: catalog, configuration, validate, wire, load_input.
Variables and field locations: docs/CODE_INDEX.md. All times are elapsed simulation time, not UTC.
"""

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

CASES = {
    "nominal": "Stable reference",
    "reference-loss": "Reference blackout",
    "asymmetric-path": "Asymmetric path",
    "clock-step": "Backward clock step",
    "oscillator-fault": "Out-of-envelope oscillator",
    "arrival-disorder": "Reordered telemetry",
}
CHOICES = {
    "policy": (0, 1),
    "tolerance": (1, 2, 4),
    "gate": (1000000, 5000000, 50000000),
    "duration": (240, 600),
}
FIELDS = (
    "duration",
    "period",
    "holdover",
    "slew",
    "slew_rate",
    "max_delay",
    "gap_start",
    "gap_end",
    "fault_time",
    "jump",
    "drift_change",
)
RANGES = (
    (1, 600),
    (1, 60),
    (1, 600),
    (0, 1),
    (1, 1000000),
    (0, 100000000),
    (0, 601),
    (0, 601),
    (1, 601),
    (-5000000000, 5000000000),
    (-10000000, 10000000),
)
NODE_RANGES = (
    (-5000000000, 5000000000),
    (-1000000, 1000000),
    (0, 10000000),
    (0, 100000000),
    (-50000000, 50000000),
)


@dataclass(frozen=True)
class Settings:
    """Finite UI experiment controls; policy 0=step, 1=rate-limited slew, never host policy."""

    scenario: str = "reference-loss"
    policy: int = 0
    tolerance: int = 1
    gate: int = 5000000
    duration: int = 240

    def __post_init__(self) -> None:
        """Reject booleans, unknown case names and choices outside the finite model."""
        if (
            not isinstance(self.scenario, str)
            or self.scenario not in CASES
            or any(
                type(getattr(self, key)) is not int or getattr(self, key) not in values
                for key, values in CHOICES.items()
            )
        ):
            raise ValueError("Unsupported setting")


def catalog() -> dict[str, Any]:
    """Provide finite labels/options without executable, path or networking configuration."""
    return {"cases": CASES, "choices": CHOICES, "defaults": asdict(Settings())}


def configuration(settings: Settings) -> dict[str, Any]:
    """Create three fictional oscillators and one explicit disturbance profile."""
    gap = settings.scenario in ("reference-loss", "oscillator-fault")
    config = dict(
        zip(
            FIELDS,
            (
                settings.duration,
                30,
                120,
                settings.policy,
                100000,
                settings.gate,
                60 if gap else 0,
                181 if gap else 0,
                61,
                2000000000 if settings.scenario == "clock-step" else 0,
                5000000 if settings.scenario == "oscillator-fault" else 0,
            ),
            strict=True,
        )
    )
    nodes = [
        [1000000, 1000, 2500 * settings.tolerance, 2000000, 0],
        [-2000000, -2000, 2500 * settings.tolerance, 2000000, 0],
        [500000, 500, 2500 * settings.tolerance, 2000000, 0],
    ]
    if settings.scenario == "asymmetric-path":
        nodes[0][4], nodes[1][4] = 900000, -900000
        nodes[2][3] = 12000000
    return {
        "schema": 1,
        "name": settings.scenario,
        "config": config,
        "nodes": nodes,
        "reverse_arrival": settings.scenario == "arrival-disorder",
    }


def validate(data: Any) -> dict[str, Any]:
    """Validate exact schema and bounded integer arithmetic before either native worker starts."""
    if (
        not isinstance(data, dict)
        or set(data) != {"schema", "name", "config", "nodes", "reverse_arrival"}
        or type(data["schema"]) is not int
        or data["schema"] != 1
    ):
        raise ValueError("Invalid schema")
    name = data["name"]
    if (
        not isinstance(name, str)
        or not 1 <= len(name) <= 48
        or any(ch not in "abcdefghijklmnopqrstuvwxyz0123456789-" for ch in name)
    ):
        raise ValueError("Invalid name")
    config, nodes = data["config"], data["nodes"]
    if (
        not isinstance(config, dict)
        or set(config) != set(FIELDS)
        or type(data["reverse_arrival"]) is not bool
    ):
        raise ValueError("Invalid configuration")
    for key, (low, high) in zip(FIELDS, RANGES, strict=True):
        if type(config[key]) is not int or not low <= config[key] <= high:
            raise ValueError("Parameter outside envelope")
    if (
        config["gap_end"] < config["gap_start"]
        or not isinstance(nodes, list)
        or not 1 <= len(nodes) <= 4
    ):
        raise ValueError("Invalid gap or nodes")
    for row in nodes:
        if (
            not isinstance(row, list)
            or len(row) != 5
            or any(
                type(value) is not int or not low <= value <= high
                for value, (low, high) in zip(row, NODE_RANGES, strict=True)
            )
            or abs(row[4]) > row[3] // 2
        ):
            raise ValueError("Invalid oscillator")
    return data


def wire(data: dict[str, Any]) -> str:
    """Serialize only validated canonical integers into the fixed C++ CLOCK1 stdin contract."""
    validate(data)
    return (
        "CLOCK1\n"
        + " ".join(str(data["config"][key]) for key in FIELDS)
        + "\n"
        + str(len(data["nodes"]))
        + "\n"
        + "\n".join(" ".join(map(str, row)) for row in data["nodes"])
        + "\n"
    )


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Reject duplicate JSON keys instead of silently accepting the last interpretation."""
    out: dict[str, Any] = {}
    for key, value in pairs:
        if key in out:
            raise ValueError("Duplicate field")
        out[key] = value
    return out


def load_input(path: Path) -> dict[str, Any]:
    """Read at most 16 KiB of explicit local JSON; no remote URI or browser upload is supported."""
    with path.open("rb") as stream:
        body = stream.read(16385)
    if len(body) > 16384:
        raise ValueError("Input too large")
    try:
        return validate(json.loads(body, object_pairs_hook=unique_object))
    except (RecursionError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError("Invalid JSON") from error
