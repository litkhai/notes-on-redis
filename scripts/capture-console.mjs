// Screen captures of web consoles (Redis Cloud, AWS) for the walkthrough pages.
//
// Attaches to a Chrome that is already logged in (started with --remote-debugging-port, reached
// here on 127.0.0.1:9222), opens its own window-named tab, and for each manifest entry:
// navigates, optionally clicks a tab, masks identifying text in the DOM, refuses to save if any
// leak term is still visible, and writes a 2x WebP (quality 82) next to the site pages.
// The console's own theme setting is not touched: dark mode and English are emulated in this tab.
//
// usage: node scripts/capture-console.mjs <manifest.json> [name,name,...]
//   needs: npm i playwright@1.48 ; python3 with Pillow (WebP)
//   mask terms: <manifest dir>/.env (gitignored), lines
//     MASK_TERMS=<regex>|<regex>|...     extra patterns to grey out (your name, account number, IDs)
//     LEAK_TERMS=<text>,<text>,...       plain strings that must not survive masking
// manifest: { "out": "docs/assets/img/<slug>", "base": "https://cloud.redis.io/#/",
//             "shots": [ { "name": "12-databases-list", "path": "databases",
//                          "tab": "Team", "click": [x, y], "tall": true, "waitMs": 6000 } ] }
import { resolve, dirname, join } from "node:path";
import { readFileSync, existsSync, mkdirSync } from "node:fs";
import { tmpdir } from "node:os";
import { execFileSync } from "node:child_process";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");

const file = process.argv[2];
if (!file) { console.error("usage: node scripts/capture-console.mjs <manifest.json> [names]"); process.exit(2); }
const only = process.argv[3] ? process.argv[3].split(",") : null;
const manifest = JSON.parse(readFileSync(resolve(file), "utf8"));
const root = resolve(dirname(new URL(import.meta.url).pathname), "..");
const out = join(root, manifest.out);
const raw = join(tmpdir(), "capture-console-raw");
mkdirSync(raw, { recursive: true });

const env = {};
const envFile = join(dirname(resolve(file)), ".env");
if (existsSync(envFile)) for (const l of readFileSync(envFile, "utf8").split("\n")) { const i = l.indexOf("="); if (i > 0) env[l.slice(0, i)] = l.slice(i + 1).trim(); }
const PATTERNS = [
  "[\\w.+-]+@[\\w-]+\\.[\\w.]+",                                   // e-mail first, so it wins over name parts
  "[\\w.-]+\\.db\\.redis\\.io(:\\d+)?",                              // Redis Cloud endpoints
  "redis-\\d+\\.[\\w.-]+\\.(redislabs|redis-cloud)\\.com(:\\d+)?",
  "[\\w.-]+\\.cache\\.amazonaws\\.com(:\\d+)?",                      // ElastiCache endpoints
  "\\b\\d{1,3}(\\.\\d{1,3}){3}\\b",                                  // IPv4
  "\\b\\d{4}-?\\d{4}-?\\d{4}\\b",                                    // AWS account IDs
  "\\b(vpc|subnet|sg|eni|igw|rtb|acl|i)-[0-9a-f]{8,17}\\b", "arn:aws[\\w:/.*-]+",
  "\\b[A-Za-z0-9]{40,}\\b",                                          // API keys and secrets
  ...(env.MASK_TERMS ? env.MASK_TERMS.split("|") : []),
];
const LEAKS = env.LEAK_TERMS ? env.LEAK_TERMS.split(",") : [];

