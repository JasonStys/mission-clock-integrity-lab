"""Qualified timestamp partial-order review by Jason Stys.

Function: order_review. Variables: qualified event IDs, strict interval edges and dependency frontiers.
Arrival order and source sequence are deliberately separate. Exact lines: docs/CODE_INDEX.md.
"""

from typing import Any


def order_review(events: list[list[int]], pairs: list[list[int]]) -> dict[str, Any]:
    """Build minimal interval-order edges and readiness frontiers from verified pair decisions.

    An edge means a strictly earlier qualified timestamp interval, not causality. Frontiers
    are not total-order positions: cross-frontier events without an edge/path can be unordered.
    """
    records = {event[0]: event for event in events}
    qualified = {event[0] for event in events if event[5]}
    edges: set[tuple[int, int]] = set()
    for left, right, code in pairs:
        if code not in (0, 1):
            continue
        before, after = (left, right) if code == 0 else (right, left)
        a, b = records[before], records[after]
        if before not in qualified or after not in qualified or a[3] + a[4] >= b[3] - b[4]:
            raise RuntimeError("Invalid qualified ordering edge")
        edges.add((before, after))
    covers = sorted(
        (a, b)
        for a, b in edges
        if not any((a, middle) in edges and (middle, b) in edges for middle in qualified)
    )
    remaining = set(qualified)
    frontiers = []
    while remaining:
        ready = sorted(
            node for node in remaining if not any((other, node) in edges for other in remaining)
        )
        if not ready:
            raise RuntimeError("Qualified timestamp ordering cycle")
        frontiers.append(ready)
        remaining.difference_update(ready)
    return {
        "qualified": sorted(qualified),
        "unqualified": sorted(set(records) - qualified),
        "cover_edges": [list(edge) for edge in covers],
        "frontiers": frontiers,
        "relations": [
            {
                "id": node,
                "definitely_before": sorted(b for a, b in edges if a == node),
                "definitely_after": sorted(a for a, b in edges if b == node),
                "unordered_qualified": sorted(
                    other
                    for other in qualified - {node}
                    if (node, other) not in edges and (other, node) not in edges
                ),
            }
            for node in sorted(qualified)
        ],
    }
