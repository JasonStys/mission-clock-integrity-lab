"""Independent Python integer timing and interval oracle by Jason Stys.

Functions: simulate_reference, audit_reference. Variables/columns: docs/CODE_INDEX.md.
No calls to production native logic. Common specification is not independent physical validation.
"""

from typing import Any


def simulate_reference(data: dict[str, Any]) -> list[list[int]]:
    """Evolve per-clock state tick-first, using explicit capped correction and phase-bound equations."""
    c = data["config"]
    state = [{"phase": n[0], "pending": 0, "synced": -1, "wall": 0} for n in data["nodes"]]
    columns: list[list[list[int]]] = [[] for _ in state]
    for second in range(c["duration"] + 1):
        for node, (n, s) in enumerate(zip(data["nodes"], state, strict=True)):
            if second:
                s["phase"] += n[1]
                if node == 0 and second >= c["fault_time"]:
                    s["phase"] += c["drift_change"]
                if node == 0 and second == c["fault_time"]:
                    s["phase"] += c["jump"]
                if c["slew"]:
                    sign = 1 if s["pending"] >= 0 else -1
                    correction = sign * min(abs(s["pending"]), c["slew_rate"])
                    s["pending"] -= correction
                    s["phase"] -= correction
            connected = second < c["gap_start"] or second >= c["gap_end"]
            accepted = second % c["period"] == 0 and connected and n[3] <= c["max_delay"]
            if accepted:
                s["synced"] = second
                if c["slew"]:
                    s["pending"] = s["phase"] + n[4]
                else:
                    s["phase"] = -n[4]
            age = second if s["synced"] < 0 else second - s["synced"]
            uncertainty = (5000000000 if s["synced"] < 0 else n[3] // 2 + 1000) + age * n[2]
            if c["slew"]:
                uncertainty += abs(s["pending"])
            within = abs(s["phase"]) <= uncertainty
            trusted = s["synced"] >= 0 and age <= c["holdover"] and within
            mode = (
                0
                if s["synced"] < 0
                else 4
                if not within
                else 3
                if age > c["holdover"]
                else 2
                if not connected or age >= c["period"]
                else 1
            )
            wall = second * 1000000000 + s["phase"]
            columns[node].append(
                [
                    second,
                    node,
                    wall,
                    s["phase"],
                    uncertainty,
                    age,
                    s["pending"],
                    int(accepted),
                    int(within),
                    int(trusted),
                    int(second > 0 and wall < s["wall"]),
                    mode,
                ]
            )
            s["wall"] = wall
    return [row for series in columns for row in series]


def audit_reference(events: list[list[int]]) -> dict[str, Any]:
    """Compare closed intervals with set qualification; separate arrival disorder from source order."""
    pairs = []
    for index, a in enumerate(events):
        for b in events[index + 1 :]:
            code = (
                3
                if not (a[5] and b[5])
                else 0
                if a[3] + a[4] < b[3] - b[4]
                else 1
                if b[3] + b[4] < a[3] - a[4]
                else 2
            )
            pairs.append([a[0], b[0], code])
    last: dict[int, int] = {}
    disorder = 0
    for e in events:
        disorder += int(e[1] in last and e[2] < last[e[1]])
        last[e[1]] = e[2]
    ordered = sorted(events, key=lambda e: (e[1], e[2]))
    regressions = [
        [a[0], b[0]]
        for a, b in zip(ordered, ordered[1:], strict=False)
        if a[1] == b[1] and b[3] < a[3]
    ]
    return {"pairs": pairs, "arrival_disorder": disorder, "regressions": regressions}
