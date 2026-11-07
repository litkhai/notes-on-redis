"""Inline SVG diagrams for /architecture/. Colours come from the site's CSS variables through
classes (.arch .box, .arch .rd, .arch .ln ...), so the same SVG works in dark and light themes.
Arrowheads are drawn as polygons, not markers: every diagram appears once per language block
and duplicate marker ids inside hidden blocks do not render reliably.
"""
import math


def _box(x, y, w, h, label, sub="", cls="box"):
    t = f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="7"/>'
    cy = y + h / 2 + (4 if not sub else -3)
    t += f'<text x="{x + w / 2}" y="{cy}" text-anchor="middle">{label}</text>'
    if sub:
        t += f'<text class="sm" x="{x + w / 2}" y="{cy + 16}" text-anchor="middle">{sub}</text>'
    return t


def _arrow(x1, y1, x2, y2, label="", dashed=False, both=False):
    cls = "ln dash" if dashed else "ln"
    t = f'<line class="{cls}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>'
    def head(xa, ya, xb, yb):
        a = math.atan2(yb - ya, xb - xa); s = 7
        p1 = (xb - s * math.cos(a - 0.45), yb - s * math.sin(a - 0.45))
        p2 = (xb - s * math.cos(a + 0.45), yb - s * math.sin(a + 0.45))
        return f'<polygon class="hd" points="{xb:.1f},{yb:.1f} {p1[0]:.1f},{p1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"/>'
    t += head(x1, y1, x2, y2)
    if both:
        t += head(x2, y2, x1, y1)
    if label:
        t += f'<text class="sm" x="{(x1 + x2) / 2}" y="{(y1 + y2) / 2 - 6}" text-anchor="middle">{label}</text>'
    return t


def svg(w, h, body, title):
    return (f'<div class="arch" markdown="0"><svg viewBox="0 0 {w} {h}" role="img" aria-label="{title}">'
            f'<title>{title}</title>{body}</svg></div>')


def cache_aside():
    b = _box(20, 95, 130, 60, "Application")
    b += _box(300, 20, 170, 60, "Redis", "cache, TTL + eviction", "rd")
    b += _box(300, 170, 170, 60, "Primary database", "source of truth")
    b += _arrow(150, 105, 298, 38, "1 GET")
    b += _arrow(150, 145, 298, 205, "2 on miss: read")
    b += _arrow(150, 125, 298, 66, "", dashed=True)
    b += '<text class="sm" x="246" y="112" text-anchor="middle">3 SET with TTL</text>'
    b += _box(560, 95, 180, 60, "Other app servers", "client-side cache", "box")
    b += _arrow(470, 50, 558, 112, "invalidations", dashed=True)
    return svg(760, 250, b, "Cache-aside: the application reads Redis first and fills it from the database on a miss")


def hot_state():
    b = _box(20, 100, 130, 56, "Application")
    b += _box(250, 90, 160, 76, "Redis primary", "AOF everysec", "rd")
    b += _box(520, 30, 150, 52, "Replica 1", "", "rd")
    b += _box(520, 170, 150, 52, "Replica 2", "", "rd")
    b += _arrow(150, 128, 248, 128, "writes, WAIT")
    b += _arrow(410, 112, 518, 60, "replication")
    b += _arrow(410, 145, 518, 192, "")
    b += _box(250, 236, 420, 40, "Sentinel ×3  ·  quorum 2  ·  promotes a replica on failure", "", "box")
    b += _arrow(330, 236, 330, 168, "", dashed=True)
    return svg(700, 290, b, "Primary with two replicas and three Sentinels for failover")


def cluster():
    b = _box(20, 105, 150, 60, "Cluster-aware client", "caches slot map")
    xs = [250, 420, 590]
    rngs = ["slots 0–5460", "5461–10922", "10923–16383"]
    for x, r in zip(xs, rngs):
        b += _box(x, 40, 150, 56, "Primary", r, "rd")
        b += _box(x, 165, 150, 50, "Replica", "", "rd")
        b += _arrow(x + 75, 96, x + 75, 163, "")
    b += _arrow(170, 125, 248, 70, "key → CRC16 mod 16384")
    b += '<text class="sm" x="495" y="245" text-anchor="middle">CLUSTER MIGRATION moves slot ranges between primaries atomically</text>'
    return svg(760, 260, b, "Redis Cluster: three shards, each a primary with a replica, keys routed by hash slot")


def managed():
    b = _box(20, 40, 160, 60, "App, region A")
    b += _box(20, 160, 160, 60, "App, region B")
    b += _box(270, 20, 230, 100, "", "", "box")
    b += f'<text x="385" y="44" text-anchor="middle">Redis Cloud · Essentials</text>'
    b += _box(290, 58, 190, 46, "one database", "replica in-zone or multi-AZ", "rd")
    b += _box(270, 140, 470, 100, "", "", "box")
    b += f'<text x="505" y="163" text-anchor="middle">Redis Cloud · Pro · Active-Active</text>'
    b += _box(290, 178, 190, 46, "copy in region A", "read + write", "rd")
    b += _box(530, 178, 190, 46, "copy in region B", "read + write", "rd")
    b += _arrow(480, 201, 528, 201, "CRDT sync", both=True)
    b += _arrow(180, 70, 288, 80, "")
    b += _arrow(180, 190, 288, 200, "")
    return svg(760, 255, b, "Redis Cloud: one replicated database on Essentials, Active-Active copies across regions on Pro")


def iris():
    b = _box(20, 110, 110, 56, "User")
    b += _box(180, 100, 170, 76, "Agent app", "LLM + your code", "box")
    b += _arrow(130, 138, 178, 138, "")
    svc = [("Intent Router", "route before the LLM", 20), ("Agent Memory", "remember · recall", 80),
           ("Agent Playbooks", "approved answers", 140), ("Context Gateway", "one MCP endpoint", 200), ("Lens", "trace each turn", 260)]
    for name, sub, y in svc:
        b += _box(430, y, 190, 48, name, sub, "rd")
        b += _arrow(350, 138, 428, y + 24, "")
    b += _box(660, 100, 100, 70, "Redis DB", "JSON + Search", "rd")
    b += _arrow(620, 104, 658, 125, "", dashed=True)      # Agent Memory: measured in iris/01
    b += _arrow(620, 216, 658, 150, "", dashed=True)      # Context Gateway: "your Redis data" (docs)
    b += _box(660, 230, 100, 56, "MCP servers", "your tools")
    b += _arrow(620, 232, 658, 252, "", dashed=True)
    return svg(780, 320, b, "Redis Iris around an agent: routing, memory, playbooks, tools and tracing, backed by a Redis database")


def search():
    b = _box(20, 80, 150, 60, "Application")
    b += _box(300, 20, 420, 180, "", "", "rd")
    b += '<text x="510" y="44" text-anchor="middle">one Redis 8 database</text>'
    b += _box(320, 60, 170, 52, "Hashes / JSON", "the records")
    b += _box(530, 60, 170, 52, "Search index", "text · numeric · vector")
    b += _box(320, 128, 380, 52, "Vector set (beta)", "VADD · VSIM, no index to define")
    b += _arrow(490, 86, 528, 86, "")
    b += _arrow(170, 110, 298, 110, "FT.SEARCH / VSIM")
    return svg(760, 215, b, "Search and vectors in the same Redis database as the records")
