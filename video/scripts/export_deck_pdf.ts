import { chromium } from "playwright";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "../..");

async function main() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({
    viewport: { width: 1280, height: 720 },
  });

  const deckUrl = `file://${path.join(ROOT, "docs/deck.html")}`;
  await page.goto(deckUrl, { waitUntil: "networkidle" });
  await page.addStyleTag({
    content: `
      @page { size: 1280px 720px; margin: 0; }
      body { padding: 0 !important; background: #090d14 !important; -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
      .deck-header { display: none !important; }
      .slide {
        max-width: 1280px !important;
        width: 1280px !important;
        height: 720px !important;
        margin: 0 !important;
        border-radius: 0 !important;
        border: none !important;
        padding: 48px 56px !important;
        page-break-after: always !important;
        break-after: page !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
      }
    `,
  });
  await page.waitForTimeout(300);

  const outPdf = path.join(ROOT, "docs/Switchyard_Pitch_Deck.pdf");
  await page.pdf({
    path: outPdf,
    width: "1280px",
    height: "720px",
    printBackground: true,
    margin: { top: "0px", right: "0px", bottom: "0px", left: "0px" },
  });

  await browser.close();
  console.log("Exported", outPdf);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
