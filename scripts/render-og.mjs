// Render docs/assets/og/og.html to og.png (1200x630) for link previews.
// usage: node scripts/render-og.mjs      (needs playwright; fetches the two Google Fonts)
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
const { chromium } = createRequire(import.meta.url)("playwright");
const dir = join(dirname(fileURLToPath(import.meta.url)), "..", "docs", "assets", "og");
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 1200, height: 630 }, deviceScaleFactor: 1 });
await p.goto("file://" + join(dir, "og.html"), { waitUntil: "networkidle" });
await p.evaluate(() => document.fonts.ready);
await p.screenshot({ path: join(dir, "og.png") });
await b.close();
console.log("wrote", join(dir, "og.png"));
