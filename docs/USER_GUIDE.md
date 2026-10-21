# CHRONICLE user guide

Created by Jason Stys. Start with the default reference-blackout case.

1. Launch the extracted app or source CLI. Keep its console open; Ctrl+C stops its own local server. The browser address is loopback, not a public hosted website.
2. Read the exact-reference verification status before interpreting evidence. Controls changing hide previous results until **Run experiment** completes.
3. In the phase plot, blue is actual simulated error and copper shading is the assumed symmetric bound. Both share milliseconds vertically and elapsed seconds horizontally. Select A/B/C to inspect different invented oscillators.
4. Scrub elapsed time, or focus the slider and use arrow keys. The exact inspector shows phase, bound, age, pending correction, mode and qualification. At 180 seconds in the default blackout, the last reference is too old; an interval can remain numerically inside its bound yet be unqualified.
5. Choose two events. If their intervals overlap or touch, strict ordering is ambiguous. If either time quality is unqualified, no supported order claim is made. Even a definite time order does not prove causality.
6. Inspect the first 18 arrival observations in the table. On a narrow screen, tab to the named scrollable region to move through the wide table with your keyboard. Full JSON retains every event and pair.
7. Download JSON/CSV/HTML/input through the visible links. They refer to the accepted experiment settings, not an unrun control change. Save user files outside Git.

## Useful comparisons

- **Backward clock step:** the positive node-A jump at second 61 is followed by a backward immediate correction at second 90. Select slew instead to compare a capped pending correction. One-second regression counts and 30-second event-subset regressions are intentionally distinct.
- **Reference blackout:** opportunities from 60 through 180 seconds are unavailable; the next accepted normal reference is 210. The holdover age limit is inclusive at 120 seconds.
- **Asymmetric path:** known path biases produce opposite residual phase offsets. Node C's 12 ms path is rejected by the 5 ms gate; widening the gate accepts it with a larger bound, not magically greater precision.
- **1 ms gate:** every default 2 ms path is rejected; acquisition fails and all pairs are unqualified. This is not a zero-error clock.
- **Out-of-envelope oscillator:** the assumed tolerance is deliberately wrong. Truth-based instrumentation exposes it; real systems need separate calibration/assurance to know a bound is invalid.
- **Reordered telemetry:** the fictional arrival list is reversed. Source sequences remain intact; arrival order must not be confused with timestamp order or causality.

## Privacy and troubleshooting

No account, telemetry, remote clock, external AI, ads, browser storage or browser uploads. The app does not alter host clocks. Optional CLI SQLite histories are unencrypted and not protected from an OS user with file access; no automatic pruning/backups occur. Browser results are not persistent unless explicitly downloaded.

No evidence on failure is intentional. Check source builds for both fixed native workers and built web assets; do not substitute a different executable to hide a disagreement. If a port is occupied, omit `--port` for an ephemeral one rather than stopping another app. Verify unsigned download hashes and respect OS warnings. Do not disable endpoint protection.

Custom scenarios follow [API](API.md); parameter limits are not claims of real oscillator calibration. Read [MODEL](MODEL.md) before interpreting timing bounds. [Help/issues](https://github.com/JasonStys/mission-clock-integrity-lab/issues) · [Jason Stys/contact](https://github.com/JasonStys). Share only synthetic reproductions and non-sensitive output.