async function mask(page) {
  await page.evaluate(({ pats }) => {
    if (location.host.endsWith("aws.amazon.com")) document.body.classList.add("awsui-dark-mode", "awsui-polaris-dark-mode");
    const re = new RegExp(pats.join("|"), "g");
    if (!document.getElementById("cm-style")) {
      const st = document.createElement("style"); st.id = "cm-style";
      st.textContent = ".cm{background:#4a5560!important;color:transparent!important;border-radius:3px;text-shadow:none!important}input.cm,textarea.cm{-webkit-text-fill-color:transparent}";
      document.head.appendChild(st);
    }
    const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT); const nodes = [];
    while (w.nextNode()) nodes.push(w.currentNode);
    for (const n of nodes) {
      if (n.parentElement?.closest(".cm,script,style")) continue;
      const t = n.nodeValue; re.lastIndex = 0; if (!re.test(t)) continue;
      re.lastIndex = 0; const frag = document.createDocumentFragment(); let i = 0, m;
      while ((m = re.exec(t))) { if (!m[0]) { re.lastIndex++; continue; }
        frag.append(t.slice(i, m.index)); const s = document.createElement("span"); s.className = "cm"; s.textContent = m[0]; frag.append(s); i = m.index + m[0].length; }
      frag.append(t.slice(i)); n.replaceWith(frag);
    }
    for (const el of document.querySelectorAll("input,textarea")) { re.lastIndex = 0; if (re.test(el.value)) el.classList.add("cm"); }
    for (const el of document.querySelectorAll("body *")) {                // avatar initials, top right
      const r = el.getBoundingClientRect(); if (r.y > 70 || r.x < 1000) continue;
      if (el.children.length === 0 && /^[A-Z]{2}$/.test(el.textContent.trim())) el.classList.add("cm");
    }
  }, { pats: PATTERNS });
  return page.evaluate(({ leaks }) => {
    const parts = []; const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    while (w.nextNode()) { const n = w.currentNode; if (!n.parentElement.closest(".cm,script,style")) parts.push(n.nodeValue); }
    const t = parts.join("\n") + "\n" + [...document.querySelectorAll("input:not(.cm),textarea:not(.cm)")].map(e => e.value).join("\n");
    return leaks.filter(l => l && t.includes(l)).concat(/[A-Za-z0-9]{40,}/.test(t) ? ["long token"] : []);
  }, { leaks: LEAKS });
}

async function contentHeight(page) {
  return page.evaluate(() => {
    let best = document.documentElement.scrollHeight;
    for (const el of document.querySelectorAll("*")) {
      const cs = getComputedStyle(el);
      if (/(auto|scroll)/.test(cs.overflowY) && el.scrollHeight > el.clientHeight + 5 && el.clientWidth > 600)
        best = Math.max(best, el.scrollHeight + el.getBoundingClientRect().top + 40);
    }
    return Math.ceil(best);
  });
}

const browser = await chromium.connectOverCDP(process.env.CDP_URL ?? "http://127.0.0.1:9222");
try {
  const ctx = browser.contexts()[0];
  let page = null;
  for (const p of ctx.pages()) { try { if ((await p.evaluate(() => window.name)) === "capture-tab") page = p; } catch {} }
  if (!page) { page = await ctx.newPage(); await page.goto("about:blank"); await page.evaluate(() => { window.name = "capture-tab"; }); }
  const cdp = await ctx.newCDPSession(page);
  await cdp.send("Emulation.setEmulatedMedia", { features: [{ name: "prefers-color-scheme", value: manifest.theme ?? "dark" }] });
  await cdp.send("Network.enable");
  await cdp.send("Network.setUserAgentOverride", { userAgent: await page.evaluate(() => navigator.userAgent), acceptLanguage: "en-US,en;q=0.9" });
  const [vw, vh] = manifest.viewport ?? [1440, 765];
  const metrics = (h) => cdp.send("Emulation.setDeviceMetricsOverride", { width: vw, height: h, deviceScaleFactor: 2, mobile: false });

  for (const s of manifest.shots) {
    if (only && !only.includes(s.name)) continue;
    await metrics(vh);
    await page.goto("about:blank");
    await page.goto(manifest.base + s.path, { waitUntil: "domcontentloaded" });
    await page.waitForTimeout(s.waitMs ?? 6000);
    if (s.tab) {
      const l = page.getByRole("tab", { name: s.tab }).or(page.getByText(s.tab, { exact: true })).first();
      await l.waitFor({ timeout: 60000 }); await l.click(); await page.waitForTimeout(4500);
    }
    if (s.button) { await page.getByRole("button", { name: s.button, exact: true }).last().click(); await page.waitForTimeout(2500); }
    if (s.click) { await page.mouse.click(...s.click); await page.waitForTimeout(1500); }
    if (s.tall) { await metrics(Math.max(vh, Math.min(await contentHeight(page), 8000))); await page.waitForTimeout(2000); }
    const leaks = await mask(page);
    if (leaks.length) throw new Error(`${s.name}: still visible after masking: ${leaks.join(", ")}`);
    await page.waitForTimeout(300);
    const png = join(raw, s.name + ".png");
    await page.screenshot({ path: png });
    execFileSync("python3", ["-c", "import sys;from PIL import Image;im=Image.open(sys.argv[1]);im.save(sys.argv[2],'WEBP',quality=82,method=6);print(sys.argv[3],im.size)",
      png, join(out, s.name + ".webp"), s.name], { stdio: "inherit" });
    await page.keyboard.press("Escape");
  }
  await cdp.send("Emulation.clearDeviceMetricsOverride");
} finally {
  await browser.close(); // detaches; the user's Chrome keeps running
}
