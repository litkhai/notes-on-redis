"""Agent Mesh A2A hand-off on local Redis 8.10.3: kill the process running a task after three of six
steps, then (1) with takeover=True resume it on another replica, (2) without takeover, watch a reader mark
it failed. Uses mesh_takeover_app.py. usage: .venv/bin/python mesh_takeover.py
"""
import json
import os
import subprocess
import sys
import time
import uuid

import httpx

HERE = os.path.dirname(os.path.abspath(__file__))
C, RPORT = "nor-iris-mesh2", 16392
URL = f"redis://127.0.0.1:{RPORT}/0"
H = {"A2A-Version": "1.0", "Content-Type": "application/json"}
procs = []


def sh(*a):
    return subprocess.run(a, capture_output=True, text=True)


def replica(port, *flags):
    p = subprocess.Popen([sys.executable, os.path.join(HERE, "mesh_takeover_app.py"), str(port), *flags],
                         env={**os.environ, "REDIS_URL": URL})
    procs.append(p)
    for _ in range(100):
        try:
            httpx.get(f"http://127.0.0.1:{port}/", timeout=0.5); return p
        except httpx.HTTPError:
            time.sleep(0.1)


def frames(port, tid, cursor=None, stop=None, timeout=60):
    """Read Task frames; return (status, [(version, kind, artifacts, state)])."""
    out = []
    hdr = {"A2A-Version": "1.0", "Accept": "text/event-stream", **({"Last-Event-ID": cursor} if cursor else {})}
    with httpx.stream("GET", f"http://127.0.0.1:{port}/tasks/{tid}:subscribe", headers=hdr, timeout=timeout) as resp:
        if resp.status_code != 200:
            return resp.status_code, resp.read().decode()[:150], out
        fid, data = None, []
        for line in resp.iter_lines():
            if line.startswith("id:"):
                fid = line[3:].strip()
            elif line.startswith("data:"):
                data.append(line[5:].strip())
            elif line == "" and data:
                f = json.loads("".join(data)); data = []
                task = f.get("task") or {}
                arts = [(a["artifactId"], a["parts"][0]["text"].split()[-1]) for a in task.get("artifacts") or []]
                if "artifactUpdate" in f:
                    a = f["artifactUpdate"]["artifact"]; arts.append((a["artifactId"], a["parts"][0]["text"].split()[-1]))
                st = (f.get("statusUpdate") or task).get("status", {}).get("state")
                msg = ((f.get("statusUpdate") or task).get("status", {}).get("message") or {}).get("parts", [{}])[0].get("text")
                out.append((fid, next(iter(f)), arts, st, msg))
                if (stop and stop(out)) or st in ("TASK_STATE_COMPLETED", "TASK_STATE_FAILED", "TASK_STATE_CANCELED"):
                    break
    return 200, "", out


def show(rows, who):
    for fid, kind, arts, st, msg in rows:
        print(f"   {who} v{fid} {kind} {[f'{a} by {p}' for a, p in arts]} {st or ''} {msg or ''}".rstrip())


def start_task(port):
    r = httpx.post(f"http://127.0.0.1:{port}/message:send", headers=H, json={
        "message": {"messageId": str(uuid.uuid4()), "role": "ROLE_USER", "parts": [{"text": "plan"}]},
        "configuration": {"returnImmediately": True}}).json()
    return r["task"]["id"]


sh("docker", "rm", "-f", C)
sh("docker", "run", "-d", "--name", C, "-p", f"127.0.0.1:{RPORT}:6379", "redis:8.10.3")
time.sleep(2)
three = lambda rows: sum(len(r[2]) for r in rows) >= 3
try:
    print("== 1. takeover=True: A runs the task, dies after three steps, B takes it over")
    A, B = 28301, 28302
    pa = replica(A); replica(B)
    tid = start_task(A); print("   task", tid[:8] + "…", "started on A")
    st, _, rows = frames(A, tid, stop=three); show(rows, "A"); cur = rows[-1][0]
    pa.kill(); t_kill = time.time(); print("   A killed (SIGKILL); saved cursor v" + cur)
    tries = []
    while time.time() - t_kill < 60:
        r = httpx.post(f"http://127.0.0.1:{B}/resume/{tid}", timeout=30)
        tries.append((round(time.time() - t_kill, 1), r.status_code, r.json()))
        if r.status_code == 200 and r.json().get("accepted"):
            break
        time.sleep(2)
    for t, code, body in tries[:2] + (tries[-1:] if len(tries) > 2 else []):
        print(f"   {t:5.1f} s  POST B /resume -> HTTP {code} {json.dumps(body)[:170]}")
    print(f"   resume attempts: {len(tries)}; accepted {tries[-1][0]} s after the kill" if tries[-1][2].get("accepted") else "   never accepted")
    st, _, rows = frames(B, tid, cursor=cur); show(rows, "B")
    final = rows[-1]
    print("   artifacts in the finished task:", [f"{a} by {p}" for a, p in final[2]] if final[1] == "task" else "see frames above")

    print("\n== 2. takeover=False: the same failure, a reader on B is following the task")
    for p in procs:
        p.terminate()
    for p in procs:
        p.wait()
    procs.clear()
    A, B = 28311, 28312
    pa = replica(A, "--no-takeover"); replica(B, "--no-takeover")
    tid = start_task(A); print("   task", tid[:8] + "…", "started on A")
    st, _, rows = frames(A, tid, stop=three); show(rows, "A"); cur = rows[-1][0]
    pa.kill(); t_kill = time.time(); print("   A killed (SIGKILL)")
    st, err, rows = frames(B, tid, cursor=cur, timeout=90); show(rows, "B")
    print(f"   reader on B saw the end {time.time() - t_kill:.1f} s after the kill" if rows else f"   HTTP {st} {err}")
    r = httpx.post(f"http://127.0.0.1:{B}/resume/{tid}", timeout=30)
    print(f"   POST B /resume on the failed task -> HTTP {r.status_code} {json.dumps(r.json())[:170]}")
finally:
    for p in procs:
        p.terminate()
    sh("docker", "rm", "-f", C)
