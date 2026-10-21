/** CHRONICLE browser instrument by Jason Stys; functions, state and DOM locations: docs/CODE_INDEX.md. */
import "./style.css";
import { milliseconds, parseRun, relation, type Run } from "./contracts";
document.querySelector<HTMLDivElement>("#app")!.innerHTML = /* HTML */ ` <a
    class="skip"
    href="#instrument"
    >Skip to timing instrument</a
  >
  <header>
    <a class="brand" href="#instrument"
      ><span class="brand-mark">◷</span> CHRONICLE <small>MISSION CLOCK INTEGRITY LAB</small></a
    >
    <nav aria-label="Project">
      <a href="#method">How it works</a
      ><a href="https://github.com/JasonStys/mission-clock-integrity-lab">Source ↗</a
      ><a href="https://github.com/JasonStys">Jason Stys ↗</a>
    </nav>
  </header>
  <main id="instrument">
    <section class="intro">
      <div>
        <p class="eyebrow">TIMING / ASSUMPTIONS / EVIDENCE</p>
        <h1>Same event.<br /><em>Different clocks.</em></h1>
        <p class="lede">
          Lose a reference. Watch uncertainty grow. Discover when a timestamp can tell you the
          order—and when it cannot.
        </p>
      </div>
      <aside>
        <span class="pill">OFFLINE · SYNTHETIC · VERIFIED</span>
        <p>One-second ticks.<br />Integer nanoseconds.<br />No changes to your computer clock.</p>
      </aside>
    </section>
    <form id="controls" aria-label="Experiment controls">
      <label
        >Scenario<select id="scenario">
          <option value="reference-loss">Reference blackout</option>
          <option value="nominal">Stable reference</option>
          <option value="asymmetric-path">Asymmetric path</option>
          <option value="clock-step">Backward clock step</option>
          <option value="oscillator-fault">Out-of-envelope oscillator</option>
          <option value="arrival-disorder">Reordered telemetry</option>
        </select></label
      ><label
        >Correction policy<select id="policy">
          <option value="0">Step / immediate</option>
          <option value="1">Slew / rate-limited</option>
        </select></label
      ><label
        >Oscillator bound<select id="tolerance">
          <option value="1">1× / 2,500 ppb</option>
          <option value="2">2× / 5,000 ppb</option>
          <option value="4">4× / 10,000 ppb</option>
        </select></label
      ><label
        >Round-trip gate<select id="gate">
          <option value="5000000">5 ms</option>
          <option value="1000000">1 ms / reject paths</option>
          <option value="50000000">50 ms</option>
        </select></label
      ><label
        >Duration<select id="duration">
          <option value="240">240 seconds</option>
          <option value="600">600 seconds</option>
        </select></label
      ><button id="run" type="submit">Run experiment ↗</button>
    </form>
    <p id="status" role="status" aria-live="polite">Preparing the independent verifiers…</p>
    <div id="evidence" hidden>
      <div class="metrics">
        <div>
          <span>DEFINITE ORDER PAIRS</span><strong id="definite"></strong
          ><small>strictly separated intervals</small>
        </div>
        <div>
          <span>AMBIGUOUS PAIRS</span><strong id="ambiguous"></strong
          ><small>overlapping / touching bounds</small>
        </div>
        <div>
          <span>UNQUALIFIED PAIRS</span><strong id="unqualified"></strong
          ><small>missing or invalid time quality</small>
        </div>
        <div>
          <span>BACKWARD WALL STEPS</span><strong id="regressions"></strong
          ><small>one-second source sampling</small>
        </div>
      </div>
      <section class="panel">
        <div class="section-head">
          <div>
            <p class="eyebrow">01 / PHASE AND HOLDOVER</p>
            <h2>The reference disappears.<br />The clock keeps ticking.</h2>
          </div>
          <label
            >Inspect clock<select id="node">
              <option value="0">A / +1,000 ppb</option>
              <option value="1">B / −2,000 ppb</option>
              <option value="2">C / +500 ppb</option>
            </select></label
          >
        </div>
        <p id="showing" class="muted"></p>
        <canvas
          id="plot"
          width="1000"
          height="320"
          role="img"
          aria-label="Clock phase error and symmetric uncertainty envelope over simulated elapsed time; exact values available in inspector and CSV"
        ></canvas>
        <div class="legend">
          <span><i class="line"></i>Actual synthetic phase error</span
          ><span><i class="band"></i>Assumed ± error bound</span
          ><span>Vertical axis: milliseconds · horizontal: elapsed seconds</span>
        </div>
        <label class="scrub"
          >Inspect elapsed second <output id="tick-label">0 s</output
          ><input id="tick" type="range" min="0" max="240" value="0"
        /></label>
        <div id="inspection" class="inspection" aria-live="polite"></div>
        <p id="envelope-note" class="notice"></p>
      </section>
      <section class="panel order-panel">
        <div>
          <p class="eyebrow">02 / ORDER IS NOT CAUSALITY</p>
          <h2>What can these<br />timestamps prove?</h2>
          <p>
            Each interval is wall time ± its modeled bound. Touching or overlapping intervals do not
            establish strict order. A scalar sort conceals that ambiguity.
          </p>
          <p class="notice">
            Qualification uses known simulation truth to flag out-of-envelope errors. A real clock
            cannot discover its true offset this way.
          </p>
        </div>
        <div>
          <div class="pair-controls">
            <label>Event A<select id="left-event"></select></label
            ><label>Event B<select id="right-event"></select></label>
          </div>
          <div id="pair-result" aria-live="polite"></div>
          <p id="arrival-note" class="muted"></p>
        </div>
      </section>
      <section class="panel">
        <div class="section-head">
          <div>
            <p class="eyebrow">03 / ARRIVAL ≠ EVENT TIME</p>
            <h2>A trace you can inspect.</h2>
          </div>
          <p class="muted">First 18 arrivals shown.<br />All observations travel with the JSON.</p>
        </div>
        <div class="table-wrap" tabindex="0" role="region" aria-label="Scrollable event arrivals">
          <table>
            <caption>
              Event arrival excerpt; ns are elapsed simulation coordinates, not UTC.
            </caption>
            <thead>
              <tr>
                <th>Event</th>
                <th>Clock</th>
                <th>Source second</th>
                <th>Wall / ms</th>
                <th>Bound / ms</th>
                <th>Quality</th>
              </tr>
            </thead>
            <tbody id="events"></tbody>
          </table>
        </div>
      </section>
      <section class="export">
        <div>
          <p class="eyebrow">04 / REPRODUCIBLE EVIDENCE</p>
          <h2>Keep the assumptions<br />with the result.</h2>
          <p>
            Complete samples, interval audit, input parameters, reference checks and limitations.
            Local SQL history is opt-in through the CLI, not a hidden browser write.
          </p>
          <div id="downloads" class="downloads"></div>
        </div>
        <div>
          <span class="eyebrow">REPORT SHA-256</span><code id="identity"></code>
          <p class="muted">
            No account, telemetry, external clock source or remote storage. No NTP/PTP packets are
            sent.
          </p>
        </div>
      </section>
    </div>
    <section id="method" class="method">
      <p class="eyebrow">METHOD / THE BOUND IS AN ASSUMPTION</p>
      <h2>Precision is a number.<br /><em>Trust needs a reason.</em></h2>
      <div class="method-grid">
        <article>
          <h3>01 · Separate timescales</h3>
          <p>
            All time is synthetic elapsed SI-like seconds. Wall readings can step backward; source
            sequence is a separate ordering signal. UTC, leap seconds and relativistic effects are
            not modeled.
          </p>
        </article>
        <article>
          <h3>02 · Qualify the envelope</h3>
          <p>
            Path delay, frequency tolerance and pending slew contribute to the bound. It is
            deterministic bookkeeping—not a confidence interval, measured oscillator calibration or
            certified UTC accuracy.
          </p>
        </article>
        <article>
          <h3>03 · Verify the software</h3>
          <p>
            C++ evolves clocks. Rust compares closed intervals. Independent Python implementations
            must agree exactly before evidence is displayed. Agreement is not flight qualification.
          </p>
        </article>
      </div>
      <p>
        <a
          href="https://github.com/JasonStys/mission-clock-integrity-lab/blob/main/docs/USER_GUIDE.md"
          >User guide ↗</a
        >
        ·
        <a href="https://github.com/JasonStys/mission-clock-integrity-lab/issues"
          >Help / report an issue ↗</a
        >
      </p>
    </section>
  </main>
  <footer>
    <span>Designed and engineered by <a href="https://github.com/JasonStys">Jason Stys</a></span
    ><span>CIVILIAN TIMING EDUCATION · NO ENDORSEMENT</span>
  </footer>`;
