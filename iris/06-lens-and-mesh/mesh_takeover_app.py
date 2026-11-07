"""Agent Mesh A2A with takeover=True: a six-step agent that records each finished step as an artifact and
skips steps already in the stored Task. Run as two replicas. /resume/{task_id} is the in-process worker call
from the A2A SDK guide ("Take over a long-running task"); a real application authorizes it.
usage: REDIS_URL=redis://127.0.0.1:16392/0 .venv/bin/python mesh_takeover_app.py <port> [--no-takeover]
"""
import asyncio
import os
import sys
import uuid
from contextlib import asynccontextmanager

import uvicorn
from a2a.server.agent_execution import AgentExecutor
from a2a.server.context import ServerCallContext
from a2a.types import (AgentCapabilities, AgentCard, AgentInterface, AgentSkill, Artifact, Message, Part, Role,
                       SendMessageRequest, Task, TaskArtifactUpdateEvent, TaskState, TaskStatus, TaskStatusUpdateEvent)
from a2a.utils import TransportProtocol
from redis.asyncio import Redis
from redis_iris.agent_mesh.a2a import RedisTaskStore
from redis_iris.agent_mesh.a2a.routes import create_resumable_rest_routes, resumable_streams_extension
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

PORT = int(sys.argv[1])
TAKEOVER = "--no-takeover" not in sys.argv
STEPS = [f"step-{i}" for i in range(1, 7)]


class Planner(AgentExecutor):
    async def execute(self, context, event_queue):
        task = context.current_task
        done = {a.artifact_id for a in task.artifacts} if task else set()
        if not task:
            await event_queue.enqueue_event(Task(id=context.task_id, context_id=context.context_id,
                                                 status=TaskStatus(state=TaskState.TASK_STATE_WORKING)))
        for step in STEPS:
            if step in done:
                continue                      # finished by an earlier process: skip it
            await asyncio.sleep(1)            # the step's work
            await event_queue.enqueue_event(TaskArtifactUpdateEvent(
                task_id=context.task_id, context_id=context.context_id, last_chunk=True,
                artifact=Artifact(artifact_id=step, parts=[Part(text=f"{step} done by {PORT}")])))
        await event_queue.enqueue_event(TaskStatusUpdateEvent(task_id=context.task_id, context_id=context.context_id,
                                                              status=TaskStatus(state=TaskState.TASK_STATE_COMPLETED)))

    async def cancel(self, context, event_queue):
        await event_queue.enqueue_event(TaskStatusUpdateEvent(task_id=context.task_id, context_id=context.context_id,
                                                              status=TaskStatus(state=TaskState.TASK_STATE_CANCELED)))


redis = Redis.from_url(os.environ["REDIS_URL"], socket_timeout=5)
store = RedisTaskStore(redis, namespace="lab:takeover" if TAKEOVER else "lab:no-takeover",
                       owner_resolver=lambda context: "lab-user", takeover=TAKEOVER)
events = store.event_stream()
card = AgentCard(name="Planner", description="Six steps", version="1.0",
                 capabilities=AgentCapabilities(streaming=True, extensions=[resumable_streams_extension()]),
                 default_input_modes=["text/plain"], default_output_modes=["text/plain"],
                 skills=[AgentSkill(id="plan", name="Plan", description="Plans", tags=["demo"])],
                 supported_interfaces=[AgentInterface(protocol_binding=TransportProtocol.HTTP_JSON,
                                                      protocol_version="1.0", url=f"http://127.0.0.1:{PORT}/")])
handler = store.request_handler(Planner(), agent_card=card)


async def resume(request):
    task_id = request.path_params["task_id"]
    task = (await store.get(task_id, ServerCallContext())).task   # StoredTask: the task and its version
    mid = f"resume-{uuid.uuid4()}"
    req = SendMessageRequest(message=Message(message_id=mid, role=Role.ROLE_USER,
                                             task_id=task_id, context_id=task.context_id, parts=[Part(text="resume")]))
    req.configuration.return_immediately = True
    try:
        result = await handler.on_message_send(req, ServerCallContext())
        state = TaskState.Name(result.status.state) if hasattr(result, "status") else type(result).__name__
        # A refused claim returns the Task unchanged and leaves the message out of its history (A2A SDK guide).
        accepted = any(m.message_id == mid for m in getattr(result, "history", []))
        return JSONResponse({"resumed_on": PORT, "accepted": accepted, "state": state,
                             "artifacts": [a.artifact_id for a in getattr(result, "artifacts", [])]})
    except Exception as e:
        return JSONResponse({"resumed_on": PORT, "error": f"{type(e).__name__}: {e}"[:200]}, status_code=409)


@asynccontextmanager
async def lifespan(app):
    async with redis:
        try:
            yield
        finally:
            await asyncio.wait_for(handler.aclose(), timeout=30)


app = Starlette(routes=[Route("/resume/{task_id}", resume, methods=["POST"]),
                        *create_resumable_rest_routes(handler, agent_card=card, store=store, event_stream=events)],
                lifespan=lifespan)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="warning")
