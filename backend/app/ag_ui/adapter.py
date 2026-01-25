"""AG-UI Adapter for Storybook Streaming"""
import uuid
import asyncio
import json
from typing import AsyncGenerator
from ag_ui.core import (
    RunAgentInput,
    EventType,
    RunStartedEvent,
    RunFinishedEvent,
    RunErrorEvent,
    StateSnapshotEvent,
    StateDeltaEvent,
    TextMessageStartEvent,
    TextMessageContentEvent,
    TextMessageEndEvent,
)
from ..graphs import compile_storybook_graph, create_initial_state

SSE_CONTENT_TYPE = "text/event-stream"


class EventEncoder:
    """SSE event encoder for AG-UI protocol."""

    def __init__(self, accept: str = SSE_CONTENT_TYPE):
        self.accept = accept

    def encode(self, event) -> str:
        """Encode event to SSE format."""
        data = event.model_dump_json()
        return f"data: {data}\n\n"


async def run_storybook_stream(input_data: RunAgentInput) -> AsyncGenerator[str, None]:
    """Stream AG-UI events from storybook generation."""
    encoder = EventEncoder(accept=SSE_CONTENT_TYPE)
    thread_id = input_data.thread_id or str(uuid.uuid4())
    run_id = input_data.run_id or str(uuid.uuid4())
    message_id = str(uuid.uuid4())
    in_message = False
    
    yield encoder.encode(RunStartedEvent(type=EventType.RUN_STARTED, thread_id=thread_id, run_id=run_id))
    
    user_message = ""
    for msg in input_data.messages:
        if msg.role == "user":
            user_message = msg.content
            break
    
    initial_ui_state = {"stage": "starting", "progress": 0, "characters": [], "pages": [], "characters_count": 0, "pages_count": 0, "storybook_id": None, "title": None}
    yield encoder.encode(StateSnapshotEvent(type=EventType.STATE_SNAPSHOT, snapshot=initial_ui_state))
    
    graph = compile_storybook_graph()
    initial_state = create_initial_state(user_message)
    config = {"configurable": {"thread_id": thread_id}}
    
    try:
        if hasattr(input_data, 'resume') and input_data.resume:
            from langgraph.types import Command
            resume_payload = input_data.resume.get("payload") if isinstance(input_data.resume, dict) else None
            event_stream = graph.astream_events(Command(resume=resume_payload), config=config, version="v2")
        else:
            event_stream = graph.astream_events(initial_state, config=config, version="v2")
        
        async for event in event_stream:
            event_type = event.get("event")
            
            if event_type == "on_chat_model_stream":
                chunk = event.get("data", {}).get("chunk")
                if chunk and hasattr(chunk, "content") and chunk.content:
                    if not in_message:
                        yield encoder.encode(TextMessageStartEvent(type=EventType.TEXT_MESSAGE_START, message_id=message_id, role="assistant"))
                        in_message = True
                    yield encoder.encode(TextMessageContentEvent(type=EventType.TEXT_MESSAGE_CONTENT, message_id=message_id, delta=chunk.content))
            
            elif event_type == "on_tool_end":
                tool_name = event.get("name", "")
                if tool_name == "generate_character_portrait":
                    yield encoder.encode(StateDeltaEvent(type=EventType.STATE_DELTA, delta=[{"op": "add", "path": "/characters_count", "value": 1}]))
                elif tool_name == "generate_page_image":
                    yield encoder.encode(StateDeltaEvent(type=EventType.STATE_DELTA, delta=[{"op": "add", "path": "/pages_count", "value": 1}]))
            
            await asyncio.sleep(0)
        
        if in_message:
            yield encoder.encode(TextMessageEndEvent(type=EventType.TEXT_MESSAGE_END, message_id=message_id))
        
        try:
            final_state_snapshot = graph.get_state(config)
            final_state = final_state_snapshot.values if final_state_snapshot else {}
            
            if final_state_snapshot and hasattr(final_state_snapshot, 'tasks') and final_state_snapshot.tasks:
                for task in final_state_snapshot.tasks:
                    if hasattr(task, 'interrupts') and task.interrupts:
                        interrupt_obj = task.interrupts[0]
                        yield encoder.encode(RunFinishedEvent(
                            type=EventType.RUN_FINISHED,
                            thread_id=thread_id,
                            run_id=run_id,
                            outcome="interrupt",
                            interrupt={"id": str(uuid.uuid4()), "reason": "human_input_required", "payload": interrupt_obj.value if hasattr(interrupt_obj, 'value') else {}}
                        ))
                        return
        except:
            pass
        
        yield encoder.encode(StateSnapshotEvent(type=EventType.STATE_SNAPSHOT, snapshot={"stage": "complete", "progress": 100}))
    
    except Exception as e:
        yield encoder.encode(RunErrorEvent(type=EventType.RUN_ERROR, message=str(e)))
    
    finally:
        yield encoder.encode(RunFinishedEvent(type=EventType.RUN_FINISHED, thread_id=thread_id, run_id=run_id, outcome="success"))
