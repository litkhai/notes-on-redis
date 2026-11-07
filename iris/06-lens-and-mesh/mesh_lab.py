"""Agent Mesh (beta) on local Redis 8.10.3: disconnect from one replica, resume on another.
Part 1 FastAPI SSE, part 2 the producer's replica dies, part 3 A2A task updates.
usage: .venv/bin/python mesh_lab.py   (starts and removes container nor-iris-mesh and four app processes)
"""
import json
import os
import subprocess
import sys
import time
import uuid

import httpx
import redis

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
C, RPORT = "nor-iris-mesh", 16392
URL = f"redis://127.0.0.1:{RPORT}/0"
procs = []


def sh(*a):
    return subprocess.run(a, capture_output=True, text=True)


def replica(app, port, **env):
    p = subprocess.Popen([PY, os.path.join(HERE, app), str(port)], env={**os.environ, "REDIS_URL": URL, **env})
    procs.append(p)
    for _ in range(100):
        try:
            httpx.get(f"http://127.0.0.1:{port}/", timeout=0.5); return p
        except httpx.HTTPError:
            time.sleep(0.1)
    raise RuntimeError(f"{app} on {port} did not start")


def sse(resp):
    """Yield (id, event, data) frames from a streaming httpx response."""
    fid = ev = None; data = []
    for line in resp.iter_lines():
        if line == "":
            if data or ev:
                yield fid, ev, "\n".join(data)
            fid = ev = None; data = []
        elif line.startswith(":"):
            continue
        else:
            k, _, v = line.partition(":"); v = v[1:] if v.startswith(" ") else v
            if k == "id": fid = v
            elif k == "event": ev = v
            elif k == "data": data.append(v)


sh("docker", "rm", "-f", C)
sh("docker", "run", "-d", "--name", C, "-p", f"127.0.0.1:{RPORT}:6379", "redis:8.10.3", "redis-server", "--save", "", "--appendonly", "no")
r = redis.Redis(port=RPORT, decode_responses=True)
for _ in range(50):
    try:
        r.ping(); break
    except redis.ConnectionError:
        time.sleep(0.2)
