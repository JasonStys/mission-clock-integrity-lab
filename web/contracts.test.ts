/** Client contracts and interval boundary tests by Jason Stys. Identifiers: docs/CODE_INDEX.md. */
import { describe, it, expect } from "vitest";
import { milliseconds, parseRun, relation } from "./contracts";
/** Minimal valid bounded report for client guard tests, not numerical-model evidence. */
function fixture() {
  return {
    id: "a".repeat(64),
    name: "test",
    columns: Array(12).fill("sample"),
    samples: [[0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 1]],
    events: [[0, 0, 0, 0, 0, 1]],
    settings: null,
    method: { clock_reference_verified: true, order_reference_verified: true },
    audit: { pairs: [], arrival_disorder: 0, regressions: [] },
    summary: {
      samples: 1,
      events: 1,
      pairs: 0,
      definite_pairs: 0,
      ambiguous_pairs: 0,
      unqualified_pairs: 0,
      arrival_disorder: 0,
      wall_regressions: 0,
      envelope_violations: 0,
      max_abs_offset_ns: 0,
      peak_bound_ns: 0,
      unqualified_events: 0,
      false_definite_claims: 0,
    },
  };
}
describe("evidence guard", () => {
  it("accepts bounded independently verified data", () =>
    expect(parseRun(fixture()).name).toBe("test"));
  it("rejects absent/unverified/hostile identity", () => {
    for (const x of [
      null,
      {},
      { ...fixture(), name: "<img>" },
      { ...fixture(), id: "bad" },
      { ...fixture(), method: { clock_reference_verified: false } },
    ])
      expect(() => parseRun(x)).toThrow();
  });
  it("rejects nonfinite/unsafe/oversized sample matrices", () => {
    for (const value of [NaN, Infinity, 9e15]) {
      const r = fixture();
      r.samples[0]![2] = value;
      expect(() => parseRun(r)).toThrow();
    }
    expect(() =>
      parseRun({ ...fixture(), samples: Array(2405).fill(fixture().samples[0]) }),
    ).toThrow();
  });
  it("rejects invalid accounting and classifications", () => {
    const r = fixture();
    r.summary.samples = 2;
    expect(() => parseRun(r)).toThrow();
    const q = fixture();
    q.samples[0]![7] = 2;
    expect(() => parseRun(q)).toThrow();
  });
  it("rejects event references and unsupported settings", () => {
    expect(() =>
      parseRun({
        ...fixture(),
        audit: { pairs: [[0, 2, 0]], regressions: [], arrival_disorder: 0 },
        summary: { ...fixture().summary, pairs: 1 },
      }),
    ).toThrow();
    expect(() => parseRun({ ...fixture(), settings: { scenario: "test", policy: 8 } })).toThrow();
  });
});
describe("closed intervals", () => {
  it("does not claim strict order at a shared endpoint", () =>
    expect(relation([0, 0, 0, 0, 2, 1], [1, 1, 1, 4, 2, 1])).toBe(2));
  it("distinguishes before and after symmetrically", () => {
    expect(relation([0, 0, 0, 0, 2, 1], [1, 1, 1, 5, 2, 1])).toBe(0);
    expect(relation([0, 0, 0, 5, 2, 1], [1, 1, 1, 0, 2, 1])).toBe(1);
  });
  it("does not qualify an unavailable time", () =>
    expect(relation([0, 0, 0, -10, 0, 0], [1, 1, 1, 4, 0, 1])).toBe(3));
  it("formats milliseconds without changing evidence", () =>
    expect(milliseconds(1234500)).toBe("1.2345"));
});
