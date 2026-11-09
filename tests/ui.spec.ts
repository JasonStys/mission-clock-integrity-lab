/** Actual instrument, reports, failures and accessibility by Jason Stys. Symbols: docs/CODE_INDEX.md. */
import { test, expect, type Page } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { readFile } from "node:fs/promises";
/** Wait for actual dual-native evidence, not a static preview placeholder. */
async function ready(page: Page) {
  await expect(page.locator("#status")).toContainText("Verified ·");
}
test("qualified partial-order review keeps uncertainty separate from order", async ({
  page,
  request,
}) => {
  await page.goto("/");
  await ready(page);
  await expect(page.locator("#order-review")).toContainText("Touching stays unordered");
  await expect(page.locator("#order-review")).toContainText("not total-order ranks");
  await page.locator("#order-review summary").click();
  await expect(page.locator("#order-review details")).toContainText("unordered qualified");
  const run = await (await request.get("/api/run")).json();
  expect(run.order_review.qualified.length + run.order_review.unqualified.length).toBe(
    run.events.length,
  );
  expect(run.order_review.frontiers.flat().sort((a: number, b: number) => a - b)).toEqual(
    run.order_review.qualified,
  );
});
test("real native/reference evidence, author and unique IDs", async ({ page }) => {
  await page.goto("/");
  await ready(page);
  await expect(page.getByRole("heading", { name: "Same event. Different clocks." })).toBeVisible();
  await expect(page.locator("#showing")).toContainText("reference-loss");
  const ids = await page.locator("[id]").evaluateAll((elements) => elements.map((e) => e.id));
  expect(new Set(ids).size).toBe(ids.length);
  const image = await page.locator("#plot").screenshot();
  expect(image.length).toBeGreaterThan(5000);
  await expect(page.getByRole("link", { name: "Jason Stys ↗", exact: true })).toHaveAttribute(
    "href",
    "https://github.com/JasonStys",
  );
});
test("step and slew produce distinct real regression evidence", async ({ page }) => {
  await page.goto("/");
  await ready(page);
  await page.locator("#scenario").selectOption("clock-step");
  await expect(page.locator("#evidence")).toBeHidden();
  await page.getByRole("button", { name: "Run experiment" }).click();
  await ready(page);
  await expect(page.locator("#regressions")).toHaveText("1");
  await page.locator("#policy").selectOption("1");
  await page.getByRole("button", { name: "Run experiment" }).click();
  await ready(page);
  await expect(page.locator("#regressions")).toHaveText("0");
});
test("overlap is ambiguous and reference rejection is unqualified", async ({ page }) => {
  await page.goto("/");
  await ready(page);
  await expect(page.locator("#pair-result")).toContainText("Ambiguous");
  await page.locator("#gate").selectOption("1000000");
  await page.getByRole("button", { name: "Run experiment" }).click();
  await ready(page);
  await expect(page.locator("#unqualified")).toHaveText("351");
  await expect(page.locator("#pair-result")).toContainText("Unqualified");
});
test("reordered arrivals remain separate from source-time regressions", async ({ page }) => {
  await page.goto("/");
  await ready(page);
  await page.locator("#scenario").selectOption("arrival-disorder");
  await page.getByRole("button", { name: "Run experiment" }).click();
  await ready(page);
  await expect(page.locator("#arrival-note")).toContainText("24 adjacent");
  await expect(page.locator("#events tr").first()).toContainText("E26");
  await expect(page.locator("#regressions")).toHaveText("0");
});
test("synthetic envelope violations are explicit", async ({ page }) => {
  await page.goto("/");
  await ready(page);
  await page.locator("#scenario").selectOption("oscillator-fault");
  await page.getByRole("button", { name: "Run experiment" }).click();
  await ready(page);
  await expect(page.locator("#envelope-note")).not.toContainText("0 synthetic");
  await page.locator("#tick").fill("120");
  await expect(page.locator("#inspection")).toContainText("Synthetic envelope violation");
});
test("all four actual exports retain accepted parameters and results", async ({ page }) => {
  await page.goto("/");
  await ready(page);
  for (const kind of ["JSON", "CSV", "HTML", "INPUT"]) {
    console.info(`Checking actual ${kind} download`);
    await expect(page.getByRole("link", { name: kind + " ↓", exact: true })).toHaveAttribute(
      "download",
      "",
    );
    const waiting = page.waitForEvent("download");
    await page.getByRole("link", { name: kind + " ↓", exact: true }).click();
    const download = await waiting;
    const path = await download.path();
    expect(path).toBeTruthy();
    const body = await readFile(path!, "utf8");
    if (kind === "JSON") {
      const r = JSON.parse(body);
      expect(r.samples.length).toBe(723);
      expect(r.summary.false_definite_claims).toBe(0);
    } else if (kind === "CSV") expect(body.trim().split("\n").length).toBe(724);
    else if (kind === "HTML") {
      expect(body).toContain("Jason Stys");
      expect(body).not.toContain("<script");
    } else expect(JSON.parse(body).name).toBe("reference-loss");
  }
});
test("failed or hostile evidence is hidden and retry works", async ({ page }) => {
  await page.goto("/");
  await ready(page);
  await page.route("**/api/run?**", (route) => route.fulfill({ status: 500, body: "failure" }));
  await page.getByRole("button", { name: "Run experiment" }).click();
  await expect(page.locator("#status")).toContainText("No verified evidence");
  await expect(page.locator("#evidence")).toBeHidden();
  await page.unroute("**/api/run?**");
  await page.route("**/api/run?**", async (route) => {
    const response = await route.fetch();
    const r = await response.json();
    r.name = '<img src=x onerror="alert(1)">';
    await route.fulfill({ json: r });
  });
  await page.getByRole("button", { name: "Run experiment" }).click();
  await expect(page.locator("#status")).toContainText("No verified evidence");
  await expect(page.locator("img")).toHaveCount(0);
  await page.unroute("**/api/run?**");
  await page.getByRole("button", { name: "Run experiment" }).click();
  await ready(page);
});
test("mobile layout, keyboard inspector and accessibility", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  await ready(page);
  const width = await page.evaluate(() => ({
    body: document.documentElement.scrollWidth,
    viewport: innerWidth,
  }));
  expect(width.body).toBeLessThanOrEqual(width.viewport);
  await page.locator("#tick").focus();
  await page.keyboard.press("ArrowRight");
  await expect(page.locator("#tick-label")).toHaveText("1 s");
  await page.locator("#node").selectOption("1");
  await expect(page.locator("#inspection")).toContainText("phase");
  await page.getByRole("region", { name: "Scrollable event arrivals" }).focus();
  await expect(page.getByRole("region", { name: "Scrollable event arrivals" })).toBeFocused();
  const results = await new AxeBuilder({ page })
    .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
    .analyze();
  expect(results.violations).toEqual([]);
});
/** A late response must not resurrect settings that the user has already changed. */
test("late responses cannot restore stale experiment evidence", async ({ page }) => {
  await page.goto("/");
  await ready(page);
  let release!: () => void;
  const gate = new Promise<void>((resolve) => {
    release = resolve;
  });
  let received!: () => void;
  const pending = new Promise<void>((resolve) => {
    received = resolve;
  });
  await page.route("**/api/run?**", async (route) => {
    const response = await route.fetch();
    received();
    await gate;
    await route.fulfill({ response });
  });
  await page.getByRole("button", { name: "Run experiment" }).click();
  await pending;
  await page.locator("#scenario").selectOption("nominal");
  const completed = page.waitForResponse((response) => response.url().includes("/api/run?"));
  release();
  await completed;
  await expect(page.locator("#evidence")).toBeHidden();
  await expect(page.locator("#status")).toContainText("Controls changed");
  await page.unroute("**/api/run?**");
  await page.getByRole("button", { name: "Run experiment" }).click();
  await ready(page);
  await expect(page.locator("#showing")).toContainText("nominal");
});
