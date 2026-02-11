"""Storybook Graph - V2 with Subgraph Pattern for Context Isolation

Each stage is a SUBGRAPH with:
1. Private message context (persisted in parent state)
2. Internal HITL loop
3. Clean output when complete

Pattern from LangGraph Guide Section 6: Subgraph Composition
"""
from typing import Annotated, Optional, Literal
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command, interrupt
from langgraph.errors import GraphInterrupt
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
import logging
from operator import add as list_add  # For append-only reducer

from .routing import get_tool_call, get_tool_result, NEXT_STAGE
from ..agents import AgentCache, get_gemini_model

logger = logging.getLogger(__name__)


# =============================================================================
# STATE SCHEMAS
# =============================================================================

@tool
def route_to_stage(
    stage: Literal["enhance", "portrait", "story"],
    reason: str
) -> str:
    """Route to specified stage."""
    return f"Routing to {stage}: {reason}"


def last_value(a, b):
    """Reducer that keeps the last value (allows multiple updates per step)."""
    return b


class StorybookState(TypedDict):
    """Parent state - holds outputs and per-stage conversation histories."""
    messages: Annotated[list, add_messages]  # Routing messages only

    # Core outputs - use last_value reducer to allow updates from both
    # Command(update=...) and node returns in the same step
    enhanced_story: Annotated[Optional[str], last_value]
    characters: Annotated[list, last_value]  # [{name, description, image_id?, image_url?}]
    pages: Annotated[list, list_add]         # [{page_number, image_id, image_url}] - APPEND reducer
    storybook_id: Annotated[Optional[str], last_value]

    # Metadata
    current_stage: Annotated[Optional[str], last_value]
    review_type: Annotated[Optional[str], last_value]  # "story_review" | "character_review" | "pages_review"
    
    # Per-stage conversation histories (isolated contexts)
    # Each stage has its own conversation that persists across text interrupts
    enhance_conversation: Annotated[list, last_value]  # Enhance stage conversation
    portrait_conversation: Annotated[list, last_value]  # Portrait stage conversation  
    story_conversation: Annotated[list, last_value]    # Story stage conversation


# Subgraph private states (used within subgraph execution only)
class EnhanceState(TypedDict):
    messages: Annotated[list, add_messages]


class PortraitState(TypedDict):
    messages: Annotated[list, add_messages]


class StoryState(TypedDict):
    messages: Annotated[list, add_messages]


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def extract_from_tool_messages(messages: list, tool_name: str) -> list[dict]:
    """Extract data from tool result messages."""
    import json
    results = []
    for msg in messages:
        if hasattr(msg, "type") and msg.type == "tool":
            if hasattr(msg, "name") and msg.name == tool_name:
                try:
                    result = json.loads(msg.content) if isinstance(msg.content, str) else msg.content
                    results.append(result)
                except:
                    pass
    return results


def format_messages_for_log(messages: list, max_chars: int = 80) -> str:
    """Format messages for readable logging."""
    lines = []
    for i, msg in enumerate(messages):
        msg_type = getattr(msg, "type", "unknown")
        content = str(getattr(msg, "content", ""))[:max_chars]
        lines.append(f"  [{i}] {msg_type}: {content}...")
    return "\n".join(lines) if lines else "  (empty)"


# =============================================================================
# SUBGRAPH ROUTING
# =============================================================================

def route_enhance_subgraph(state: EnhanceState) -> Literal["agent", "__end__"]:
    """Route within enhance subgraph."""
    messages = state["messages"]

    if get_tool_call(messages, "escalate"):
        logger.info("[ENHANCE SUBGRAPH] Escalate → exit")
        return "__end__"

    if get_tool_call(messages, "present_enhanced_story"):
        logger.info("[ENHANCE SUBGRAPH] Story presented → exit")
        return "__end__"

    if messages:
        last_msg = messages[-1]
        if hasattr(last_msg, "type") and last_msg.type == "ai":
            if not (hasattr(last_msg, "tool_calls") and last_msg.tool_calls):
                logger.info("[ENHANCE SUBGRAPH] AI finished (no tool calls) → exit")
                return "__end__"

    return "agent"


