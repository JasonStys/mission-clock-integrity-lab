"""Independent closed-interval ordering review examples by Jason Stys.

Functions: test_*; variables: hand-chosen touching/strict/unqualified intervals and cover edges.
Frontiers never imply total time order or causality. Definition lines: docs/CODE_INDEX.md.
"""

import pytest

from clocklab.engine import build_run
from clocklab.model import CASES, Settings
from clocklab.ordering import order_review


def test_touching_and_unqualified_intervals_and_minimal_edges():
    """[8,12] and [12,16] touch; both precede [19,21], which precedes [29,31]."""
    events = [
        [0, 0, 0, 10, 2, 1],
        [1, 1, 0, 14, 2, 1],
        [2, 1, 1, 20, 1, 1],
        [3, 2, 0, 100, 1, 0],
        [4, 2, 1, 30, 1, 1],
    ]
    pairs = [
        [0, 1, 2],
        [0, 2, 0],
        [0, 3, 3],
        [0, 4, 0],
        [1, 2, 0],
        [1, 3, 3],
        [1, 4, 0],
        [2, 3, 3],
        [2, 4, 0],
        [3, 4, 3],
    ]
    review = order_review(events, pairs)
    assert review["cover_edges"] == [[0, 2], [1, 2], [2, 4]]
    assert review["frontiers"] == [[0, 1], [2], [4]]
    assert review["unqualified"] == [3]
    assert review["relations"][0]["unordered_qualified"] == [1]
    assert review["relations"][-1]["definitely_after"] == [0, 1, 2]
    reversed_pairs = [[b, a, 1 if code == 0 else 0 if code == 1 else code] for a, b, code in pairs]
    assert order_review(list(reversed(events)), reversed_pairs) == review


def test_empty_unqualified_and_invalid_edge():
    """Unqualified data has no ordered frontier; a falsely definite touching pair fails closed."""
    assert order_review([], [])["frontiers"] == []
    assert order_review([[0, 0, 0, 10, 2, 0]], [])["unqualified"] == [0]
    with pytest.raises(RuntimeError, match="Invalid qualified"):
        order_review([[0, 0, 0, 10, 2, 1], [1, 1, 0, 14, 2, 1]], [[0, 1, 0]])


def test_native_cases_edges_follow_strict_qualified_intervals():
    """Independently check every reported minimal edge against the verified event's closed bounds."""
    for scenario in CASES:
        run = build_run(Settings(scenario=scenario))
        by_id = {event[0]: event for event in run["events"]}
        review = run["order_review"]
        assert (
            sorted(node for group in review["frontiers"] for node in group) == review["qualified"]
        )
        for left, right in review["cover_edges"]:
            a, b = by_id[left], by_id[right]
            assert a[5] and b[5] and a[3] + a[4] < b[3] - b[4]
