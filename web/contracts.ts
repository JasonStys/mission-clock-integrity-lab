/** Defensive integer evidence contracts by Jason Stys. Functions/fields: docs/CODE_INDEX.md. */
export interface Run {
  id: string;
  name: string;
  columns: string[];
  samples: number[][];
  events: number[][];
  settings: {
    scenario: string;
    policy: number;
    tolerance: number;
    gate: number;
    duration: number;
  } | null;
  summary: Record<string, number>;
  audit: { pairs: number[][]; arrival_disorder: number; regressions: number[][] };
  order_review: {
    qualified: number[];
    unqualified: number[];
    cover_edges: number[][];
    frontiers: number[][];
    relations: {
      id: number;
      definitely_before: number[];
      definitely_after: number[];
      unordered_qualified: number[];
    }[];
  };
  method: { clock_reference_verified: boolean; order_reference_verified: boolean };
}
/** Verify records before drawing or indexing; no nonfinite, unsafe integer or unbounded arrays. */
export function parseRun(value: unknown): Run {
  const r = value as Partial<Run> | null;
  if (
    !r ||
    typeof r !== "object" ||
    !/^[a-f0-9]{64}$/.test(r.id ?? "") ||
    !/^[a-z0-9-]{1,48}$/.test(r.name ?? "") ||
    !r.method?.clock_reference_verified ||
    !r.method.order_reference_verified
  )
    throw new Error("Unverified evidence");
  const matrix = (rows: unknown, width: number, limit: number): rows is number[][] =>
    Array.isArray(rows) &&
    rows.length <= limit &&
    rows.every(
      (row) =>
        Array.isArray(row) &&
        row.length === width &&
        row.every((x) => Number.isSafeInteger(x) && Math.abs(x) <= 9e12),
    );
  if (
    !matrix(r.samples, 12, 2404) ||
    !r.samples.length ||
    !matrix(r.events, 6, 96) ||
    !r.events.length ||
    !r.audit ||
    !matrix(r.audit.pairs, 3, 4560) ||
    !matrix(r.audit.regressions, 2, 96) ||
    !r.summary ||
    Object.values(r.summary).some((x) => !Number.isSafeInteger(x) || x < 0)
  )
    throw new Error("Invalid evidence shape");
  const required = [
    "samples",
    "events",
    "pairs",
    "definite_pairs",
    "ambiguous_pairs",
    "unqualified_pairs",
    "arrival_disorder",
    "wall_regressions",
    "envelope_violations",
    "max_abs_offset_ns",
    "peak_bound_ns",
    "unqualified_events",
    "false_definite_claims",
  ];
  if (
    required.some((key) => r.summary?.[key] === undefined) ||
    r.summary.samples !== r.samples.length ||
    r.summary.events !== r.events.length ||
    r.summary.pairs !== r.audit.pairs.length ||
    r.summary.false_definite_claims !== 0
  )
    throw new Error("Invalid accounting");
  if (
    r.samples.some(
      (row) =>
        row[0]! < 0 ||
        row[0]! > 600 ||
        row[1]! < 0 ||
        row[1]! > 3 ||
        row[4]! < 0 ||
        row.slice(7, 11).some((x) => x !== 0 && x !== 1) ||
        row[11]! < 0 ||
        row[11]! > 4,
    )
  )
    throw new Error("Invalid sample");
  const ids = new Set(r.events.map((row) => row[0]));
  if (
    ids.size !== r.events.length ||
    r.events.some((e) => e[4]! < 0 || (e[5] !== 0 && e[5] !== 1)) ||
    r.audit.pairs.some(
      (p) => !ids.has(p[0]) || !ids.has(p[1]) || p[0] === p[1] || p[2]! < 0 || p[2]! > 3,
    )
  )
    throw new Error("Invalid event audit");
  if (
    !Array.isArray(r.columns) ||
    r.columns.length !== 12 ||
    r.columns.some((s) => typeof s !== "string" || s.length > 32)
  )
    throw new Error("Invalid columns");
  if (
    r.settings !== null &&
    (!r.settings ||
      typeof r.settings.scenario !== "string" ||
      ![0, 1].includes(r.settings.policy) ||
      ![1, 2, 4].includes(r.settings.tolerance) ||
      ![1e6, 5e6, 5e7].includes(r.settings.gate) ||
      ![240, 600].includes(r.settings.duration))
  )
    throw new Error("Invalid settings");
  return r as Run;
}
/** Strictly separated closed intervals establish order; equality/overlap does not. */
export function relation(a: number[], b: number[]): number {
  return !a[5] || !b[5]
    ? 3
    : a[3]! + a[4]! < b[3]! - b[4]!
      ? 0
      : b[3]! + b[4]! < a[3]! - a[4]!
        ? 1
        : 2;
}
/** Render raw integer nanoseconds as display milliseconds, never modifying analytical evidence. */
export function milliseconds(ns: number): string {
  return (ns / 1e6).toLocaleString("en-US", { maximumFractionDigits: 4 });
}
