"""AG-UI Adapter for Storybook Streaming"""
import uuid
import asyncio
import json
import re
from typing import AsyncGenerator, Optional
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
    CustomEvent,
)
from ..graphs import get_graph

SSE_CONTENT_TYPE = "text/event-stream"

# Stage to review type mapping (used for UI inference)
STAGE_TO_REVIEW_TYPE = {
    "enhance": "story_review",
    "portrait": "character_review",
    "story": "pages_review"
}


class ToolCallAccumulator:
    """Accumulates streaming tool call arguments for partial JSON parsing."""

    def __init__(self):
        self.tool_name: Optional[str] = None
        self.tool_id: Optional[str] = None
        self.args_buffer: str = ""

    def reset(self):
        """Reset accumulator for new tool call."""
        self.tool_name = None
        self.tool_id = None
        self.args_buffer = ""

    def update(self, tool_call_chunk: dict) -> Optional[dict]:
        """
        Update with a tool call chunk, return parsed data if possible.

        Args:
            tool_call_chunk: Chunk from LLM stream with name/id/args

        Returns:
            Parsed data dict or None if not yet parseable
        """
        # First chunk has name/id
        if tool_call_chunk.get("name"):
            self.tool_name = tool_call_chunk["name"]
        if tool_call_chunk.get("id"):
            self.tool_id = tool_call_chunk["id"]

        # Accumulate args string
        if tool_call_chunk.get("args"):
            self.args_buffer += tool_call_chunk["args"]

        # Try to extract partial data
        return self._try_parse_partial()

    def _try_parse_partial(self) -> Optional[dict]:
        """Attempt to parse partial JSON for preview."""
        if not self.args_buffer:
            return None

        try:
            # Try full parse first
            parsed = json.loads(self.args_buffer)
            # For user_interaction, args is: {"type": "story_review", "data": {"enhanced_story": "...", ...}}
            return {
                "type": parsed.get("type"),
                "data": parsed.get("data", {})
            }
        except json.JSONDecodeError:
            # Partial JSON - extract what we can
            return self._extract_partial_fields()

    def _extract_partial_fields(self) -> Optional[dict]:
        """Extract fields from incomplete JSON string."""
        result = {"type": None, "data": {}}

        # Extract type if present
        type_match = re.search(
            r'"type"\s*:\s*"(story_review|character_review|pages_review)"',
            self.args_buffer
        )
        if type_match:
            result["type"] = type_match.group(1)

        # Extract enhanced_story if present (greedy match to last quote)
        story_match = re.search(
            r'"enhanced_story"\s*:\s*"((?:[^"\\]|\\.)*?)(?:"|$)',
            self.args_buffer,
            re.DOTALL
        )
        if story_match:
            # Unescape JSON string
            story_text = story_match.group(1).replace('\\"', '"').replace('\\n', '\n')
            result["data"]["enhanced_story"] = story_text

        # Extract characters array if it looks complete
        # Look for "characters": [...] pattern
        chars_match = re.search(
            r'"characters"\s*:\s*\[(.*?)\]',
            self.args_buffer,
            re.DOTALL
        )
        if chars_match:
            try:
                # Try to parse the characters array
                chars_json = f'[{chars_match.group(1)}]'
                characters = json.loads(chars_json)
                result["data"]["characters"] = characters
            except:
                # Partial characters array, skip for now
                pass

        return result if (result["type"] or result["data"]) else None


def snake_to_camel(name: str) -> str:
    """Convert snake_case to camelCase."""
    components = name.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


def convert_event_keys(obj):
    """Recursively convert dict keys from snake_case to camelCase.
    Also removes None values since Zod expects undefined, not null.
    Used only for AG-UI event envelope fields (not user state data).
    """
    if isinstance(obj, dict):
        result = {}
        for k, v in obj.items():
            # Skip None values - Zod expects undefined (missing), not null
            if v is None:
                continue
            result[snake_to_camel(k)] = convert_event_keys(v)
        return result
    elif isinstance(obj, list):
        return [convert_event_keys(item) for item in obj]
    else:
        return obj


class EventEncoder:
    """SSE event encoder for AG-UI protocol."""

    def __init__(self, accept: str = SSE_CONTENT_TYPE):
        self.accept = accept

    def encode(self, event) -> str:
        """Encode event to SSE format with camelCase keys.
        
        Note: AG-UI pydantic models use snake_case (thread_id, run_id, message_id)
        but CopilotKit expects camelCase (threadId, runId, messageId).
        We convert the event envelope here. State data is already camelCase.
        """
        data_dict = event.model_dump()
        # Convert event envelope keys to camelCase, remove None values
        camel_dict = convert_event_keys(data_dict)
        data = json.dumps(camel_dict)
        
        # Extra logging for interrupt events
        if camel_dict.get('outcome') == 'interrupt':
            print(f"[AG-UI Encoder] ===== INTERRUPT EVENT =====")
            print(f"[AG-UI Encoder] Full event: {json.dumps(camel_dict, indent=2)}")
            print(f"[AG-UI Encoder] =========================")
        else:
            print(f"[AG-UI Encoder] Sending event: {data[:200]}...")
        
        return f"data: {data}\n\n"