def route_portrait_subgraph(state: PortraitState) -> Literal["agent", "__end__"]:
    """Route within portrait subgraph."""
    messages = state["messages"]

    if get_tool_call(messages, "escalate"):
        logger.info("[PORTRAIT SUBGRAPH] Escalate → exit")
        return "__end__"

    if messages:
        last_msg = messages[-1]
        if hasattr(last_msg, "type") and last_msg.type == "ai":
            if not (hasattr(last_msg, "tool_calls") and last_msg.tool_calls):
                logger.info("[PORTRAIT SUBGRAPH] AI finished (no tool calls) → exit")
                return "__end__"

    return "agent"


def route_story_subgraph(state: StoryState) -> Literal["agent", "__end__"]:
    """Route within story subgraph."""
    messages = state["messages"]

    if get_tool_call(messages, "escalate"):
        logger.info("[STORY SUBGRAPH] Escalate → exit")
        return "__end__"

    if messages:
        last_msg = messages[-1]
        if hasattr(last_msg, "type") and last_msg.type == "ai":
            if not (hasattr(last_msg, "tool_calls") and last_msg.tool_calls):
                logger.info("[STORY SUBGRAPH] AI finished (no tool calls) → exit")
                return "__end__"

    return "agent"


# =============================================================================
# SUBGRAPH BUILDERS
# =============================================================================

def build_enhance_subgraph():
    async def enhance_agent_node(state: EnhanceState) -> dict:
        logger.info("[ENHANCE AGENT] Processing...")
        agent = AgentCache.get_agent("enhance")
        result = await agent.ainvoke({"messages": state["messages"]})
        return {"messages": result["messages"]}

    builder = StateGraph(EnhanceState)
    builder.add_node("agent", enhance_agent_node)
    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", route_enhance_subgraph, {"agent": "agent", "__end__": END})
    return builder.compile()


def build_portrait_subgraph():
    async def portrait_agent_node(state: PortraitState) -> dict:
        logger.info("[PORTRAIT AGENT] Processing...")
        agent = AgentCache.get_agent("portrait")
        result = await agent.ainvoke({"messages": state["messages"]})
        return {"messages": result["messages"]}
    
    builder = StateGraph(PortraitState)
    builder.add_node("agent", portrait_agent_node)
    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", route_portrait_subgraph, {"agent": "agent", "__end__": END})
    return builder.compile()


def build_story_subgraph():
    async def story_agent_node(state: StoryState) -> dict:
        logger.info("[STORY AGENT] Processing...")
        agent = AgentCache.get_agent("story")
        result = await agent.ainvoke({"messages": state["messages"]})
        return {"messages": result["messages"]}
    
    builder = StateGraph(StoryState)
    builder.add_node("agent", story_agent_node)
    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", route_story_subgraph, {"agent": "agent", "__end__": END})
    return builder.compile()


# Cache subgraphs
_enhance_subgraph = None
_portrait_subgraph = None
_story_subgraph = None

def get_enhance_subgraph():
    global _enhance_subgraph
    if _enhance_subgraph is None:
        _enhance_subgraph = build_enhance_subgraph()
    return _enhance_subgraph

def get_portrait_subgraph():
    global _portrait_subgraph
    if _portrait_subgraph is None:
        _portrait_subgraph = build_portrait_subgraph()
    return _portrait_subgraph

def get_story_subgraph():
    global _story_subgraph
    if _story_subgraph is None:
        _story_subgraph = build_story_subgraph()
    return _story_subgraph


# =============================================================================
# PARENT GRAPH NODES
# =============================================================================

