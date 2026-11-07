"""What the Lens SDK sends, without a Lens instance: point IRIS_LENS_ENDPOINT at a loopback OTLP/HTTP
receiver, run one turn with a real Agent Memory recall (iris/02 .env), a retrieval and a custom step,
and decode what arrives. Lens on Redis Cloud needs an Essentials or Pro records database (issue #8).
usage: .venv/bin/python lens_local.py [--no-content]
"""
import json
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import ExportTraceServiceRequest

received = []


class Receiver(BaseHTTPRequestHandler):
    def do_POST(self):
        body = self.rfile.read(int(self.headers["Content-Length"]))
        req = ExportTraceServiceRequest(); req.ParseFromString(body)
        received.append((self.path, dict(self.headers), req))
        self.send_response(200); self.send_header("Content-Type", "application/x-protobuf"); self.end_headers()

    def log_message(self, *a):
        pass


srv = HTTPServer(("127.0.0.1", 0), Receiver)
threading.Thread(target=srv.serve_forever, daemon=True).start()
for line in (Path(__file__).resolve().parent.parent / "02-agent-memory" / ".env").read_text().splitlines():
    if "=" in line:
        k, v = line.split("=", 1); os.environ.setdefault(k, v.strip())
os.environ.update(IRIS_LENS_ENDPOINT=f"http://127.0.0.1:{srv.server_port}", IRIS_LENS_API_KEY="local-test-key",
                  IRIS_LENS_AGENT_ID="notes-on-redis-lab")
if "--no-content" in sys.argv:
    os.environ["IRIS_LENS_CAPTURE_CONTENT"] = "false"

from redis_iris import lens  # noqa: E402
from redis_iris.agent_memory import AgentMemory, AgentMemorySettings  # noqa: E402

print("lens.init ->", lens.init())
mem = AgentMemory(AgentMemorySettings.from_env(), assistant_id="notes-on-redis-lab")
with lens.turn("lens-local-1", user_id="cust-2001") as turn:
    rec = mem.recall("how big should my Redis Cloud database be", owner="cust-2001", limit=3)
    with lens.retrieval(query="free plan limits", data_source="help-center") as s:
        s.results([("doc-free-plan", 0.91, "The free plan has 30 MB and 30 connections."), ("doc-tls", 0.42, "TLS needs a paid plan.")])
    with lens.span("rank-and-answer", candidates=2) as sp:
        sp.set_attribute("app.answer_chars", 64)
    turn.set_outcome("completed")
print("turn trace id:", turn.trace_id, "| memories recalled:", len(rec.memories))
lens.shutdown()
srv.shutdown()


STORE = os.environ.get("IRIS_AGENT_MEMORY_STORE_ID", "")


def val(v):
    k = v.WhichOneof("value"); x = getattr(v, k) if k else None
    return x if not hasattr(x, "values") else [val(i) for i in x.values]


for path, headers, req in received:
    print(f"\nPOST {path}  auth header: {'Authorization' in headers or 'authorization' in headers}  "
          f"content-type: {headers.get('Content-Type')}")
    for rs in req.resource_spans:
        print("resource:", {a.key: val(a.value) for a in rs.resource.attributes if a.key.startswith(("service", "iris", "telemetry.sdk.name"))})
        spans = [s for ss in rs.scope_spans for s in ss.spans]
        ids = {s.span_id: s.name for s in spans}
        for s in sorted(spans, key=lambda s: s.start_time_unix_nano):
            attrs = {a.key: val(a.value) for a in s.attributes}
            attrs = {k: (v.replace(STORE, "<store-id>") if isinstance(v, str) and STORE else v) for k, v in attrs.items()}
            short = {k: (v if not isinstance(v, str) or len(v) < 90 or k == "iris.retrieval.documents" else v[:87] + "...") for k, v in attrs.items()}
            print(f"- {s.name}  (parent: {ids.get(s.parent_span_id, '-')}, {(s.end_time_unix_nano - s.start_time_unix_nano) / 1e6:.0f} ms)")
            for k, v in sorted(short.items()):
                print(f"    {k} = {json.dumps(v, ensure_ascii=False)}")
