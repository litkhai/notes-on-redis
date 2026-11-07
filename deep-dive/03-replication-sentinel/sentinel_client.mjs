// The same failover as sentinel_client.py, with node-redis 6.3.1's createSentinel(): write every 20 ms,
// kill the master, time the first write on the new one. Uses setup/node_modules (cd ../../setup && npm ci).
// usage: node sentinel_client.mjs   (on a fresh 'docker compose up')
import { createRequire } from "node:module";
import { execFileSync } from "node:child_process";
const require = createRequire(new URL("../../setup/package.json", import.meta.url));
const { createSentinel, createClient } = require("redis");
const NAMES = { "10.231.77.10": "nor-repl-primary", "10.231.77.11": "nor-repl-replica1", "10.231.77.12": "nor-repl-replica2" };
const roots = [21, 22, 23].map(n => ({ host: `10.231.77.${n}`, port: 26379 }));
// Sentinel 8.10 has no QUIT, so the helper connection is closed with destroy().
const ask = async () => { const s = createClient({ socket: { host: roots[0].host, port: 26379 } }); await s.connect();
  const r = await s.sendCommand(["SENTINEL", "get-master-addr-by-name", "mymaster"]); s.destroy(); return r[0]; };
const sentinel = createSentinel({ name: "mymaster", sentinelRootNodes: roots });
const errors = {}; sentinel.on("error", e => { errors[e.constructor.name] = (errors[e.constructor.name] || 0) + 1; });
await sentinel.connect();
const before = await ask();
console.log(`node-redis ${require("redis/package.json").version}; master from the Sentinels: ${before} = ${NAMES[before]}`);
await sentinel.set("c", "0");
const log = []; let stop = false;
const writer = (async () => { while (!stop) { const t = Date.now();
  try { const v = Number(await sentinel.incr("c")); log.push([t, true, v, Date.now() - t]); } catch (e) { log.push([t, false, e.constructor.name, Date.now() - t]); }
  await new Promise(r => setTimeout(r, 20)); } })();
await new Promise(r => setTimeout(r, 3000));
const tKill = Date.now(); execFileSync("docker", ["kill", NAMES[before]]); console.log(`killed ${NAMES[before]} (SIGKILL)`);
let now = before;
while (Date.now() - tKill < 60000) { try { now = await ask(); } catch {} if (now !== before) break; await new Promise(r => setTimeout(r, 200)); }
console.log(`Sentinels report the new master ${now} = ${NAMES[now]} after ${((Date.now() - tKill) / 1000).toFixed(1)} s`);
await new Promise(r => setTimeout(r, 3000)); stop = true; await writer;
const bad = log.filter(r => !r[1]), ok = log.filter(r => r[1]);
let gap = 0, start = null; for (const [t, good] of log) { if (!good && start === null) start = t; if (good && start !== null) { gap = Math.max(gap, t - start); start = null; } }
const firstAfter = ok.find(r => r[0] > tKill + 100);
console.log(`writes ${log.length}, failed ${bad.length}, errors thrown ${JSON.stringify([...new Set(bad.map(r => r[2]))])}, error events ${JSON.stringify(errors)}`);
console.log(`longest stretch without a successful write ${(gap / 1000).toFixed(1)} s; first write after the kill succeeded at ${firstAfter ? ((firstAfter[0] - tKill) / 1000).toFixed(1) + " s" : "never"}`);
const slow = log.reduce((a, r) => (r[3] > a[3] ? r : a));
console.log(`slowest write: issued ${((slow[0] - tKill) / 1000).toFixed(1)} s after the kill, took ${(slow[3] / 1000).toFixed(1)} s (node-redis queued it until the new master answered)`);
console.log(`last value ${ok.at(-1)[2]}, successful writes ${ok.length}, increments lost ${ok.length - ok.at(-1)[2]}`);
execFileSync("docker", ["start", NAMES[before]]);
await sentinel.close();