async def orchestrator_node(state: StorybookState) -> Command[Literal["enhance", "portrait", "story", "orchestrator"]]:
    """
    Orchestrator: Route to stages or chat with user.
    
    Pattern: interrupt FIRST if last msg is AI (waiting for user input),
    THEN model call. This prevents duplicate model calls on resume.
    """
    logger.info("\n" + "="*60)
    logger.info("[ORCHESTRATOR] Invoked")

    try:
        messages = list(state["messages"])
        
        # If last message is AI, we already responded - get user input FIRST
        # This prevents duplicate model calls on interrupt resume
        if messages and hasattr(messages[-1], "type") and messages[-1].type == "ai":
            logger.info("[ORCHESTRATOR] Last msg is AI - interrupt for user input first")
            user_input = interrupt({"type": "text", "intention": "self"})
            messages.append(HumanMessage(content=user_input))
            logger.info(f"[ORCHESTRATOR] Got user input: {user_input[:60]}...")

        # NOW invoke model (only runs once per user message)
        model = get_gemini_model()
        model_with_tools = model.bind_tools([route_to_stage])

        response = await model_with_tools.ainvoke([
            SystemMessage(content="""你是故事书创作助手的协调器。

职责：
1. 与用户对话，理解需求
2. 当用户想创作故事时，调用 route_to_stage 工具

何时调用 route_to_stage：
- 用户提供故事想法 → route_to_stage(stage="enhance", reason="...")
- 用户要生成角色图片 → route_to_stage(stage="portrait", reason="...")
- 用户要生成故事页面 → route_to_stage(stage="story", reason="...")

何时不调用工具：
- 打招呼、问问题、需求不明确

使用用户的语言对话。"""),
            *messages
        ])

        # Check for tool calls
        if hasattr(response, "tool_calls") and response.tool_calls:
            for tc in response.tool_calls:
                if tc.get("name") == "route_to_stage":
                    target_stage = tc["args"]["stage"]
                    reason = tc["args"]["reason"]
                    logger.info(f"[ORCHESTRATOR] Routing to '{target_stage}'")

                    # Clear target stage's conversation on fresh entry
                    update = {
                        "messages": [response, AIMessage(content=reason)],
                        "current_stage": "orchestrator",
                    }
                    # Reset the target stage's conversation
                    if target_stage == "enhance":
                        update["enhance_conversation"] = []
                    elif target_stage == "portrait":
                        update["portrait_conversation"] = []
                    elif target_stage == "story":
                        update["story_conversation"] = []

                    return Command(goto=target_stage, update=update)

        # No tool calls = chat response, loop back
        logger.info(f"[ORCHESTRATOR] Chat response")
        return Command(
            goto="orchestrator",
            update={
                "messages": [response],
                "current_stage": "orchestrator"
            }
        )

    except GraphInterrupt:
        logger.info(f"[ORCHESTRATOR] Interrupted")
        raise
    except Exception as e:
        logger.error(f"[ORCHESTRATOR] Error: {e}", exc_info=True)
        return Command(
            goto="orchestrator",
            update={
                "messages": [AIMessage(content=f"Error: {e}")],
                "current_stage": "orchestrator"
            }
        )


