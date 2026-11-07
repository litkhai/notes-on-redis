// Same smoke test with node-redis. Never prints the URL.
// usage: node smoke.mjs
import { createClient } from "redis";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { createRequire } from "node:module";

const here = dirname(fileURLToPath(import.meta.url));
const env = Object.fromEntries(readFileSync(join(here, ".env"), "utf8").split("\n").filter(l => l.includes("=")).map(l => [l.slice(0, l.indexOf("=")), l.slice(l.indexOf("=") + 1).trim()]));
const version = createRequire(import.meta.url)("redis/package.json").version;
console.log("node-redis", version);
for (const [name, url] of Object.entries({ local: "redis://127.0.0.1:16379", "cloud-free": env.REDIS_URL })) {
  const c = createClient({ url });
  c.on("error", e => console.error(name, e.message));
  await c.connect();
  await c.set("smoke:node", "ok", { EX: 60 });
  const info = await c.info("server");
  console.log(`${name}: PING=${await c.ping()} GET=${await c.get("smoke:node")} version=${info.match(/redis_version:(\S+)/)[1]}`);
  await c.quit();
}