/** Resolve owned template elements once by unique ID. */
function element<T extends HTMLElement>(id: string): T {
  return document.getElementById(id) as T;
}
let current: Run | null = null;
let requestVersion = 0;
const status = element("status"),
  evidence = element("evidence"),
  form = element<HTMLFormElement>("controls"),
  button = element<HTMLButtonElement>("run");
const selected = () => Number(element<HTMLSelectElement>("node").value);
/** Construct preset query only from allowlisted controls; exports retain accepted report settings. */
function query(): URLSearchParams {
  return new URLSearchParams(
    ["scenario", "policy", "tolerance", "gate", "duration"].map((key) => [
      key,
      element<HTMLSelectElement>(key).value,
    ]),
  );
}
/** Draw actual integer evidence with a common symmetric axis, never an invented animation. */
function draw(): void {
  if (!current) return;
  const canvas = element<HTMLCanvasElement>("plot"),
    ctx = canvas.getContext("2d")!;
  const rows = current.samples.filter((r) => r[1] === selected());
  const max = Math.max(1, ...rows.map((r) => Math.max(Math.abs(r[3]!), r[4]!))) * 1.08;
  const x = (t: number) => 60 + (t / rows.at(-1)![0]!) * 920,
    y = (ns: number) => 155 - (ns / max) * 125;
  ctx.clearRect(0, 0, 1000, 320);
  ctx.font = "13px monospace";
  ctx.lineWidth = 1;
  for (const f of [-1, 0, 1]) {
    ctx.strokeStyle = "#d6d9d8";
    ctx.beginPath();
    ctx.moveTo(60, y(max * f));
    ctx.lineTo(980, y(max * f));
    ctx.stroke();
    ctx.fillStyle = "#4d5d66";
    ctx.fillText(milliseconds(max * f), 2, y(max * f) - 5);
  }
  ctx.fillStyle = "rgba(186,116,70,.20)";
  ctx.beginPath();
  rows.forEach((r, i) => (i ? ctx.lineTo(x(r[0]!), y(r[4]!)) : ctx.moveTo(x(r[0]!), y(r[4]!))));
  [...rows].reverse().forEach((r) => ctx.lineTo(x(r[0]!), y(-r[4]!)));
  ctx.closePath();
  ctx.fill();
  ctx.strokeStyle = "#174d67";
  ctx.lineWidth = 2.5;
  ctx.beginPath();
  rows.forEach((r, i) => (i ? ctx.lineTo(x(r[0]!), y(r[3]!)) : ctx.moveTo(x(r[0]!), y(r[3]!))));
  ctx.stroke();
  ctx.fillStyle = "#4d5d66";
  for (let i = 0; i <= 4; i++) {
    const t = (rows.at(-1)![0]! * i) / 4;
    ctx.fillText(`${t} s`, Math.min(950, x(t) - 10), 304);
  }
  const tick = Number(element<HTMLInputElement>("tick").value);
  ctx.strokeStyle = "#a3572f";
  ctx.setLineDash([4, 4]);
  ctx.beginPath();
  ctx.moveTo(x(tick), 20);
  ctx.lineTo(x(tick), 285);
  ctx.stroke();
  ctx.setLineDash([]);
}
/** Update exact sample inspector, including simulation-only validity and correction state. */
function inspect(): void {
  if (!current) return;
  const t = Number(element<HTMLInputElement>("tick").value),
    row = current.samples.find((r) => r[0] === t && r[1] === selected())!;
  const modes = [
    "Acquiring / no accepted reference",
    "Reference available",
    "Holdover",
    "Holdover limit exceeded",
    "Synthetic envelope violation",
  ];
  element("tick-label").textContent = `${t} s`;
  element("inspection").textContent =
    `${modes[row[11]!]} · phase ${milliseconds(row[3]!)} ms · bound ±${milliseconds(row[4]!)} ms · reference age ${row[5]} s · pending correction ${milliseconds(row[6]!)} ms · ${row[9] ? "qualified interval" : "unqualified interval"}`;
  draw();
}
/** Explain a chosen pair using the exact closed-interval relation, never scalar-sort certainty. */
function compare(): void {
  if (!current) return;
  const a = current.events.find(
      (e) => e[0] === Number(element<HTMLSelectElement>("left-event").value),
    )!,
    b = current.events.find(
      (e) => e[0] === Number(element<HTMLSelectElement>("right-event").value),
    )!;
  const code = relation(a, b),
    names = [
      "A is strictly before B",
      "B is strictly before A",
      "Ambiguous / intervals overlap or touch",
      "Unqualified / no supported time-order claim",
    ];
  element("pair-result").textContent =
    a[0] === b[0]
      ? "Select two different events."
      : `${names[code]}. A: [${milliseconds(a[3]! - a[4]!)}, ${milliseconds(a[3]! + a[4]!)}] ms. B: [${milliseconds(b[3]! - b[4]!)}, ${milliseconds(b[3]! + b[4]!)}] ms. Simulation source seconds: ${a[2]} and ${b[2]}. This is temporal order, not causality.`;
}
/** Render accepted bounded data through text nodes and same-origin download links. */
function render(run: Run): void {
  current = run;
  evidence.hidden = false;
  for (const [id, key] of [
    ["definite", "definite_pairs"],
    ["ambiguous", "ambiguous_pairs"],
    ["unqualified", "unqualified_pairs"],
    ["regressions", "wall_regressions"],
  ])
    element(id!).textContent = run.summary[key!]!.toLocaleString("en-US");
  element("showing").textContent =
    `Showing ${run.name} · ${run.samples.at(-1)![0]} s · ${run.settings?.policy === 1 ? "rate-limited slew" : "immediate steps"}. Both independent references passed.`;
  element("envelope-note").textContent =
    `${run.summary.envelope_violations} synthetic envelope violations; ${run.summary.unqualified_events} unqualified event intervals. An invalid assumed bound cannot certify time.`;
  element<HTMLInputElement>("tick").max = String(run.samples.at(-1)![0]);
  element<HTMLInputElement>("tick").value = "0";
  const options = run.events.map(
    (e) => new Option(`E${e[0]} / ${"ABCD"[e[1]!]} / ${e[2]} s`, String(e[0])),
  );
  for (const id of ["left-event", "right-event"]) {
    const control = element<HTMLSelectElement>(id);
    control.replaceChildren(...options.map((o) => o.cloneNode(true)));
  }
  element<HTMLSelectElement>("right-event").selectedIndex = Math.min(
    run.events.length - 1,
    Math.floor(run.events.length / 3),
  );
  element("arrival-note").textContent =
    `${run.audit.arrival_disorder} adjacent source-sequence decreases in arrival order. ${run.audit.regressions.length} wall-time regressions in the 30-second event subset. The one-second simulator checks a denser stream.`;
  element("events").replaceChildren(
    ...run.events.slice(0, 18).map((e) => {
      const tr = document.createElement("tr");
      for (const text of [
        `E${e[0]}`,
        "ABCD"[e[1]!]!,
        String(e[2]),
        milliseconds(e[3]!),
        milliseconds(e[4]!),
        e[5] ? "Qualified" : "Unqualified",
      ]) {
        const td = document.createElement("td");
        td.textContent = text;
        tr.append(td);
      }
      return tr;
    }),
  );
  element("identity").textContent = run.id;
  element("downloads").replaceChildren(
    ...["json", "csv", "html", "input"].map((kind) => {
      const a = document.createElement("a"),
        params = new URLSearchParams(
          Object.entries(run.settings ?? {}).map(([k, v]) => [k, String(v)]),
        );
      params.set("format", kind);
      a.href = "/api/report?" + params;
      a.textContent = kind.toUpperCase() + " ↓";
      return a;
    }),
  );
  inspect();
  compare();
}
/** Hide old evidence while checking new inputs; errors never leave an old chart presented as current. */
async function run(): Promise<void> {
  const version = ++requestVersion;
  current = null;
  evidence.hidden = true;
  button.disabled = true;
  status.textContent = "Checking C++ clocks and Rust event intervals against Python…";
  try {
    const response = await fetch("/api/run?" + query(), { signal: AbortSignal.timeout(15000) });
    if (!response.ok) throw new Error("Request failed");
    const data = await response.json();
    if (version !== requestVersion) return;
    render(parseRun(data));
    status.textContent =
      "Verified · clock samples and interval audit agree exactly with independent Python references.";
  } catch {
    if (version !== requestVersion) return;
    current = null;
    evidence.hidden = true;
    status.textContent =
      "No verified evidence available. Check local workers and retry. Old results have been hidden.";
  } finally {
    if (version === requestVersion) button.disabled = false;
  }
}
form.addEventListener("submit", (event) => {
  event.preventDefault();
  void run();
});
form.addEventListener("change", () => {
  requestVersion++;
  button.disabled = false;
  current = null;
  evidence.hidden = true;
  status.textContent = "Controls changed. Run the experiment to produce new verified evidence.";
});
element("node").addEventListener("change", inspect);
element("tick").addEventListener("input", inspect);
element("left-event").addEventListener("change", compare);
element("right-event").addEventListener("change", compare);
void run();
