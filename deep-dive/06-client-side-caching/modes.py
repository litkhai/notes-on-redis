"""Client-side caching tracking options on Redis 8.10.3, on raw connections so every push is visible:
OPTIN, OPTOUT, NOLOOP, and the RESP2 redirect mode (invalidations delivered over Pub/Sub).
usage: python3 modes.py   (standard library only; starts and removes container nor-dd-csc2)
"""
import socket
import subprocess
import time

C, PORT = "nor-dd-csc2", 16392
subprocess.run(["docker", "rm", "-f", C], capture_output=True)
subprocess.run(["docker", "run", "-d", "--name", C, "-p", f"127.0.0.1:{PORT}:6379", "redis:8.10.3"], check=True, capture_output=True)
time.sleep(2)


class Conn:
    def __init__(self, resp3=True):
        self.s = socket.create_connection(("127.0.0.1", PORT)); self.s.settimeout(0.5)
        if resp3:
            self.cmd("HELLO 3")

    def cmd(self, line):
        self.s.sendall(line.encode() + b"\r\n"); time.sleep(0.05); return self.read()

    def read(self):
        out = b""
        try:
            while True:
                chunk = self.s.recv(65536)
                if not chunk:
                    break
                out += chunk
                if len(chunk) < 65536:
                    time.sleep(0.05)
        except socket.timeout:
            pass
        return out.decode(errors="replace").replace("\r\n", " ").strip()


def invalidated(text):
    """Keys named in invalidation messages (RESP3 push or RESP2 Pub/Sub message)."""
    toks = text.split()
    return sorted({t for t in toks if t.startswith("k:")})


w = Conn()   # a separate writer


def run(title, setup, reads, writes, own_writes=()):
    t = Conn()
    for line in setup:
        t.cmd(line)
    for line in reads:
        t.cmd(line)
    got = ""
    for line in own_writes:          # a push for its own write arrives with the SET reply
        got += " " + t.cmd(line)
    for k in writes:
        w.cmd(f"SET {k} new")
    got += " " + t.read()
    print(f"{title:46} invalidations received for: {invalidated(got) or 'none'}")


print("== OPTIN: only reads after CLIENT CACHING YES are tracked")
run("OPTIN, GET k:a, then CACHING YES + GET k:b", ["CLIENT TRACKING ON OPTIN"],
    ["GET k:a", "CLIENT CACHING YES", "GET k:b"], ["k:a", "k:b"])
print("== OPTOUT: every read is tracked except after CLIENT CACHING NO")
run("OPTOUT, GET k:c, then CACHING NO + GET k:d", ["CLIENT TRACKING ON OPTOUT"],
    ["GET k:c", "CLIENT CACHING NO", "GET k:d"], ["k:c", "k:d"])
print("== NOLOOP: the tracking connection writes the key it read")
run("default, GET k:e, then its own SET k:e", ["CLIENT TRACKING ON"], ["GET k:e"], [], ["SET k:e mine"])
run("NOLOOP, GET k:f, then its own SET k:f", ["CLIENT TRACKING ON NOLOOP"], ["GET k:f"], [], ["SET k:f mine"])
print("== RESP2 redirect: invalidations go to another connection subscribed to __redis__:invalidate")
sub = Conn(resp3=False)
sub_id = sub.cmd("CLIENT ID").lstrip(":")
print("   subscriber:", sub.cmd("SUBSCRIBE __redis__:invalidate"))
data = Conn(resp3=False)
print("   data connection:", data.cmd(f"CLIENT TRACKING ON REDIRECT {sub_id}"), "| GET k:g ->", data.cmd("GET k:g"))
w.cmd("SET k:g new")
got = sub.read()
print("   after another client's SET k:g, the subscriber got:", got)
print("   the data connection itself got:", data.read() or "nothing")
subprocess.run(["docker", "rm", "-f", C], capture_output=True)
