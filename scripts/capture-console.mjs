// Screen captures of web console pages for the site's walkthrough articles (Redis Cloud
// console, Redis Insight). Adapted from notes-on-clickhouse scripts/capture-play.mjs; the
// /play-specific query logic is replaced by a generic "open URL, wait for selector, clip or
// full page" flow. Masking is NOT done here — mask in an image editor before committing.
//
// manifest: a JSON array of
//   { url, png, webp, waitFor?: "css selector", clip?: {x,y,width,height},
//     viewport?: [1440, 900], scale?: 2, theme?: "light", storageState?: "path.json" }
// usage: node scripts/capture-console.mjs <manifest.json>
//   needs: npm i playwright && npx playwright install chromium ; cwebp on PATH
//   storageState: a Playwright storage state saved after logging in by hand
//   (npx playwright codegen --save-storage=state.json https://cloud.redis.io) — gitignored.
// Not run yet (STATUS.md).
import { resolve, dirname } from "node:path";
import { readFileSync, mkdirSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");

const file = process.argv[2];
if (!file) { console.error("usage: node scripts/capture-console.mjs <manifest.json>"); process.exit(2); }
const manifest = JSON.parse(readFileSync(resolve(file), "utf8"));

const browser = await chromium.launch();
try {
  for (const e of manifest) {
    const [w, h] = e.viewport ?? [1440, 900];
    const theme = e.theme ?? "light";
    const ctx = await browser.newContext({
      viewport: { width: w, height: h },
      deviceScaleFactor: e.scale ?? 2,
      colorScheme: theme,
      storageState: e.storageState,
    });
    const page = await ctx.newPage();
    await page.goto(e.url, { waitUntil: "networkidle" });
    if (e.waitFor) await page.waitForSelector(e.waitFor, { timeout: 60000 });
    await page.waitForTimeout(e.settleMs ?? 1500);
    mkdirSync(dirname(e.png), { recursive: true });
    mkdirSync(dirname(e.webp), { recursive: true });
    await page.screenshot({ path: e.png, clip: e.clip, fullPage: !e.clip });
    execFileSync("cwebp", ["-quiet", "-q", "82", e.png, "-o", e.webp]);
    const dim = readWebpSize(e.webp);
    console.log(`${e.webp} ${dim[0]} ${dim[1]}`);
    await ctx.close();
  }
} finally { await browser.close(); }

// width/height from the WebP header (VP8 lossy, VP8L, VP8X)
function readWebpSize(f) {
  const b = readFileSync(f);
  const fmt = b.toString("ascii", 12, 16);
  if (fmt === "VP8 ") return [b.readUInt16LE(26) & 0x3fff, b.readUInt16LE(28) & 0x3fff];
  if (fmt === "VP8L") { const v = b.readUInt32LE(21); return [(v & 0x3fff) + 1, ((v >> 14) & 0x3fff) + 1]; }
  if (fmt === "VP8X") return [b.readUIntLE(24, 3) + 1, b.readUIntLE(27, 3) + 1];
  throw new Error("unknown WebP chunk " + fmt);
}