print("redis", r.info("server")["redis_version"])
try:
    print("\n== 1. FastAPI SSE: start on replica A (18101), read 5 events, disconnect")
    A, B = 18101, 18102
    replica("mesh_sse_app.py", A); replica("mesh_sse_app.py", B)
    job = httpx.post(f"http://127.0.0.1:{A}/jobs").json(); jid = job["job_id"]
    print("   POST /jobs on A ->", {**job, "job_id": jid[:8] + "…"})
    seen = []
    with httpx.stream("GET", f"http://127.0.0.1:{A}/jobs/{jid}/events", timeout=30) as resp:
        for fid, ev, data in sse(resp):
            if ev == "progress":
                seen.append(json.loads(data)["step"]); cursor = fid
                print(f"   A  id={fid} {ev} {data}")
                if len(seen) == 5:
                    break
    t_off = time.time(); time.sleep(3)
    print(f"   disconnected for {time.time() - t_off:.1f} s; saved cursor {cursor}")
    print("\n== reconnect to replica B (18102) with Last-Event-ID")
    replay = []
    with httpx.stream("GET", f"http://127.0.0.1:{B}/jobs/{jid}/events", headers={"Last-Event-ID": cursor}, timeout=30) as resp:
        print("   status", resp.status_code)
        t0 = time.time(); first_live = None
        for fid, ev, data in sse(resp):
            d = json.loads(data) if data.startswith("{") else data
            if ev == "progress":
                replay.append(d["step"])
                if first_live is None and time.time() - t0 > 0.2:
                    first_live = d["step"]
            last = fid
            if ev in ("completed", "stream.end"):
                print(f"   B  id={fid} {ev} {data}"); break
    print(f"   steps before disconnect {seen}")
    print(f"   steps after reconnect   {replay}")
    print(f"   arrived at once (replayed): {replay[:replay.index(first_live)] if first_live else replay}; then live from step {first_live}")
    print(f"   all 20 exactly once: {sorted(seen + replay) == list(range(1, 21))}")
    for label, hdr in (("final cursor", {"Last-Event-ID": last}), ("malformed cursor", {"Last-Event-ID": "not-a-cursor"}),
                       ("unknown run", None)):
        url = f"http://127.0.0.1:{B}/jobs/{jid if hdr else uuid.uuid4()}/events"
        with httpx.stream("GET", url, headers=hdr or {}, timeout=10) as resp:
            body = resp.read().decode()[:90] if resp.status_code != 200 else ""
            print(f"   reconnect with {label:16} -> HTTP {resp.status_code} {body}")
    print("\n== what is in Redis")
    for k in sorted(r.scan_iter("lab:sse*")):
        t = r.type(k); extra = ""
        if t == "stream":
            info = r.xinfo_stream(k)
            extra = f"XLEN {r.xlen(k)}, idmp keys {[x for x in info if 'idmp' in x.lower()]}"
        print(f"   {k.replace(jid, '<job>')} {t} ttl={r.ttl(k)} {extra}")

    def lose_producer(label, env, watch):
        """Start a run on A, read it from B, kill A after 3 events, reconnect like a browser would."""
        for p in procs: p.terminate()
        for p in procs: p.wait()
        procs.clear()
        print(f"\n== 2{label}")
        pa = replica("mesh_sse_app.py", A, **env); replica("mesh_sse_app.py", B, **env)
        jid = httpx.post(f"http://127.0.0.1:{A}/jobs").json()["job_id"]
        n, cur, t_kill = 0, None, None
        while True:
            hdr = {"Last-Event-ID": cur} if cur else {}
            with httpx.stream("GET", f"http://127.0.0.1:{B}/jobs/{jid}/events", headers=hdr, timeout=120) as resp:
                if t_kill:
                    print(f"   {time.time() - t_kill:5.1f} s  reconnect -> HTTP {resp.status_code}")
                if resp.status_code != 200:
                    return
                for fid, ev, data in sse(resp):
                    cur = fid or cur
                    if ev == "progress":
                        n += 1
                        if n == 3:
                            pa.kill(); t_kill = time.time(); print("    0.0 s  B has read 3 events; replica A killed (SIGKILL)")
                    elif ev:
                        print(f"   {time.time() - t_kill:5.1f} s  {ev} {data}")
                if t_kill:
                    print(f"   {time.time() - t_kill:5.1f} s  connection closed by B")
            if t_kill and time.time() - t_kill > watch:
                print(f"   past {watch} s with no final event; stopped watching")
                return

    A, B = 18101, 18102
    lose_producer(". the producer's replica dies; SDK defaults (heartbeat 15 s, silence 60 s, socket timeout unset)", {}, 75)
    print("   redis-py", redis.__version__, "default socket_timeout:",
          __import__("inspect").signature(__import__("redis.asyncio").asyncio.Redis.__init__).parameters["socket_timeout"].default)
    lose_producer("b. the same with REDIS_SOCKET_TIMEOUT=30 (and heartbeat 5 s, silence 12 s to keep it short)",
                  {"REDIS_SOCKET_TIMEOUT": "30", "REDIS_STREAM_HEARTBEAT_INTERVAL": "5", "REDIS_STREAM_SILENCE_TIMEOUT": "12"}, 60)

    print("\n== 3. A2A: task started on replica A (18201), resumed on replica B (18202)")
    for p in procs: p.terminate()
    for p in procs: p.wait()
    procs.clear()
    A, B = 18201, 18202
    replica("mesh_a2a_app.py", A); replica("mesh_a2a_app.py", B)
    H = {"A2A-Version": "1.0", "Content-Type": "application/json"}
    res = httpx.post(f"http://127.0.0.1:{A}/message:send", headers=H, json={
        "message": {"messageId": str(uuid.uuid4()), "role": "ROLE_USER", "parts": [{"text": "count"}]},
        "configuration": {"returnImmediately": True}}).json()
    tid = res["task"]["id"]; print("   POST /message:send on A -> task", tid[:8] + "…", res["task"]["status"]["state"])

    def frames(port, cursor=None, stop_after=None):
        out = []
        hdr = {"A2A-Version": "1.0", "Accept": "text/event-stream", **({"Last-Event-ID": cursor} if cursor else {})}
        with httpx.stream("GET", f"http://127.0.0.1:{port}/tasks/{tid}:subscribe", headers=hdr, timeout=30) as resp:
            if resp.status_code != 200:
                return resp.status_code, out, cursor
            for fid, ev, data in sse(resp):
                f = json.loads(data)
                arts = [a["artifactId"] for a in (f.get("task", {}).get("artifacts") or [])]
                if "artifactUpdate" in f: arts.append(f["artifactUpdate"]["artifact"]["artifactId"])
                state = (f.get("statusUpdate") or f.get("task") or {}).get("status", {}).get("state")
                kind = next(iter(f))
                out.append((fid, kind, arts, state)); cursor = fid or cursor
                if stop_after and len(out) >= stop_after:
                    break
                if state == "TASK_STATE_COMPLETED":
                    break
        return 200, out, cursor

    st, got, cur = frames(A, stop_after=4)
    for f in got: print(f"   A  id={f[0]} {f[1]} {f[2]} {f[3] or ''}")
    time.sleep(2); print(f"   disconnected 2 s; saved cursor (Task version) {cur}")
    st, got2, cur2 = frames(B, cursor=cur)
    for f in got2: print(f"   B  id={f[0]} {f[1]} {f[2]} {f[3] or ''}")
    ids = [a for f in got + got2 for a in f[2]]
    print(f"   artifacts received {len(ids)}, distinct {len(set(ids))}: all 10 exactly once = {sorted(set(ids)) == sorted(f'update-{i}' for i in range(1, 11)) and len(ids) == 10}")
    st, _, _ = frames(B, cursor=cur2); print(f"   reconnect at the final version -> HTTP {st}")
    print("\n== what is in Redis")
    for k in sorted(k for k in r.scan_iter("*") if "sse" not in k):
        print(f"   {k.replace(tid, '<task>')} {r.type(k)} ttl={r.ttl(k)}")
finally:
    for p in procs:
        p.terminate()
    sh("docker", "rm", "-f", C)
