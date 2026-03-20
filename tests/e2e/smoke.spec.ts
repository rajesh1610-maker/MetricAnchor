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

test("homepage loads without error", async ({ page }) => {
  const response = await page.goto(BASE);
  expect(response?.status()).toBeLessThan(400);
  await expect(page).not.toHaveTitle(/Error/);
});

// ── Datasets page ──────────────────────────────────────────────────────────────

test("datasets page loads dataset list", async ({ page }) => {
  const response = await page.goto(`${BASE}/datasets`);
  expect(response?.status()).toBeLessThan(400);
  const title = await page.title();
  expect(title).not.toMatch(/500|Error/);
});

// ── Ask page ───────────────────────────────────────────────────────────────────

test("ask page loads successfully", async ({ page }) => {
  const response = await page.goto(`${BASE}/ask`);
  expect(response?.status()).toBeLessThan(400);
  await expect(page).not.toHaveTitle(/Error/);
});

// ── Semantic models page ───────────────────────────────────────────────────────

test("semantic models page loads", async ({ page }) => {
  const response = await page.goto(`${BASE}/semantic-models`);
  expect(response?.status()).toBeLessThan(400);
  const title = await page.title();
  expect(title).not.toMatch(/500|Error/);
});

// ── Navigation links ───────────────────────────────────────────────────────────

test("can navigate from datasets to ask page", async ({ page }) => {
  await page.goto(`${BASE}/datasets`);
  await page.waitForLoadState("networkidle");

  const askLink = page.locator('a[href*="/ask"]').first();
  if (await askLink.isVisible()) {
    await askLink.click();
    await page.waitForLoadState("networkidle");
    expect(page.url()).toContain("/ask");
  }
});

// ── API health from browser ────────────────────────────────────────────────────

test("API health endpoint returns OK", async ({ request }) => {
  const response = await request.get("http://localhost:8000/api/health");
  expect(response.status()).toBe(200);
  const body = await response.json();
  expect(body.status).toBe("ok");
});