async def enhance_node(state: StorybookState) -> Command[Literal["enhance", "portrait", "orchestrator"]]:
    """
    Enhance stage: Enhance story and extract characters.
    
    Pattern: 
    - Text interrupt BEFORE subgraph (for conversational feedback)
    - Story review interrupt AFTER subgraph (for approval)
    - Check for pending review to skip subgraph on APPROVED resume
    """
    logger.info("\n" + "="*60)
    logger.info("[ENHANCE NODE] Invoked")

    try:
        enhance_conversation = list(state.get("enhance_conversation") or [])
        existing_messages = state.get("messages", [])
        
        logger.info(f"[ENHANCE NODE] Conversation history: {len(enhance_conversation)} messages")

        # Check if we have a pending story review (resuming from story_review interrupt)
        # If enhanced_story exists in state + review_type is story_review, we're resuming
        pending_story = state.get("enhanced_story")
        pending_characters = state.get("characters", [])
        pending_review = state.get("review_type") == "story_review"
        
        if pending_story and pending_characters and pending_review:
            # Resuming from story_review interrupt - skip subgraph, go straight to interrupt
            logger.info(f"[ENHANCE NODE] Resuming from story_review - skipping subgraph")
            logger.info(f"[ENHANCE NODE]   pending_story: {len(pending_story)} chars")
            logger.info(f"[ENHANCE NODE]   pending_characters: {len(pending_characters)} items")
            
            user_response = interrupt({
                "type": "story_review", 
                "intention": "next",
                "data": {
                    "enhanced_story": pending_story,
                    "characters": pending_characters
                }
            })
            logger.info(f"[ENHANCE NODE] User response: {user_response}")

            if user_response == "APPROVED":
                logger.info(f"[ENHANCE NODE] APPROVED → portrait")
                return Command(
                    goto="portrait",
                    update={
                        "current_stage": "enhance",
                        "review_type": None,  # Clear review flag
                    }
                )
            else:
                # Feedback - clear pending state and re-run with feedback
                logger.info(f"[ENHANCE NODE] Feedback → enhance (loop)")
                return Command(
                    goto="enhance",
                    update={
                        "current_stage": "enhance",
                        "review_type": None,  # Clear review flag
                        "enhance_conversation": enhance_conversation + [HumanMessage(content=user_response)],
                    }
                )

        # TEXT INTERRUPT - before subgraph (for conversational feedback)
        if enhance_conversation and hasattr(enhance_conversation[-1], "type") and enhance_conversation[-1].type == "ai":
            logger.info("[ENHANCE NODE] Last msg is AI - interrupt for user input first")
            user_input = interrupt({"type": "text", "intention": "self"})
            enhance_conversation.append(HumanMessage(content=user_input))
            logger.info(f"[ENHANCE NODE] Got user input: {user_input[:60]}...")

        # Build subgraph messages
        if not enhance_conversation:
            # First entry - use orchestrator's reason as initial context
            initial_context = existing_messages[-1].content if existing_messages else "Create a story"
            subgraph_messages = [HumanMessage(content=initial_context)]
            logger.info(f"[ENHANCE NODE] First entry with context: {initial_context[:60]}...")
        else:
            subgraph_messages = enhance_conversation.copy()
            logger.info(f"[ENHANCE NODE] Continuation with {len(subgraph_messages)} messages")

        # Invoke subgraph
        subgraph = get_enhance_subgraph()
        result = await subgraph.ainvoke({"messages": subgraph_messages})
        new_conversation = result["messages"]
        logger.info(f"[ENHANCE NODE] Subgraph returned {len(new_conversation)} messages")

        # Check for present_enhanced_story tool call
        enhanced_story = None
        characters = []
        story_presented = False

        for msg in result["messages"]:
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                for tc in msg.tool_calls:
                    if tc.get("name") == "present_enhanced_story":
                        story_presented = True
                        args = tc.get("args", {})
                        enhanced_story = args.get("enhanced_story")
                        characters = args.get("characters", [])
                        break
            if story_presented:
                break

        if story_presented and enhanced_story:
            # Add index to each character
            characters_with_index = [{**char, "index": idx} for idx, char in enumerate(characters)]
            logger.info(f"[ENHANCE NODE] Story presented: {len(enhanced_story)} chars, {len(characters_with_index)} characters")

            # STORY REVIEW INTERRUPT - after subgraph
            # First, save results to state so they persist across interrupt
            # Then interrupt for review
            user_response = interrupt({
                "type": "story_review", 
                "intention": "next",
                "data": {
                    "enhanced_story": enhanced_story,
                    "characters": characters_with_index
                }
            })
            logger.info(f"[ENHANCE NODE] User response: {user_response}")

            if user_response == "APPROVED":
                # APPROVED → go to portrait stage
                logger.info(f"[ENHANCE NODE] APPROVED → portrait")
                return Command(
                    goto="portrait",
                    update={
                        "enhanced_story": enhanced_story,
                        "characters": characters_with_index,
                        "current_stage": "enhance",
                        "enhance_conversation": new_conversation,
                        "review_type": None,
                    }
                )
            else:
                # Feedback → loop back to enhance with user feedback
                logger.info(f"[ENHANCE NODE] Feedback → enhance (loop)")
                return Command(
                    goto="enhance",
                    update={
                        "enhanced_story": enhanced_story,
                        "characters": characters_with_index,
                        "current_stage": "enhance",
                        "enhance_conversation": new_conversation + [HumanMessage(content=user_response)],
                        "review_type": None,
                    }
                )
        else:
            # No story yet - just loop back, next invocation will interrupt if needed
            logger.info(f"[ENHANCE NODE] No story yet, loop back")
            return Command(
                goto="enhance",
                update={
                    "current_stage": "enhance",
                    "enhance_conversation": new_conversation,
                }
            )

    except GraphInterrupt:
        logger.info(f"[ENHANCE NODE] Interrupted")
        raise
    except Exception as e:
        logger.error(f"[ENHANCE NODE] Error: {e}", exc_info=True)
        return Command(
            goto="orchestrator",
            update={"messages": [AIMessage(content=f"Error: {e}")], "current_stage": "enhance"}
        )