async def run_storybook_stream(input_data: RunAgentInput) -> AsyncGenerator[str, None]:
    """Stream AG-UI events from storybook generation."""
    encoder = EventEncoder(accept=SSE_CONTENT_TYPE)

    # Use provided thread_id or generate new one
    thread_id = input_data.thread_id or str(uuid.uuid4())

    # Always generate new run_id to avoid state machine conflicts
    # CRITICAL: Each execution needs its own run_id even if using same thread_id
    run_id = str(uuid.uuid4())

    message_id = str(uuid.uuid4())
    in_message = False
    has_error = False  # Track if we've sent an error event

    # Tool call accumulator for streaming
    tool_accumulator = ToolCallAccumulator()
    last_emitted_story = ""  # Track to avoid duplicate emissions
    review_type_emitted = False  # Track if we've emitted reviewType
    current_stage = None  # Track current stage for reviewType inference
    
    # Track portrait generation state
    portrait_review_emitted = False  # Track if we've emitted character_review
    portrait_generating_count = 0  # Track number of portraits being generated
    
    # Track pages generation state
    pages_review_emitted = False  # Track if we've emitted pages_review
    page_generating_count = 0  # Track number of pages being generated

    # Extract resume from forwarded_props (CopilotKit sends it here)
    resume_value = None
    if hasattr(input_data, 'forwarded_props') and input_data.forwarded_props:
        if isinstance(input_data.forwarded_props, dict):
            # Check for command.resume pattern
            command = input_data.forwarded_props.get('command', {})
            if isinstance(command, dict):
                resume_value = command.get('resume')

    print(f"\n{'='*80}")
    print(f"[AG-UI Stream] Starting new storybook generation")
    print(f"[AG-UI Stream]   thread_id: {thread_id}")
    print(f"[AG-UI Stream]   run_id: {run_id} (always new)")
    print(f"[AG-UI Stream]   resume: {resume_value}")
    print(f"[AG-UI Stream]   forwarded_props: {json.dumps(input_data.forwarded_props, indent=2, default=str) if hasattr(input_data, 'forwarded_props') else 'None'}")
    print(f"{'='*80}\n")

    # Send RUN_STARTED
    yield encoder.encode(RunStartedEvent(
        type=EventType.RUN_STARTED,
        thread_id=thread_id,
        run_id=run_id
    ))

    # Extract latest user message
    latest_user_message = None
    for msg in reversed(input_data.messages):
        if msg.role == "user":
            latest_user_message = msg.content
            break

    print(f"[AG-UI Stream] Latest user message: {latest_user_message[:100] if latest_user_message else 'None'}...")

    if not latest_user_message:
        # No user message - just finish cleanly
        print("[AG-UI Stream] No user message found, finishing immediately")
        yield encoder.encode(RunFinishedEvent(
            type=EventType.RUN_FINISHED,
            thread_id=thread_id,
            run_id=run_id
        ))
        return
    
    # Build initial state snapshot
    # When resuming, load existing state from checkpointer to preserve characters/pages
    initial_ui_state = {
        "currentStage": "starting",
        "progress": 0,
        "characters": [],
        "pages": [],
        "charactersCount": 0,
        "pagesCount": 0,
        "storybookId": "",
        "title": "",
        "reviewType": "",
        "isStreaming": False,
        "portraitGeneratingIndex": -1,
        "pageGeneratingIndex": -1,
        "enhancedStory": "",
        "enhancedStoryPartial": "",
        "charactersPartial": [],
    }
    
    # If resuming, load existing state from graph checkpointer
    if resume_value:
        try:
            graph = get_graph()
            config = {"configurable": {"thread_id": thread_id}}
            existing_state = graph.get_state(config)
            if existing_state and existing_state.values:
                vals = existing_state.values
                print(f"[AG-UI Stream] Loading existing state for resume:")
                print(f"[AG-UI Stream]   enhanced_story: {len(vals.get('enhanced_story', '') or '')} chars")
                print(f"[AG-UI Stream]   characters: {len(vals.get('characters', []))} items")
                print(f"[AG-UI Stream]   pages: {len(vals.get('pages', []))} items")
                
                # Populate from checkpointer state
                if vals.get("enhanced_story"):
                    initial_ui_state["enhancedStory"] = vals["enhanced_story"]
                if vals.get("characters"):
                    initial_ui_state["characters"] = vals["characters"]
                    initial_ui_state["charactersCount"] = len(vals["characters"])
                if vals.get("pages"):
                    initial_ui_state["pages"] = vals["pages"]
                    initial_ui_state["pagesCount"] = len(vals["pages"])
                if vals.get("storybook_id"):
                    initial_ui_state["storybookId"] = vals["storybook_id"]
                if vals.get("current_stage"):
                    initial_ui_state["currentStage"] = vals["current_stage"]
        except Exception as e:
            print(f"[AG-UI Stream] Warning: Could not load existing state: {e}")
    
    yield encoder.encode(StateSnapshotEvent(
        type=EventType.STATE_SNAPSHOT,
        snapshot=initial_ui_state
    ))

    try:
        # Get singleton graph instance with persistent checkpointer
        graph = get_graph()

        # Config with thread_id and recursion_limit
        config = {
            "configurable": {"thread_id": thread_id},
            "recursion_limit": 10
        }

        print(f"[AG-UI Stream] Starting graph execution...")

        # Check if there's an active interrupt on this thread
        has_active_interrupt = False
        active_interrupt_type = None
        try:
            state_snapshot = graph.get_state(config)
            if state_snapshot and hasattr(state_snapshot, 'tasks') and state_snapshot.tasks:
                for task in state_snapshot.tasks:
                    if hasattr(task, 'interrupts') and task.interrupts:
                        has_active_interrupt = True
                        interrupt_obj = task.interrupts[0]
                        interrupt_value = interrupt_obj.value if hasattr(interrupt_obj, 'value') else {}
                        active_interrupt_type = interrupt_value.get("type")
                        print(f"[AG-UI Stream] 🔄 Detected active interrupt on thread")
                        print(f"[AG-UI Stream]   interrupt type: {active_interrupt_type}")
                        break
        except Exception as e:
            print(f"[AG-UI Stream] Warning: Could not check for active interrupt: {e}")

        # Use resume if there's explicit resume value OR active interrupt
        if resume_value or has_active_interrupt:
            actual_resume = resume_value or latest_user_message
            print(f"[AG-UI Stream] Resuming from interrupt")
            print(f"[AG-UI Stream]   resume value: {actual_resume[:100] if actual_resume else 'None'}...")
            print(f"[AG-UI Stream]   interrupt type: {active_interrupt_type}")
            
            from langgraph.types import Command
            
            # For review interrupts with APPROVED, set a flag so node can skip subgraph re-run
            # The data (enhanced_story, characters, pages) is in the interrupt payload
            state_update = {}
            if active_interrupt_type in ["story_review", "character_review", "pages_review"]:
                if resume_value == "APPROVED":
                    # Extract data from interrupt payload to persist in state
                    try:
                        state_snapshot = graph.get_state(config)
                        if state_snapshot and hasattr(state_snapshot, 'tasks') and state_snapshot.tasks:
                            for task in state_snapshot.tasks:
                                if hasattr(task, 'interrupts') and task.interrupts:
                                    interrupt_obj = task.interrupts[0]
                                    interrupt_value = interrupt_obj.value if hasattr(interrupt_obj, 'value') else {}
                                    interrupt_data = interrupt_value.get("data", {})
                                    
                                    # Set the flag and data so node can skip subgraph
                                    state_update["review_type"] = active_interrupt_type
                                    if interrupt_data.get("enhanced_story"):
                                        state_update["enhanced_story"] = interrupt_data["enhanced_story"]
                                    if interrupt_data.get("characters"):
                                        state_update["characters"] = interrupt_data["characters"]
                                    if interrupt_data.get("pages"):
                                        state_update["pages"] = interrupt_data["pages"]
                                    break
                        print(f"[AG-UI Stream] 📦 Extracted interrupt data for state: {list(state_update.keys())}")
                    except Exception as e:
                        print(f"[AG-UI Stream] Warning: Could not extract interrupt data: {e}")
            
            # Pass resume value with optional state update
            # Node checks review_type to decide whether to skip subgraph
            print(f"[AG-UI Stream] 📤 Passing resume to node (node handles routing)")
            if state_update:
                print(f"[AG-UI Stream]   with state_update: {list(state_update.keys())}")
                event_stream = graph.astream_events(
                    Command(update=state_update, resume=actual_resume),
                    config=config,
                    version="v2"
                )
            else:
                event_stream = graph.astream_events(
                    Command(resume=actual_resume),
                    config=config,
                    version="v2"
                )
        else:
            # No active interrupt - start fresh or continue conversation
            print(f"[AG-UI Stream] Starting fresh conversation (no active interrupt)")
            event_stream = graph.astream_events(
                {"messages": [{"role": "user", "content": latest_user_message}]},
                config=config,
                version="v2"
            )

        # Stream events
        async for event in event_stream:
            event_type = event.get("event")

            # Track current stage from event metadata
            if event_type == "on_chain_start":
                event_name = event.get("name", "")
                if event_name in ["enhance", "portrait", "story"]:
                    previous_stage = current_stage
                    current_stage = event_name
                    print(f"[AG-UI Stream] 🎬 Detected stage: {current_stage}")
                    
                    # Emit stage change as currentStage delta
                    yield encoder.encode(StateDeltaEvent(
                        type=EventType.STATE_DELTA,
                        delta=[{
                            "op": "replace",
                            "path": "/currentStage",
                            "value": current_stage
                        }]
                    ))
                    
                    # When transitioning TO portrait, the enhance Command has now been processed
                    # Query graph state to get the characters that were just added
                    if current_stage == "portrait" and previous_stage == "enhance":
                        try:
                            graph = get_graph()
                            config = {"configurable": {"thread_id": thread_id}}
                            current_graph_state = graph.get_state(config)
                            if current_graph_state and current_graph_state.values:
                                vals = current_graph_state.values
                                characters = vals.get("characters", [])
                                enhanced_story = vals.get("enhanced_story", "")
                                print(f"[AG-UI Stream] 📚 Transition to portrait - syncing state:")
                                print(f"[AG-UI Stream]   characters: {len(characters)} items")
                                print(f"[AG-UI Stream]   enhanced_story: {len(enhanced_story or '')} chars")
                                
                                if characters or enhanced_story:
                                    sync_patches = []
                                    if enhanced_story:
                                        sync_patches.append({
                                            "op": "replace",
                                            "path": "/enhancedStory",
                                            "value": enhanced_story
                                        })
                                    if characters:
                                        sync_patches.append({
                                            "op": "replace",
                                            "path": "/characters",
                                            "value": characters
                                        })
                                        sync_patches.append({
                                            "op": "replace",
                                            "path": "/charactersCount",
                                            "value": len(characters)
                                        })
                                    if sync_patches:
                                        yield encoder.encode(StateDeltaEvent(
                                            type=EventType.STATE_DELTA,
                                            delta=sync_patches
                                        ))
                        except Exception as e:
                            print(f"[AG-UI Stream] Warning: Could not sync state on portrait transition: {e}")
                    
                    # When transitioning TO story, the portrait Command has now been processed
                    # Query graph state to get the characters with image_ids
                    if current_stage == "story" and previous_stage == "portrait":
                        try:
                            graph = get_graph()
                            config = {"configurable": {"thread_id": thread_id}}
                            current_graph_state = graph.get_state(config)
                            if current_graph_state and current_graph_state.values:
                                vals = current_graph_state.values
                                characters = vals.get("characters", [])
                                enhanced_story = vals.get("enhanced_story", "")
                                print(f"[AG-UI Stream] 📚 Transition to story - syncing state:")
                                print(f"[AG-UI Stream]   characters: {len(characters)} items")
                                print(f"[AG-UI Stream]   characters with images: {sum(1 for c in characters if c.get('image_id'))}")
                                print(f"[AG-UI Stream]   enhanced_story: {len(enhanced_story or '')} chars")
                                
                                if characters or enhanced_story:
                                    sync_patches = []
                                    if enhanced_story:
                                        sync_patches.append({
                                            "op": "replace",
                                            "path": "/enhancedStory",
                                            "value": enhanced_story
                                        })
                                    if characters:
                                        sync_patches.append({
                                            "op": "replace",
                                            "path": "/characters",
                                            "value": characters
                                        })
                                        sync_patches.append({
                                            "op": "replace",
                                            "path": "/charactersCount",
                                            "value": len(characters)
                                        })
                                    if sync_patches:
                                        yield encoder.encode(StateDeltaEvent(
                                            type=EventType.STATE_DELTA,
                                            delta=sync_patches
                                        ))
                        except Exception as e:
                            print(f"[AG-UI Stream] Warning: Could not sync state on story transition: {e}")

            # Stream LLM tokens
            if event_type == "on_chat_model_stream":
                chunk = event.get("data", {}).get("chunk")
                if not chunk:
                    continue

                # === TEXT CONTENT STREAMING ===
                if hasattr(chunk, "content") and chunk.content:
                    # Extract text from chunk.content (handle both string and list formats)
                    content_text = ""
                    if isinstance(chunk.content, str):
                        content_text = chunk.content
                    elif isinstance(chunk.content, list):
                        for item in chunk.content:
                            if isinstance(item, dict) and "text" in item:
                                content_text += item["text"]

                    if content_text:
                        if not in_message:
                            yield encoder.encode(TextMessageStartEvent(
                                type=EventType.TEXT_MESSAGE_START,
                                message_id=message_id,
                                role="assistant"
                            ))
                            in_message = True
                        yield encoder.encode(TextMessageContentEvent(
                            type=EventType.TEXT_MESSAGE_CONTENT,
                            message_id=message_id,
                            delta=content_text
                        ))

                # === TOOL CALL ARGUMENT STREAMING ===
                if hasattr(chunk, "tool_call_chunks") and chunk.tool_call_chunks:
                    for tc_chunk in chunk.tool_call_chunks:
                        # Check if it's present_enhanced_story tool
                        tool_name = tool_accumulator.tool_name or tc_chunk.get("name")

                        if tool_name == "present_enhanced_story":
                            # Update accumulator and get partial data
                            partial_data = tool_accumulator.update(tc_chunk)

                            if partial_data:
                                # STEP 1: Emit reviewType FIRST (separate event)
                                if not review_type_emitted:
                                    # present_enhanced_story is only used in enhance stage
                                    review_type = "story_review"

                                    print(f"[AG-UI Stream] 📖 Emitting reviewType: {review_type} (tool: {tool_name})")
                                    yield encoder.encode(StateDeltaEvent(
                                        type=EventType.STATE_DELTA,
                                        delta=[
                                            {
                                                "op": "replace",
                                                "path": "/reviewType",
                                                "value": review_type
                                            },
                                            {
                                                "op": "replace",
                                                "path": "/isStreaming",
                                                "value": True
                                            }
                                        ]
                                    ))
                                    review_type_emitted = True
                                    # Give frontend time to render component

                                # STEP 2: Then emit data deltas (separate event)
                                data_patches = []

                                # Try to parse complete JSON first
                                try:
                                    args = json.loads(tool_accumulator.args_buffer)
                                    story = args.get("enhanced_story", "")
                                    chars = args.get("characters", [])
                                except json.JSONDecodeError:
                                    # Partial JSON - extract what we can with regex
                                    story_match = re.search(
                                        r'"enhanced_story"\s*:\s*"((?:[^"\\]|\\.)*?)(?:"|$)',
                                        tool_accumulator.args_buffer,
                                        re.DOTALL
                                    )
                                    story = story_match.group(1).replace('\\"', '"').replace('\\n', '\n') if story_match else ""

                                    chars_match = re.search(
                                        r'"characters"\s*:\s*\[(.*?)\]',
                                        tool_accumulator.args_buffer,
                                        re.DOTALL
                                    )
                                    try:
                                        chars = json.loads(f'[{chars_match.group(1)}]') if chars_match else []
                                    except:
                                        chars = []

                                if story and story != last_emitted_story:
                                    data_patches.append({
                                        "op": "replace",
                                        "path": "/enhancedStoryPartial",
                                        "value": story
                                    })
                                    last_emitted_story = story
                                    print(f"[AG-UI Stream] Streaming story partial: {len(story)} chars")

                                if chars:
                                    data_patches.append({
                                        "op": "replace",
                                        "path": "/charactersPartial",
                                        "value": chars
                                    })
                                    print(f"[AG-UI Stream] Streaming characters partial: {len(chars)} items")

                                if data_patches:
                                    yield encoder.encode(StateDeltaEvent(
                                        type=EventType.STATE_DELTA,
                                        delta=data_patches
                                    ))

            # === TOOL START: Detect when portrait/page generation begins ===
            elif event_type == "on_tool_start":
                tool_name = event.get("name", "")
                
                # Detect portrait generation start
                if tool_name == "generate_character_portrait":
                    portrait_generating_count += 1
                    
                    # Emit character_review type on first portrait generation
                    if not portrait_review_emitted:
                        print(f"[AG-UI Stream] 🎨 First portrait generation starting - emitting character_review")
                        yield encoder.encode(StateDeltaEvent(
                            type=EventType.STATE_DELTA,
                            delta=[
                                {
                                    "op": "replace",
                                    "path": "/reviewType",
                                    "value": "character_review"
                                },
                                {
                                    "op": "replace",
                                    "path": "/isStreaming",
                                    "value": True
                                },
                                {
                                    "op": "replace",
                                    "path": "/portraitGeneratingIndex",
                                    "value": portrait_generating_count - 1
                                }
                            ]
                        ))
                        portrait_review_emitted = True
                    else:
                        # Update which portrait is generating
                        yield encoder.encode(StateDeltaEvent(
                            type=EventType.STATE_DELTA,
                            delta=[{
                                "op": "replace",
                                "path": "/portraitGeneratingIndex",
                                "value": portrait_generating_count - 1
                            }]
                        ))
                
                # Detect page generation start
                elif tool_name == "generate_page_image":
                    page_generating_count += 1
                    
                    # Emit pages_review type on first page generation
                    if not pages_review_emitted:
                        print(f"[AG-UI Stream] 📄 First page generation starting - emitting pages_review")
                        yield encoder.encode(StateDeltaEvent(
                            type=EventType.STATE_DELTA,
                            delta=[
                                {
                                    "op": "replace",
                                    "path": "/reviewType",
                                    "value": "pages_review"
                                },
                                {
                                    "op": "replace",
                                    "path": "/isStreaming",
                                    "value": True
                                },
                                {
                                    "op": "replace",
                                    "path": "/pageGeneratingIndex",
                                    "value": page_generating_count - 1
                                }
                            ]
                        ))
                        pages_review_emitted = True
                    else:
                        # Update which page is generating
                        yield encoder.encode(StateDeltaEvent(
                            type=EventType.STATE_DELTA,
                            delta=[{
                                "op": "replace",
                                "path": "/pageGeneratingIndex",
                                "value": page_generating_count - 1
                            }]
                        ))

            # Emit state deltas for tool completions
            elif event_type == "on_tool_end":
                tool_name = event.get("name", "")
                print(f"[AG-UI Stream] ✅ Tool completed: {tool_name}")

                # Handle present_enhanced_story tool completion
                if tool_name == "present_enhanced_story":
                    # Get tool input args
                    tool_input = event.get("data", {}).get("input", {})
                    if tool_input:
                        patches = []
                        if "enhanced_story" in tool_input:
                            patches.append({
                                "op": "replace",
                                "path": "/enhancedStory",
                                "value": tool_input["enhanced_story"]
                            })
                        if "characters" in tool_input:
                            patches.append({
                                "op": "replace",
                                "path": "/characters",
                                "value": tool_input["characters"]
                            })

                        if patches:
                            print(f"[AG-UI Stream] Emitting final data from present_enhanced_story")
                            yield encoder.encode(StateDeltaEvent(
                                type=EventType.STATE_DELTA,
                                delta=patches
                            ))

                    # Reset accumulator and clear streaming state
                    tool_accumulator.reset()
                    last_emitted_story = ""
                    review_type_emitted = False

                    # Emit streaming finished signal
                    print(f"[AG-UI Stream] Emitting isStreaming: False")
                    yield encoder.encode(StateDeltaEvent(
                        type=EventType.STATE_DELTA,
                        delta=[{
                            "op": "replace",
                            "path": "/isStreaming",
                            "value": False
                        }]
                    ))

                elif tool_name == "generate_character_portrait":
                    # Get tool input and output
                    tool_input = event.get("data", {}).get("input", {})
                    tool_output_raw = event.get("data", {}).get("output")

                    if tool_input and tool_output_raw:
                        # Parse tool output - it might be ToolMessage object or dict
                        if hasattr(tool_output_raw, "content"):
                            # ToolMessage object - parse content
                            try:
                                tool_output = json.loads(tool_output_raw.content) if isinstance(tool_output_raw.content, str) else tool_output_raw.content
                            except:
                                tool_output = {}
                        else:
                            # Already a dict
                            tool_output = tool_output_raw

                        # Get index from tool output (preferred) or input
                        character_index = tool_output.get("index", tool_input.get("character_index", 0))
                        image_id = tool_output.get("image_id")
                        image_url = tool_output.get("image_url")

                        if image_url:
                            # Use JSON Patch to update specific character by index
                            print(f"[AG-UI Stream] 🖼️ Updating character at index {character_index} with imageUrl")
                            yield encoder.encode(StateDeltaEvent(
                                type=EventType.STATE_DELTA,
                                delta=[
                                    {
                                        "op": "add",
                                        "path": f"/characters/{character_index}/imageId",
                                        "value": image_id
                                    },
                                    {
                                        "op": "add",
                                        "path": f"/characters/{character_index}/imageUrl",
                                        "value": image_url
                                    }
                                ]
                            ))

                    # Also increment counter for progress tracking
                    yield encoder.encode(StateDeltaEvent(
                        type=EventType.STATE_DELTA,
                        delta=[{"op": "add", "path": "/charactersCount", "value": 1}]
                    ))
                    
                elif tool_name == "generate_page_image":
                    # Get tool input and output
                    tool_input = event.get("data", {}).get("input", {})
                    tool_output_raw = event.get("data", {}).get("output")
                    
                    if tool_output_raw:
                        # Parse tool output
                        if hasattr(tool_output_raw, "content"):
                            try:
                                tool_output = json.loads(tool_output_raw.content) if isinstance(tool_output_raw.content, str) else tool_output_raw.content
                            except:
                                tool_output = {}
                        else:
                            tool_output = tool_output_raw
                        
                        page_number = tool_output.get("page_number", tool_input.get("page_number", 0))
                        image_url = tool_output.get("image_url")
                        image_id = tool_output.get("image_id")
                        
                        if image_url:
                            print(f"[AG-UI Stream] 📄 Page {page_number} generated with imageUrl")
                            # Add the page to pages array (camelCase keys)
                            yield encoder.encode(StateDeltaEvent(
                                type=EventType.STATE_DELTA,
                                delta=[{
                                    "op": "add",
                                    "path": "/pages/-",  # Append to array
                                    "value": {
                                        "pageNumber": page_number,
                                        "imageId": image_id,
                                        "imageUrl": image_url,
                                        "prompt": tool_input.get("prompt", "")  # Scene description
                                    }
                                }]
                            ))
                    
                    # Increment counter for progress tracking
                    yield encoder.encode(StateDeltaEvent(
                        type=EventType.STATE_DELTA,
                        delta=[{"op": "add", "path": "/pagesCount", "value": 1}]
                    ))

            # Yield control periodically
            await asyncio.sleep(0)

        # End message if we were streaming one
        if in_message:
            yield encoder.encode(TextMessageEndEvent(
                type=EventType.TEXT_MESSAGE_END,
                message_id=message_id
            ))
            in_message = False

        print(f"[AG-UI Stream] Graph execution completed, checking for interrupts...")

        # Check for interrupts
        try:
            final_state_snapshot = graph.get_state(config)
            if final_state_snapshot and hasattr(final_state_snapshot, 'tasks') and final_state_snapshot.tasks:
                for task in final_state_snapshot.tasks:
                    if hasattr(task, 'interrupts') and task.interrupts:
                        print(f"[AG-UI Stream] Found interrupt, pausing execution")
                        interrupt_obj = task.interrupts[0]
                        interrupt_value = interrupt_obj.value if hasattr(interrupt_obj, 'value') else {}

                        # DEBUG: Log the actual interrupt data
                        print(f"[AG-UI Stream] Interrupt data: {json.dumps(interrupt_value, indent=2)}")

                        # Check interrupt type
                        interrupt_type = interrupt_value.get("type")
                        
                        # Emit isStreaming: false when interrupt happens
                        yield encoder.encode(StateDeltaEvent(
                            type=EventType.STATE_DELTA,
                            delta=[{
                                "op": "replace",
                                "path": "/isStreaming",
                                "value": False
                            }]
                        ))

                        if interrupt_type == "text":
                            # Text interrupt: message already sent via streaming
                            # No CustomEvent needed - frontend renders from messages
                            print(f"[AG-UI Stream] Text interrupt - message already streamed, sending RUN_FINISHED only")
                            yield encoder.encode(RunFinishedEvent(
                                type=EventType.RUN_FINISHED,
                                thread_id=thread_id,
                                run_id=run_id,
                                # outcome="interrupt"
                            ))
                        else:
                            # Other interrupt types: need user approval, send CustomEvent
                            print(f"[AG-UI Stream] Non-text interrupt (type={interrupt_type}) - sending CustomEvent")
                            print(f"[AG-UI Stream]   event value: {json.dumps(interrupt_value, indent=2)}")

                            yield encoder.encode(CustomEvent(
                                type=EventType.CUSTOM,
                                name="on_interrupt",
                                value=interrupt_value
                            ))

                            yield encoder.encode(RunFinishedEvent(
                                type=EventType.RUN_FINISHED,
                                thread_id=thread_id,
                                run_id=run_id,
                                # outcome="interrupt"
                            ))

                        print(f"[AG-UI Stream] Interrupt events sent, waiting for resume...")
                        return
        except Exception as e:
            print(f"[AG-UI Stream] Error checking for interrupts: {e}")
            import traceback
            traceback.print_exc()
            # Continue to normal completion if interrupt check fails

        print(f"[AG-UI Stream] No interrupts, completing successfully")

        # Send final state snapshot
        yield encoder.encode(StateSnapshotEvent(
            type=EventType.STATE_SNAPSHOT,
            snapshot={"stage": "complete", "progress": 100}
        ))

        # Send RUN_FINISHED
        yield encoder.encode(RunFinishedEvent(
            type=EventType.RUN_FINISHED,
            thread_id=thread_id,
            run_id=run_id
        ))

        print(f"[AG-UI Stream] Stream completed successfully\n")

    except RuntimeError as e:
        # Interrupt exceptions are RuntimeError - this is the HITL flow
        if "interrupt" in str(e).lower() or "Called get_config" in str(e):
            print(f"\n[AG-UI Stream] Interrupt exception caught (expected HITL flow)")

            # End message if we were streaming one
            if in_message:
                try:
                    yield encoder.encode(TextMessageEndEvent(
                        type=EventType.TEXT_MESSAGE_END,
                        message_id=message_id
                    ))
                except Exception as end_err:
                    print(f"[AG-UI Stream] Failed to send TEXT_MESSAGE_END: {end_err}")
                in_message = False

            # Check graph state for interrupt details
            try:
                final_state_snapshot = graph.get_state(config)
                if final_state_snapshot and hasattr(final_state_snapshot, 'tasks') and final_state_snapshot.tasks:
                    for task in final_state_snapshot.tasks:
                        if hasattr(task, 'interrupts') and task.interrupts:
                            interrupt_obj = task.interrupts[0]
                            interrupt_value = interrupt_obj.value if hasattr(interrupt_obj, 'value') else {}

                            print(f"[AG-UI Stream] Interrupt value: {json.dumps(interrupt_value, indent=2)}")

                            interrupt_type = interrupt_value.get("type")
                            
                            # Emit isStreaming: false when interrupt happens
                            yield encoder.encode(StateDeltaEvent(
                                type=EventType.STATE_DELTA,
                                delta=[{
                                    "op": "replace",
                                    "path": "/isStreaming",
                                    "value": False
                                }]
                            ))

                            if interrupt_type == "text":
                                # Text interrupt - message already streamed
                                # No CustomEvent needed
                                print(f"[AG-UI Stream] Text interrupt detected")
                                yield encoder.encode(RunFinishedEvent(
                                    type=EventType.RUN_FINISHED,
                                    thread_id=thread_id,
                                    run_id=run_id,
                                    # outcome="interrupt"
                                ))
                            else:
                                # Other interrupt types - send CustomEvent for approval UI
                                print(f"[AG-UI Stream] Sending CustomEvent for type={interrupt_type}")
                                yield encoder.encode(CustomEvent(
                                    type=EventType.CUSTOM,
                                    name="on_interrupt",
                                    value=interrupt_value
                                ))

                                yield encoder.encode(RunFinishedEvent(
                                    type=EventType.RUN_FINISHED,
                                    thread_id=thread_id,
                                    run_id=run_id,
                                    # outcome="interrupt"
                                ))

                            print(f"[AG-UI Stream] Interrupt handled, waiting for resume...\n")
                            return
            except Exception as state_err:
                print(f"[AG-UI Stream] Error getting interrupt state: {state_err}")
                import traceback
                traceback.print_exc()

            # Fallback: send generic interrupt event
            print(f"[AG-UI Stream] Sending fallback interrupt event")
            yield encoder.encode(RunFinishedEvent(
                type=EventType.RUN_FINISHED,
                thread_id=thread_id,
                run_id=run_id,
                # outcome="interrupt"
            ))
            return

        # Other RuntimeErrors are real errors
        print(f"\n[AG-UI Stream] RuntimeError (not interrupt): {e}")
        import traceback
        traceback.print_exc()
        has_error = True

        if in_message:
            try:
                yield encoder.encode(TextMessageEndEvent(
                    type=EventType.TEXT_MESSAGE_END,
                    message_id=message_id
                ))
            except Exception as end_err:
                print(f"[AG-UI Stream] Failed to send TEXT_MESSAGE_END: {end_err}")
            in_message = False

        try:
            yield encoder.encode(RunErrorEvent(
                type=EventType.RUN_ERROR,
                thread_id=thread_id,
                run_id=run_id,
                message=str(e)
            ))
        except Exception as error_event_err:
            print(f"[AG-UI Stream] Failed to send RUN_ERROR: {error_event_err}")

        print(f"[AG-UI Stream] Stream ended with error\n")
        return

    except Exception as e:
        print(f"\n[AG-UI Stream] ERROR occurred: {e}")
        import traceback
        traceback.print_exc()
        has_error = True

        # If we were in the middle of a message, end it first
        if in_message:
            try:
                yield encoder.encode(TextMessageEndEvent(
                    type=EventType.TEXT_MESSAGE_END,
                    message_id=message_id
                ))
            except Exception as end_err:
                print(f"[AG-UI Stream] Failed to send TEXT_MESSAGE_END: {end_err}")
            in_message = False

        # Send RUN_ERROR
        try:
            error_message = str(e)
            print(f"[AG-UI Stream] Sending RUN_ERROR with message: {error_message}")
            yield encoder.encode(RunErrorEvent(
                type=EventType.RUN_ERROR,
                thread_id=thread_id,
                run_id=run_id,
                message=error_message
            ))
        except Exception as error_event_err:
            print(f"[AG-UI Stream] Failed to send RUN_ERROR: {error_event_err}")

        # Don't send RUN_FINISHED after RUN_ERROR - protocol violation
        print(f"[AG-UI Stream] Stream ended with error (no RUN_FINISHED sent)\n")
        return
