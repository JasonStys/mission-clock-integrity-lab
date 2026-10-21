"""Analytic, finite-space, generated and native parser contracts by Jason Stys. Index: docs/CODE_INDEX.md."""

import itertools
import subprocess

import pytest
from hypothesis import given
from hypothesis import settings as generated
from hypothesis import strategies as st

from clocklab.engine import analyze, binary, build_run, execute
from clocklab.model import (
    CASES,
    CHOICES,
    FIELDS,
    NODE_RANGES,
    RANGES,
    Settings,
    configuration,
    validate,
    wire,
)
from clocklab.reference import audit_reference, simulate_reference

COMBINATIONS = list(itertools.product(CASES, *CHOICES.values()))


@pytest.mark.parametrize("scenario,policy,tolerance,gate,duration", COMBINATIONS)
def test_every_control(scenario, policy, tolerance, gate, duration):
    """Every finite browser setting requires exact native/reference agreement and complete accounting."""
    run = build_run(Settings(scenario, policy, tolerance, gate, duration))
    summary = run["summary"]
    assert summary["samples"] == 3 * (duration + 1)
    assert summary["pairs"] == summary["events"] * (summary["events"] - 1) // 2
    assert summary["pairs"] == sum(
        summary[key] for key in ("definite_pairs", "ambiguous_pairs", "unqualified_pairs")
    )
    assert summary["false_definite_claims"] == 0
    assert all(abs(row[3]) <= row[4] for row in run["samples"] if row[9])


def test_analytical_drift_and_bounds():
    """A free-running 2,000 ppb clock gains exactly 240,000 ns in 120 seconds."""
    data = configuration(Settings("nominal"))
    data["nodes"] = [[0, 2000, 2000, 2000000, 0]]
    data["config"].update(duration=120, gap_start=1, gap_end=121)
    rows = analyze(data)["samples"]
    assert rows[-1][3:6] == [240000, 1241000, 120]
    data["config"]["max_delay"] = 0
    assert all(row[11] == 0 and not row[9] for row in analyze(data)["samples"])


def test_distinct_failure_modes():
    """Blackout, step regression, out-of-envelope truth and reordered arrival have different evidence."""
    assert build_run(Settings("reference-loss"))["summary"]["unqualified_events"] > 0
    assert build_run(Settings("clock-step"))["summary"]["wall_regressions"] == 1
    assert build_run(Settings("clock-step", 1))["summary"]["wall_regressions"] == 0
    assert build_run(Settings("oscillator-fault"))["summary"]["envelope_violations"] > 0
    assert build_run(Settings("arrival-disorder"))["summary"]["arrival_disorder"] > 0
    assert build_run(Settings("nominal"))["summary"]["envelope_violations"] == 0


@generated(max_examples=60, deadline=None)
@given(
    initial=st.integers(-5000000000, 5000000000),
    drift=st.integers(-1000000, 1000000),
    tolerance=st.integers(0, 10000000),
    duration=st.integers(1, 60),
    slew=st.integers(0, 1),
)
def test_generated_integer_models(initial, drift, tolerance, duration, slew):
    """Generated bounded oscillators compare actual C++ and Rust results with independent Python."""
    data = configuration(Settings("nominal"))
    data["nodes"] = [[initial, drift, tolerance, 0, 0]]
    data["config"].update(duration=duration, slew=slew, gap_start=10, gap_end=40)
    assert analyze(data)["samples"] == simulate_reference(data)


@pytest.mark.parametrize("field,bounds", list(zip(FIELDS, RANGES, strict=True)))
@pytest.mark.parametrize("outside", [0, 1])
def test_config_bounds(field, bounds, outside):
    """Both Python and C++ reject each unsupported numeric bound before arithmetic."""
    data = configuration(Settings())
    tokens = wire(data).split()
    tokens[1 + FIELDS.index(field)] = str(bounds[outside] + (-1 if outside == 0 else 1))
    assert (
        subprocess.run(
            [str(binary("clock_core"))], input=" ".join(tokens), text=True, capture_output=True
        ).returncode
        == 2
    )
    data["config"][field] = int(tokens[1 + FIELDS.index(field)])
    with pytest.raises(ValueError):
        validate(data)