async def portrait_node(state: StorybookState) -> Command[Literal["portrait", "story", "orchestrator"]]:
    """
    Portrait stage: Generate character portraits.
    
    Pattern:
    - Text interrupt BEFORE subgraph (for conversational feedback)
    - Character review interrupt AFTER subgraph (for approval)
    - Check for pending review to skip subgraph on APPROVED resume
    """
    logger.info("\n" + "="*60)
    logger.info("[PORTRAIT NODE] Invoked")

    try:
        portrait_conversation = list(state.get("portrait_conversation") or [])
        existing_messages = state.get("messages", [])
        
        logger.info(f"[PORTRAIT NODE] Conversation history: {len(portrait_conversation)} messages")

        # Check if we have a pending character review (resuming from character_review interrupt)
        pending_characters = state.get("characters", [])
        pending_review = state.get("review_type") == "character_review"
        has_images = any(c.get("image_id") for c in pending_characters)
        
        if pending_characters and has_images and pending_review:
            # Resuming from character_review interrupt - skip subgraph
            logger.info(f"[PORTRAIT NODE] Resuming from character_review - skipping subgraph")
            logger.info(f"[PORTRAIT NODE]   pending_characters: {len(pending_characters)} items")
            
            user_response = interrupt({
                "type": "character_review", 
                "intention": "next",
                "data": {
                    "characters": pending_characters
                }
            })
            logger.info(f"[PORTRAIT NODE] User response: {user_response}")

            if user_response == "APPROVED":
                logger.info(f"[PORTRAIT NODE] APPROVED → story")
                return Command(
                    goto="story",
                    update={
                        "current_stage": "portrait",
                        "review_type": None,
                    }
                )
            else:
                logger.info(f"[PORTRAIT NODE] Feedback → portrait (loop)")
                return Command(
                    goto="portrait",
                    update={
                        "current_stage": "portrait",
                        "review_type": None,
                        "portrait_conversation": portrait_conversation + [HumanMessage(content=user_response)],
                    }
                )

        # TEXT INTERRUPT - before subgraph (for conversational feedback)
        if portrait_conversation and hasattr(portrait_conversation[-1], "type") and portrait_conversation[-1].type == "ai":
            logger.info("[PORTRAIT NODE] Last msg is AI - interrupt for user input first")
            user_input = interrupt({"type": "text", "intention": "self"})
            portrait_conversation.append(HumanMessage(content=user_input))
            logger.info(f"[PORTRAIT NODE] Got user input: {user_input[:60]}...")

        # Build subgraph messages
        if not portrait_conversation:
            # First entry - build context from state
            context = f"""Enhanced Story:
{state.get('enhanced_story', '')}

Characters to create portraits for:
{state.get('characters', [])}

Generate portrait image for each character."""
            subgraph_messages = [HumanMessage(content=context)]
            logger.info(f"[PORTRAIT NODE] First entry with {len(state.get('characters', []))} characters")
        else:
            subgraph_messages = portrait_conversation.copy()
            logger.info(f"[PORTRAIT NODE] Continuation with {len(subgraph_messages)} messages")

        # Invoke subgraph
        subgraph = get_portrait_subgraph()
        result = await subgraph.ainvoke({"messages": subgraph_messages})
        new_conversation = result["messages"]
        logger.info(f"[PORTRAIT NODE] Subgraph returned {len(new_conversation)} messages")

        # Check for portrait generation results
        portrait_results = extract_from_tool_messages(result["messages"], "generate_character_portrait")
        portraits_generated = any(r.get("image_id") for r in portrait_results)
        logger.info(f"[PORTRAIT NODE] Results: {len(portrait_results)} calls, success={portraits_generated}")

        # Merge portrait results into characters
        updated_characters = [char.copy() for char in state.get("characters", [])]
        for portrait in portrait_results:
            idx = portrait.get("index", 0)
            if idx < len(updated_characters) and portrait.get("image_id"):
                updated_characters[idx]["image_id"] = portrait.get("image_id")
                updated_characters[idx]["image_url"] = portrait.get("image_url")

        if portraits_generated:
            # Portraits ready - interrupt for review
            user_response = interrupt({
                "type": "character_review", 
                "intention": "next",
                "data": {
                    "characters": updated_characters
                }
            })
            logger.info(f"[PORTRAIT NODE] User response: {user_response}")

            if user_response == "APPROVED":
                # APPROVED → go to story stage
                logger.info(f"[PORTRAIT NODE] APPROVED → story")
                return Command(
                    goto="story",
                    update={
                        "characters": updated_characters,
                        "current_stage": "portrait",
                        "portrait_conversation": new_conversation,
                        "review_type": None,
                    }
                )
            else:
                # Feedback → loop back to portrait with user feedback
                logger.info(f"[PORTRAIT NODE] Feedback → portrait (loop)")
                return Command(
                    goto="portrait",
                    update={
                        "characters": updated_characters,
                        "current_stage": "portrait",
                        "portrait_conversation": new_conversation + [HumanMessage(content=user_response)],
                        "review_type": None,
                    }
                )
        else:
            # No portraits yet - just loop back, next invocation will interrupt if needed
            logger.info(f"[PORTRAIT NODE] No portraits yet, loop back")
            return Command(
                goto="portrait",
                update={
                    "current_stage": "portrait",
                    "portrait_conversation": new_conversation,
                }
            )

    except GraphInterrupt:
        logger.info(f"[PORTRAIT NODE] Interrupted")
        raise
    except Exception as e:
        logger.error(f"[PORTRAIT NODE] Error: {e}", exc_info=True)
        return Command(
            goto="orchestrator",
            update={"messages": [AIMessage(content=f"Error: {e}")], "current_stage": "portrait"}
        )


