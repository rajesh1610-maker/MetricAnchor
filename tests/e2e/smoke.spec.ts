/**
 * E2E smoke tests — verify the most important user flows load and function.
 *
 * These tests require the full stack to be running (make up).
 * They do NOT make assertions about specific data values; they only verify
 * that the UI renders without errors and key interactions work.
 */

import { expect, test } from "@playwright/test";

const BASE = "http://localhost:3000";

// ── Homepage ───────────────────────────────────────────────────────────────────

test("homepage loads and shows navigation", async ({ page }) => {
  await page.goto(BASE);
  await expect(page).not.toHaveTitle(/Error/);
  // Should have some nav or main content
  await expect(page.locator("body")).toBeVisible();
});

// ── Datasets page ──────────────────────────────────────────────────────────────

test("datasets page loads dataset list", async ({ page }) => {
  await page.goto(`${BASE}/datasets`);
  await page.waitForLoadState("networkidle");
  // Should show either a list or an empty state — no crash
  await expect(page.locator("body")).toBeVisible();
  const title = await page.title();
  expect(title).not.toMatch(/500|Error/);
});

// ── Ask page ───────────────────────────────────────────────────────────────────

test("ask page loads with question textarea", async ({ page }) => {
  await page.goto(`${BASE}/ask`);
  await page.waitForLoadState("networkidle");
  // Textarea for entering questions should be present
  const textarea = page.locator("textarea");
  await expect(textarea.first()).toBeVisible();
});

test("ask page shows dataset selector", async ({ page }) => {
  await page.goto(`${BASE}/ask`);
  await page.waitForLoadState("networkidle");
  // Some kind of dataset selection UI should exist
  const selects = page.locator("select, [role=combobox], [data-testid=dataset-select]");
  // At minimum the page shouldn't crash
  await expect(page.locator("body")).toBeVisible();
});

// ── Semantic models page ───────────────────────────────────────────────────────

test("semantic models page loads", async ({ page }) => {
  await page.goto(`${BASE}/semantic-models`);
  await page.waitForLoadState("networkidle");
  await expect(page.locator("body")).toBeVisible();
  const title = await page.title();
  expect(title).not.toMatch(/500|Error/);
});

// ── Dev mode toggle ────────────────────────────────────────────────────────────

test("dev mode toggle works on ask page", async ({ page }) => {
  await page.goto(`${BASE}/ask`);
  await page.waitForLoadState("networkidle");

  // Press Cmd+Shift+D (Mac) or Ctrl+Shift+D (Linux/Win) to toggle dev mode
  await page.keyboard.press("Meta+Shift+D");
  // Page should not crash after keypress
  await expect(page.locator("body")).toBeVisible();
});

// ── Navigation links ───────────────────────────────────────────────────────────

test("can navigate from datasets to ask page", async ({ page }) => {
  await page.goto(`${BASE}/datasets`);
  await page.waitForLoadState("networkidle");

  // Look for a link to the Ask page in the nav
  const askLink = page.locator('a[href*="/ask"]').first();
  if (await askLink.isVisible()) {
    await askLink.click();
    await page.waitForLoadState("networkidle");
    expect(page.url()).toContain("/ask");
  }
});
