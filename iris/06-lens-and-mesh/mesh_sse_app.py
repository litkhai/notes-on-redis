"""Agent Mesh, FastAPI SSE: one app, run as two replicas on different ports.
Adapted from the redis.io quickstart (fastapi-sse-demo.py). Differences: no browser page, no in-memory
job table (the scope is derived from the job id so any replica can serve it), and a 0.5 s step.
usage: REDIS_URL=redis://127.0.0.1:16392/0 .venv/bin/python mesh_sse_app.py <port>
"""
import asyncio
import os
import sys
from uuid import UUID, uuid4

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse

os.environ.setdefault("REDIS_PREFIX", "lab:sse")
from redis_iris.agent_mesh.fastapi_sse import FastAPIRedis, StreamBackendDep  # noqa: E402

PORT = int(sys.argv[1])
app = FastAPI()
FastAPIRedis(app).lifespan().streams()


async def produce(writer):
    for n in range(1, 21):
        await asyncio.sleep(0.5)                       # simulated agent work
        await writer.append("progress", {"step": n, "by": PORT})
    await writer.finish("completed", {"count": 20, "by": PORT})


@app.post("/jobs")
async def start(streams: StreamBackendDep):
    job_id = str(uuid4())
    await streams.start(produce, scope=f"job:{job_id}", stream_id=job_id)
    return {"job_id": job_id, "started_on": PORT}


@app.get("/jobs/{job_id}/events", response_class=StreamingResponse)
async def events(job_id: UUID, request: Request, streams: StreamBackendDep):
    # A real application authorizes the caller for this job here. IDs and cursors grant no access.
    return await streams.sse(str(job_id), request=request, scope=f"job:{job_id}")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="warning")
