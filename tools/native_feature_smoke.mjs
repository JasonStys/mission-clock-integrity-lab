/**
 * Frozen dual-native timestamp review acceptance by Jason Stys.
 * Function: runNativeJourney callback; variables: qualified intervals, relations and frontiers.
 * Checks integer timestamp separation only; no real clocks or causal ordering claims.
 * Symbol locations: docs/CODE_INDEX.md.
 */
import assert from "node:assert/strict";
import { expect } from "@playwright/test";
import { runNativeJourney } from "./native_browser.mjs";

await runNativeJourney(async ({ page, request }) => {
  await page.goto("/");
  await expect(page.locator("#status")).toContainText("Verified ·");
  await expect(page.locator("#order-review")).toContainText("Touching stays unordered");
  await page.locator("#order-review summary").click();
  await expect(page.locator("#order-review details")).toContainText("unordered qualified");
  const response = await request.get("/api/run");
  assert.equal(response.status(), 200);
  const report = await response.json();
  const review = report.order_review;
  const qualified = report.events.filter((event) => event[5] === 1);
  assert.deepEqual(
    review.qualified,
    qualified.map((event) => event[0]).sort((a, b) => a - b),
  );
  assert.equal(review.qualified.length + review.unqualified.length, report.events.length);
  assert.deepEqual(
    review.frontiers.flat().sort((a, b) => a - b),
    review.qualified,
  );
  for (const relation of review.relations) {
    const current = qualified.find((event) => event[0] === relation.id);
    const before = qualified.filter((event) => current[3] + current[4] < event[3] - event[4]);
    const after = qualified.filter((event) => event[3] + event[4] < current[3] - current[4]);
    assert.deepEqual(
      relation.definitely_before,
      before.map((event) => event[0]).sort((a, b) => a - b),
    );
    assert.deepEqual(
      relation.definitely_after,
      after.map((event) => event[0]).sort((a, b) => a - b),
    );
  }
  for (const [a, b] of review.cover_edges) {
    const first = qualified.find((event) => event[0] === a);
    const second = qualified.find((event) => event[0] === b);
    assert.ok(first[3] + first[4] < second[3] - second[4]);
  }
  const exported = await request.get("/api/report?format=json");
  assert.equal(exported.status(), 200);
  assert.match(exported.headers()["content-disposition"], /attachment/u);
  assert.deepEqual((await exported.json()).order_review, review);
});