async def story_node(state: StorybookState) -> Command[Literal["story", "orchestrator"]]:
    """
    Story stage: Generate page illustrations.
    
    Pattern:
    - Text interrupt BEFORE subgraph (for conversational feedback)
    - Pages review interrupt AFTER subgraph (for approval)
    - Check for pending review to skip subgraph on APPROVED resume
    """
    logger.info("\n" + "="*60)
    logger.info("[STORY NODE] Invoked")

    try:
        story_conversation = list(state.get("story_conversation") or [])
        existing_messages = state.get("messages", [])
        
        logger.info(f"[STORY NODE] Conversation history: {len(story_conversation)} messages")

        # Check if we have a pending pages review (resuming from pages_review interrupt)
        pending_pages = state.get("pages", [])
        pending_review = state.get("review_type") == "pages_review"
        
        if pending_pages and pending_review:
            # Resuming from pages_review interrupt - skip subgraph
            logger.info(f"[STORY NODE] Resuming from pages_review - skipping subgraph")
            logger.info(f"[STORY NODE]   pending_pages: {len(pending_pages)} items")
            
            user_response = interrupt({
                "type": "pages_review", 
                "intention": "next",
                "data": {
                    "pages": pending_pages
                }
            })
            logger.info(f"[STORY NODE] User response: {user_response}")

            if user_response == "APPROVED":
                logger.info("[STORY NODE] APPROVED → orchestrator")
                return Command(
                    goto="orchestrator",
                    update={
                        "current_stage": "story",
                        "review_type": None,
                        "messages": [AIMessage(content="Story pages completed!")],
                    }
                )
            else:
                logger.info("[STORY NODE] Feedback → story (loop)")
                return Command(
                    goto="story",
                    update={
                        "current_stage": "story",
                        "review_type": None,
                        "story_conversation": story_conversation + [HumanMessage(content=user_response)],
                    }
                )

        # TEXT INTERRUPT - before subgraph (for conversational feedback)
        if story_conversation and hasattr(story_conversation[-1], "type") and story_conversation[-1].type == "ai":
            logger.info("[STORY NODE] Last msg is AI - interrupt for user input first")
            user_input = interrupt({"type": "text", "intention": "self"})
            story_conversation.append(HumanMessage(content=user_input))
            logger.info(f"[STORY NODE] Got user input: {user_input[:60]}...")

        # Build subgraph messages
        if not story_conversation:
            # First entry - build context from state
            context = f"""Enhanced Story:
{state.get('enhanced_story', '')}

Characters (use their image_ids for visual consistency in pages):
{state.get('characters', [])}

Discuss your page plan with the user before generating."""
            subgraph_messages = [HumanMessage(content=context)]
            logger.info(f"[STORY NODE] First entry with context")
        else:
            subgraph_messages = story_conversation.copy()
            logger.info(f"[STORY NODE] Continuation with {len(subgraph_messages)} messages")
            logger.info(f"[STORY NODE] Messages:\n{format_messages_for_log(subgraph_messages)}")

        # Invoke subgraph
        subgraph = get_story_subgraph()
        result = await subgraph.ainvoke({"messages": subgraph_messages})
        new_conversation = result["messages"]
        logger.info(f"[STORY NODE] Subgraph returned {len(new_conversation)} messages")

        # Check for tool calls
        page_tool_called = False
        escalate_tool_called = False
        for msg in result["messages"]:
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                for tc in msg.tool_calls:
                    if tc.get("name") == "generate_page_image":
                        page_tool_called = True
                    elif tc.get("name") == "escalate":
                        escalate_tool_called = True

        if escalate_tool_called:
            logger.info("[STORY NODE] Escalate → orchestrator")
            return Command(
                goto="orchestrator",
                update={
                    "messages": [AIMessage(content="Escalating from story stage")],
                    "current_stage": "story",
                    "story_conversation": new_conversation,
                }
            )

        if page_tool_called:
            # Pages generated - ONLY extract from NEW messages to avoid duplicates
            # The subgraph returns all messages (input + new), so we slice to get only new ones
            messages_before_count = len(subgraph_messages)
            new_messages_only = result["messages"][messages_before_count:]
            new_pages = extract_from_tool_messages(new_messages_only, "generate_page_image")
            
            # Get existing pages for the interrupt review data
            # (reducer hasn't run yet, so we need to manually combine for display)
            existing_pages = state.get("pages", [])
            all_pages_for_review = existing_pages + new_pages
            logger.info(f"[STORY NODE] Pages: {len(new_pages)} new (from {len(new_messages_only)} new msgs), {len(all_pages_for_review)} total")

            # Interrupt for review - show ALL pages (existing + new)
            user_response = interrupt({
                "type": "pages_review", 
                "intention": "next",
                "data": {
                    "pages": all_pages_for_review
                }
            })
            logger.info(f"[STORY NODE] User response: {user_response}")

            if user_response == "APPROVED":
                # APPROVED → go back to orchestrator (story complete)
                # NOTE: Only return new_pages - the list_add reducer will append automatically!
                logger.info("[STORY NODE] APPROVED → orchestrator")
                return Command(
                    goto="orchestrator",
                    update={
                        "pages": new_pages,  # Reducer appends to existing pages
                        "current_stage": "story",
                        "story_conversation": new_conversation,
                        "messages": [AIMessage(content="Story pages completed!")],
                        "review_type": None,
                    }
                )
            else:
                # Feedback → loop back to story with user feedback
                # NOTE: Only return new_pages - the list_add reducer will append automatically!
                logger.info("[STORY NODE] Feedback → story (loop)")
                return Command(
                    goto="story",
                    update={
                        "pages": new_pages,  # Reducer appends to existing pages
                        "current_stage": "story",
                        "story_conversation": new_conversation + [HumanMessage(content=user_response)],
                        "review_type": None,
                    }
                )
        else:
            # No pages yet - just loop back, next invocation will interrupt if needed
            logger.info("[STORY NODE] No pages yet, loop back")
            return Command(
                goto="story",
                update={
                    "current_stage": "story",
                    "story_conversation": new_conversation,
                }
            )

    except GraphInterrupt:
        logger.info(f"[STORY NODE] Interrupted")
        raise
    except Exception as e:
        logger.error(f"[STORY NODE] Error: {e}", exc_info=True)
        return Command(
            goto="orchestrator",
            update={"messages": [AIMessage(content=f"Error: {e}")], "current_stage": "story"}
        )


