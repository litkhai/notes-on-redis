"""Agent Mesh, A2A: a counting agent behind the official A2A SDK request handler with RedisTaskStore,
run as two replicas on different ports. Adapted from the redis.io quickstart (a2a-demo.py): no browser
page, ten updates at 0.5 s, and one fixed owner (loopback demo only; derive it from verified identity).
usage: REDIS_URL=redis://127.0.0.1:16392/0 .venv/bin/python mesh_a2a_app.py <port>
"""
import asyncio
import os
import sys
from contextlib import asynccontextmanager

import uvicorn
from a2a.server.agent_execution import AgentExecutor
from a2a.types import (AgentCapabilities, AgentCard, AgentInterface, AgentSkill, Artifact, Part, Task,
                       TaskArtifactUpdateEvent, TaskState, TaskStatus, TaskStatusUpdateEvent)
from a2a.utils import TransportProtocol
from redis.asyncio import Redis
from redis_iris.agent_mesh.a2a import RedisTaskStore
from redis_iris.agent_mesh.a2a.routes import create_resumable_rest_routes, resumable_streams_extension
from starlette.applications import Starlette

PORT = int(sys.argv[1])
N = 10


class CountingAgent(AgentExecutor):
    async def execute(self, context, event_queue):
        await event_queue.enqueue_event(Task(id=context.task_id, context_id=context.context_id,
                                             status=TaskStatus(state=TaskState.TASK_STATE_WORKING)))
        for n in range(1, N + 1):
            await asyncio.sleep(0.5)
            await event_queue.enqueue_event(TaskArtifactUpdateEvent(
                task_id=context.task_id, context_id=context.context_id, last_chunk=True,
                artifact=Artifact(artifact_id=f"update-{n}", parts=[Part(text=f"update {n} of {N} by {PORT}")])))
        await event_queue.enqueue_event(TaskStatusUpdateEvent(
            task_id=context.task_id, context_id=context.context_id,
            status=TaskStatus(state=TaskState.TASK_STATE_COMPLETED)))

    async def cancel(self, context, event_queue):
        await event_queue.enqueue_event(TaskStatusUpdateEvent(
            task_id=context.task_id, context_id=context.context_id,
            status=TaskStatus(state=TaskState.TASK_STATE_CANCELED)))


redis = Redis.from_url(os.environ["REDIS_URL"], socket_timeout=5)
store = RedisTaskStore(redis, namespace="lab:a2a", owner_resolver=lambda context: "lab-user")
events = store.event_stream()
card = AgentCard(
    name="Counting agent", description="Counts to ten", version="1.0",
    capabilities=AgentCapabilities(streaming=True, extensions=[resumable_streams_extension()]),
    default_input_modes=["text/plain"], default_output_modes=["text/plain"],
    skills=[AgentSkill(id="count", name="Count", description="Counts", tags=["demo"])],
    supported_interfaces=[AgentInterface(protocol_binding=TransportProtocol.HTTP_JSON,
                                         protocol_version="1.0", url=f"http://127.0.0.1:{PORT}/")])
handler = store.request_handler(CountingAgent(), agent_card=card, event_stream=events)


@asynccontextmanager
async def lifespan(app):
    async with redis:
        try:
            yield
        finally:
            await asyncio.wait_for(handler.aclose(), timeout=30)


app = Starlette(routes=create_resumable_rest_routes(handler, agent_card=card, store=store, event_stream=events),
                lifespan=lifespan)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="warning")