@pytest.mark.parametrize("index,bounds", list(enumerate(NODE_RANGES)))
@pytest.mark.parametrize("outside", [0, 1])
def test_node_bounds(index, bounds, outside):
    """Every per-node boundary is independently guarded by both languages."""
    data = configuration(Settings())
    tokens = wire(data).split()
    tokens[13 + index] = str(bounds[outside] + (-1 if outside == 0 else 1))
    assert (
        subprocess.run(
            [str(binary("clock_core"))], input=" ".join(tokens), text=True, capture_output=True
        ).returncode
        == 2
    )
    data["nodes"][0][index] = int(tokens[13 + index])
    with pytest.raises(ValueError):
        validate(data)


@pytest.mark.parametrize(
    "text",
    ["", "CLOCK2", "CLOCK1 1.0", "CLOCK1 +1", "CLOCK1 9223372036854775808", "x" * 4097],
    ids=["empty", "version", "float", "plus", "overflow", "oversize"],
)
def test_native_malformed(text):
    """Truncated, noncanonical, overflow and oversized clock stdin fail without a crash."""
    result = subprocess.run([str(binary("clock_core"))], input=text, text=True, capture_output=True)
    assert result.returncode == 2 and not result.stdout


def test_native_trailing_count_and_bias():
    """Extra fields, invalid count and physically unsupported synthetic path bias reject."""
    data = configuration(Settings())
    for index, value in [(12, "0"), (12, "5"), (17, "1000001")]:
        tokens = wire(data).split()
        tokens[index] = value
        assert (
            subprocess.run(
                [str(binary("clock_core"))], input=" ".join(tokens), text=True, capture_output=True
            ).returncode
            == 2
        )
    with pytest.raises(RuntimeError):
        execute("clock_core", wire(data) + " extra")


@pytest.mark.parametrize(
    "events",
    [
        [[0, 0, 0, 0, 2, 1], [1, 1, 1, 4, 2, 1]],
        [[0, 0, 0, -5, 0, 1], [1, 1, 1, -4, 0, 1]],
        [[0, 0, 0, 9, 2, 0], [1, 1, 1, 15, 2, 1]],
        [[0, 0, 0, 9, 0, 1], [1, 0, 1, 5, 0, 1]],
    ],
)
def test_interval_endpoints(events):
    """Touching, negative, unqualified and backward observations use actual Rust auditing."""
    request = "EVENTS1 " + str(len(events)) + " " + " ".join(str(v) for row in events for v in row)
    assert execute("clock-audit", request) == audit_reference(events)


@pytest.mark.parametrize(
    "text",
    [
        "",
        "EVENTS1 0",
        "EVENTS1 97",
        "EVENTS1 1 0 0 0 0 -1 1",
        "EVENTS1 1 0 0 0 0 0 2",
        "EVENTS1 1 0 0 0 9000000000001 0 1",
        "x" * 65537,
        "EVENTS1 🕐",
    ],
    ids=[
        "empty",
        "zero",
        "count",
        "negative-bound",
        "flag",
        "stamp-range",
        "oversize",
        "non-ascii",
    ],
)
def test_rust_malformed(text):
    """The actual memory-safe worker rejects invalid, non-ASCII and oversized inputs."""
    result = subprocess.run(
        [str(binary("clock-audit"))], input=text.encode("utf-8"), capture_output=True
    )
    assert result.returncode == 2 and not result.stdout


def test_maximum_nodes_and_zero_bound():
    """Maximum native shape remains bounded; exact coincident zero-width intervals are ambiguous."""
    data = configuration(Settings("nominal", duration=600))
    data["nodes"] = [[0, 0, 0, 0, 0]] * 4
    run = analyze(data)
    assert len(run["samples"]) == 2404 and len(run["events"]) == 84
    assert run["summary"]["ambiguous_pairs"] > 0