# =============================================================================
# GRAPH BUILDER
# =============================================================================

def build_storybook_graph() -> StateGraph:
    """Build parent graph with subgraph calls."""
    builder = StateGraph(StorybookState)
    
    builder.add_node("orchestrator", orchestrator_node)
    builder.add_node("enhance", enhance_node)
    builder.add_node("portrait", portrait_node)
    builder.add_node("story", story_node)
    
    builder.add_edge(START, "orchestrator")
    # All routing done via Command API
    
    return builder


def compile_storybook_graph(checkpointer=None):
    builder = build_storybook_graph()
    return builder.compile(checkpointer=checkpointer or MemorySaver())


# =============================================================================
# GRAPH SINGLETON
# =============================================================================

_graph_instance = None

def get_graph():
    """Get singleton graph instance with persistent checkpointer."""
    global _graph_instance
    if _graph_instance is None:
        logger.info("[GRAPH] Creating singleton with MemorySaver")
        _graph_instance = compile_storybook_graph(checkpointer=MemorySaver())
    return _graph_instance


async def run_storybook_generation(user_input: str, thread_id: Optional[str] = None) -> dict:
    """Run the complete storybook generation pipeline."""
    logger.info(f"[PIPELINE] Starting: {user_input[:100]}...")
    graph = get_graph()
    config = {"configurable": {"thread_id": thread_id or "default"}}

    try:
        final_state = await graph.ainvoke(
            {"messages": [{"role": "user", "content": user_input}]},
            config
        )
        logger.info(f"[PIPELINE] Complete: storybook_id={final_state.get('storybook_id')}")
        return final_state
    except Exception as e:
        logger.error(f"[PIPELINE] Failed: {e}")
        raise
