import { chromium } from "playwright";
import path from "node:path";
import fs from "node:fs";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "../..");
const DOCS_DIR = path.join(ROOT, "docs");
const SCREENS_DIR = path.join(ROOT, "video/public/screens");

async function main() {
  fs.mkdirSync(DOCS_DIR, { recursive: true });
  fs.mkdirSync(SCREENS_DIR, { recursive: true });

  const browser = await chromium.launch({
    headless: true,
  });
  const context = await browser.newContext({
    viewport: { width: 1600, height: 1000 },
    deviceScaleFactor: 2,
  });

  const page = await context.newPage();
  const webUrl = `file://${path.join(ROOT, "web/index.html")}`;
  await page.goto(webUrl, { waitUntil: "networkidle" });
  await page.waitForTimeout(400);

  // 1. Top Command Center Hero (Header + KPIs + 4 Zetaris Disconnected Sources)
  const p1 = path.join(DOCS_DIR, "command-center.png");
  await page.screenshot({ path: p1, fullPage: false });
  fs.copyFileSync(p1, path.join(SCREENS_DIR, "command-center.png"));
  console.log("Captured command-center.png");

  // 2. Scroll to Agent Loop + World Model Conflict Matrix + Sourced Remediation Order
  await page.evaluate(() => {
    const el = document.querySelector(".main-split");
    if (el) el.scrollIntoView({ behavior: "instant", block: "start" });
    window.scrollBy(0, -16);
  });
  await page.waitForTimeout(250);
  const p2 = path.join(DOCS_DIR, "conflict-reconciliation.png");
  await page.screenshot({ path: p2, fullPage: false });
  fs.copyFileSync(p2, path.join(SCREENS_DIR, "conflict-reconciliation.png"));
  console.log("Captured conflict-reconciliation.png");

  // 3. Scroll to Bottom Telemetry Panel: Tab 1 = All 4 Meterless Engines
  await page.click('[data-tab="engines"]');
  await page.waitForTimeout(200);
  await page.evaluate(() => {
    const el = document.querySelector(".subtabs");
    if (el) el.scrollIntoView({ behavior: "instant", block: "start" });
    window.scrollBy(0, -24);
  });
  await page.waitForTimeout(250);
  const p3 = path.join(DOCS_DIR, "meterless-engines.png");
  await page.screenshot({ path: p3, fullPage: false });
  fs.copyFileSync(p3, path.join(SCREENS_DIR, "meterless-engines.png"));
  console.log("Captured meterless-engines.png");

  // 4. Tab 2 = Meterless Nightshift & NVIDIA Nemotron Receipts
  await page.click('[data-tab="nightshift"]');
  await page.waitForTimeout(200);
  await page.evaluate(() => {
    const el = document.querySelector(".subtabs");
    if (el) el.scrollIntoView({ behavior: "instant", block: "start" });
    window.scrollBy(0, -24);
  });
  await page.waitForTimeout(250);
  const p4 = path.join(DOCS_DIR, "nightshift-receipts.png");
  await page.screenshot({ path: p4, fullPage: false });
  fs.copyFileSync(p4, path.join(SCREENS_DIR, "nightshift-receipts.png"));
  console.log("Captured nightshift-receipts.png");

  // 5. Tab 3 = Zetaris Federated SQL Workbench
  await page.click('[data-tab="zetaris"]');
  await page.waitForTimeout(200);
  await page.evaluate(() => {
    const el = document.querySelector(".subtabs");
    if (el) el.scrollIntoView({ behavior: "instant", block: "start" });
    window.scrollBy(0, -24);
  });
  await page.waitForTimeout(250);
  const p5 = path.join(DOCS_DIR, "zetaris-sql.png");
  await page.screenshot({ path: p5, fullPage: false });
  fs.copyFileSync(p5, path.join(SCREENS_DIR, "zetaris-sql.png"));
  console.log("Captured zetaris-sql.png");

  await browser.close();
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
