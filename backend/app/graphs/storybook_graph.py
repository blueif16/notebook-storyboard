"""Storybook Graph - V2 with Subgraph Pattern for Context Isolation

Each stage is a SUBGRAPH with:
1. Private message context
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
    """
    路由到指定阶段。

    Args:
        stage: 目标阶段
        reason: 为什么路由到这个阶段（你的分析和指令）

    Returns:
        确认消息
    """
    return f"Routing to {stage}: {reason}"


class StorybookState(TypedDict):
    """Parent state - holds only outputs, minimal routing messages."""
    messages: Annotated[list, add_messages]  # Only routing messages

    # Core outputs
    enhanced_story: Optional[str]
    characters: list[dict]  # [{name, description, image_id?, image_url?}]
    pages: list[dict]       # [{page_number, image_id, image_url}]
    storybook_id: Optional[str]

    # Metadata
    current_stage: Optional[str]
    review_type: Optional[str]  # "story_review" | "character_review" | "pages_review"


# Subgraph private states
class EnhanceState(TypedDict):
    """Private messages for enhance agent."""
    messages: Annotated[list, add_messages]


class PortraitState(TypedDict):
    """Private messages for portrait agent."""
    messages: Annotated[list, add_messages]


class StoryState(TypedDict):
    """Private messages for story agent."""
    messages: Annotated[list, add_messages]


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def extract_from_tool_messages(messages: list, tool_name: str) -> list[dict]:
    """Extract data from tool result messages."""
    results = []
    for msg in messages:
        if hasattr(msg, "type") and msg.type == "tool":
            if hasattr(msg, "name") and msg.name == tool_name:
                import json
                try:
                    result = json.loads(msg.content) if isinstance(msg.content, str) else msg.content
                    results.append(result)
                except:
                    pass
    return results


def extract_user_interaction_data(messages: list) -> Optional[dict]:
    """Extract the data from last user_interaction tool call."""
    for msg in reversed(messages):
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                if tc.get("name") == "user_interaction":
                    return tc.get("args", {}).get("data")
    return None


# =============================================================================
# SUBGRAPH ROUTING
# =============================================================================

def route_enhance_subgraph(state: EnhanceState) -> Literal["agent", "__end__"]:
    """Route within enhance subgraph."""
    messages = state["messages"]

    # Check if escalate was called
    if get_tool_call(messages, "escalate"):
        logger.info("[SUBGRAPH] Enhance escalating - exiting")
        return "__end__"

    # Check if present_enhanced_story was called - story is ready
    if get_tool_call(messages, "present_enhanced_story"):
        logger.info("[SUBGRAPH] Story presented - exiting")
        return "__end__"

    # Check if last message is AI message without tool calls - agent is done
    if messages:
        last_msg = messages[-1]
        if hasattr(last_msg, "type") and last_msg.type == "ai":
            has_tool_calls = hasattr(last_msg, "tool_calls") and last_msg.tool_calls
            if not has_tool_calls:
                logger.info("[SUBGRAPH] Enhance agent finished (no tool calls) - exiting")
                return "__end__"

    # Default: keep working
    return "agent"


def route_portrait_subgraph(state: PortraitState) -> Literal["agent", "__end__"]:
    """Route within portrait subgraph."""
    messages = state["messages"]

    if get_tool_call(messages, "escalate"):
        return "__end__"

    interaction = get_tool_call(messages, "user_interaction")
    if interaction:
        args = interaction.get("args", {})
        if args.get("intention") == "next":
            response = get_tool_result(messages, "user_interaction")
            if response == "APPROVED":
                return "__end__"
            return "agent"

    # Check if last message is AI message without tool calls - agent is done
    if messages:
        last_msg = messages[-1]
        if hasattr(last_msg, "type") and last_msg.type == "ai":
            has_tool_calls = hasattr(last_msg, "tool_calls") and last_msg.tool_calls
            if not has_tool_calls:
                logger.info("[SUBGRAPH] Portrait agent finished (no tool calls) - exiting")
                return "__end__"

    return "agent"


def route_story_subgraph(state: StoryState) -> Literal["agent", "__end__"]:
    """Route within story subgraph."""
    messages = state["messages"]

    if get_tool_call(messages, "escalate"):
        return "__end__"

    interaction = get_tool_call(messages, "user_interaction")
    if interaction:
        args = interaction.get("args", {})
        if args.get("intention") == "next":
            response = get_tool_result(messages, "user_interaction")
            if response == "APPROVED":
                return "__end__"
            return "agent"

    # Check if last message is AI message without tool calls - agent is done
    if messages:
        last_msg = messages[-1]
        if hasattr(last_msg, "type") and last_msg.type == "ai":
            has_tool_calls = hasattr(last_msg, "tool_calls") and last_msg.tool_calls
            if not has_tool_calls:
                logger.info("[SUBGRAPH] Story agent finished (no tool calls) - exiting")
                return "__end__"

    return "agent"


# =============================================================================
# SUBGRAPH BUILDERS
# =============================================================================

def build_enhance_subgraph():
    """Enhance subgraph with internal HITL loop."""

    async def enhance_agent_node(state: EnhanceState) -> dict:
        logger.info("[SUBGRAPH] Enhance agent working...")
        agent = AgentCache.get_agent("enhance")
        result = await agent.ainvoke({"messages": state["messages"]})
        return {"messages": result["messages"]}

    builder = StateGraph(EnhanceState)
    builder.add_node("agent", enhance_agent_node)
    builder.add_edge(START, "agent")

    # Internal loop or exit
    builder.add_conditional_edges(
        "agent",
        route_enhance_subgraph,
        {
            "agent": "agent",  # Continue working
            "__end__": END,     # Done
        }
    )

    return builder.compile()


def build_portrait_subgraph():
    """Portrait subgraph with internal HITL loop."""
    
    async def portrait_agent_node(state: PortraitState) -> dict:
        logger.info("[SUBGRAPH] Portrait agent working...")
        agent = AgentCache.get_agent("portrait")
        result = await agent.ainvoke({"messages": state["messages"]})
        return {"messages": result["messages"]}
    
    builder = StateGraph(PortraitState)
    builder.add_node("agent", portrait_agent_node)
    builder.add_edge(START, "agent")
    
    builder.add_conditional_edges(
        "agent",
        route_portrait_subgraph,
        {
            "agent": "agent",
            "__end__": END,
        }
    )
    
    return builder.compile()


def build_story_subgraph():
    """Story subgraph with internal HITL loop."""
    
    async def story_agent_node(state: StoryState) -> dict:
        logger.info("[SUBGRAPH] Story agent working...")
        agent = AgentCache.get_agent("story")
        result = await agent.ainvoke({"messages": state["messages"]})
        return {"messages": result["messages"]}
    
    builder = StateGraph(StoryState)
    builder.add_node("agent", story_agent_node)
    builder.add_edge(START, "agent")
    
    builder.add_conditional_edges(
        "agent",
        route_story_subgraph,
        {
            "agent": "agent",
            "__end__": END,
        }
    )
    
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
    Orchestrator: 判断用户意图并路由或对话

    - 如果是闲聊 → 生成回复，使用 interrupt，继续循环
    - 如果是创作故事 → 调用 route_to_stage 工具，传递 reason 给下一个阶段
    """
    logger.info("[NODE] orchestrator_node")

    try:
        model = get_gemini_model()

        # 给模型绑定路由工具
        model_with_tools = model.bind_tools([route_to_stage])

        response = await model_with_tools.ainvoke([
            SystemMessage(content="""你是故事书创作助手的协调器。

你的职责：
1. 与用户对话，理解他们的需求
2. 当用户明确想要创作故事时，调用 route_to_stage 工具路由到对应阶段
3. 使用用户的语言对话以及写reason


何时调用 route_to_stage：
- 用户提供故事想法 → route_to_stage(stage="enhance", reason="用户想创作...的故事，我会...")
- 用户要生成角色图片 → route_to_stage(stage="portrait", reason="...")
- 用户要生成故事页面 → route_to_stage(stage="story", reason="...")

何时不调用工具（正常对话）：
- 用户打招呼："hi", "hello"
- 用户问问题："你能做什么？"
- 用户的需求不明确，需要澄清

记住：reason 参数会传递给下一个阶段，所以要写清楚你的理解和计划。"""),
            *state["messages"]
        ])

        # 检查是否有工具调用
        if hasattr(response, "tool_calls") and response.tool_calls:
            # 有工具调用 = 需要路由到某个 stage
            for tc in response.tool_calls:
                if tc.get("name") == "route_to_stage":
                    target_stage = tc["args"]["stage"]
                    reason = tc["args"]["reason"]

                    logger.info(f"[ORCHESTRATOR] Routing to {target_stage}: {reason[:100]}...")

                    # 路由到 stage，传递模型的分析作为第一条消息
                    return Command(
                        goto=target_stage,
                        update={
                            "messages": [AIMessage(content=reason)],
                            "current_stage": "orchestrator"
                        }
                    )

        # 没有工具调用 = 正常对话
        logger.info(f"[ORCHESTRATOR] Chat response: {response.content[:100]}...")

        # 使用 interrupt 等待用户输入
        user_input = interrupt({
            "type": "text",
            "intention": "self",
            "value": response.content
        })

        # 继续循环
        return Command(
            goto="orchestrator",
            update={
                "messages": [response, HumanMessage(content=user_input)],
                "current_stage": "orchestrator"
            }
        )

    except GraphInterrupt:
        # Interrupt must propagate to LangGraph
        logger.info(f"[NODE] orchestrator_node interrupted (expected) - re-raising")
        raise
    except Exception as e:
        logger.error(f"[NODE] orchestrator failed: {e}", exc_info=True)

        # 错误也使用 interrupt 模式
        user_input = interrupt({
            "type": "text",
            "intention": "self",
            "value": f"抱歉，出现错误: {e}"
        })

        return Command(
            goto="orchestrator",
            update={
                "messages": [AIMessage(content=f"抱歉，出现错误: {e}"), HumanMessage(content=user_input)],
                "current_stage": "orchestrator"
            }
        )


async def enhance_node(state: StorybookState) -> Command[Literal["enhance", "portrait", "orchestrator"]]:
    """
    Call enhance subgraph.

    传递 orchestrator 的最后一条消息（包含分析和指令）
    Clean output: enhanced_story + characters

    使用 Command API 控制路由：
    - APPROVED → goto portrait
    - 反馈 → goto enhance (继续修改)
    - 升级 → goto orchestrator
    """
    logger.info("[NODE] enhance_node - invoking subgraph")

    try:
        # 传递 orchestrator 的最后一条消息
        orchestrator_instruction = state["messages"][-1].content if state["messages"] else "Create a story"

        logger.info(f"[NODE] Passing orchestrator instruction: {orchestrator_instruction[:100]}...")

        # Invoke subgraph with orchestrator's instruction
        subgraph = get_enhance_subgraph()
        result = await subgraph.ainvoke({
            "messages": [HumanMessage(content=orchestrator_instruction)]
        })

        # Check if present_enhanced_story tool was called
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
                        logger.info(f"[NODE] Found present_enhanced_story call: {len(enhanced_story or '')} chars, {len(characters)} characters")
                        break
            if story_presented:
                break

        if story_presented and enhanced_story:
            # ⭐ Auto-generate index for each character
            characters_with_index = []
            for idx, char in enumerate(characters):
                char_with_index = char.copy()
                char_with_index["index"] = idx
                characters_with_index.append(char_with_index)

            logger.info(f"[NODE] Added index to {len(characters_with_index)} characters")

            # Story is ready for review - send interrupt and wait for response
            logger.info(f"[NODE] Story ready for review, sending interrupt")
            user_response = interrupt({
                "type": "story_review",
                "intention": "next"
            })

            # ⭐ 关键：检查用户响应并决定路由
            logger.info(f"[NODE] User response: {user_response}")

            if user_response == "APPROVED":
                # 用户批准 → 进入下一个阶段
                logger.info(f"[NODE] APPROVED → routing to portrait")
                return Command(
                    goto="portrait",
                    update={
                        "messages": [AIMessage(content=f"Enhanced story with {len(characters_with_index)} characters")],
                        "enhanced_story": enhanced_story,
                        "characters": characters_with_index,
                        "current_stage": "enhance",
                    }
                )
            else:
                # 用户提供反馈 → 继续当前阶段
                logger.info(f"[NODE] Feedback received → back to enhance")
                return Command(
                    goto="enhance",
                    update={
                        "messages": [
                            AIMessage(content=f"Enhanced story with {len(characters_with_index)} characters"),
                            HumanMessage(content=user_response)
                        ],
                        "enhanced_story": enhanced_story,
                        "characters": characters_with_index,
                        "current_stage": "enhance",
                    }
                )
        else:
            # No story presented - just text conversation
            logger.info(f"[NODE] No story presented, sending text interrupt")
            user_response = interrupt({
                "type": "text",
                "intention": "self"
            })

            # 继续对话
            return Command(
                goto="enhance",
                update={
                    "messages": [HumanMessage(content=user_response)],
                    "current_stage": "enhance",
                }
            )

    except GraphInterrupt:
        # Interrupt must propagate to LangGraph
        logger.info(f"[NODE] enhance_node interrupted (expected) - re-raising")
        raise
    except RuntimeError as e:
        # Other RuntimeErrors are real errors
        logger.error(f"[NODE] enhance_node failed: {e}")
        return Command(
            goto="orchestrator",
            update={
                "messages": [AIMessage(content=f"Error: {e}")],
                "current_stage": "enhance",
            }
        )
    except Exception as e:
        logger.error(f"[NODE] enhance_node failed: {e}")
        return Command(
            goto="orchestrator",
            update={
                "messages": [AIMessage(content=f"Error: {e}")],
                "current_stage": "enhance",
            }
        )


async def portrait_node(state: StorybookState) -> Command[Literal["portrait", "story", "orchestrator"]]:
    """
    Call portrait subgraph.

    Clean input: enhanced_story + characters
    Clean output: characters with image_id, image_url
    """
    logger.info("[NODE] portrait_node - invoking subgraph")

    try:
        # Build minimal input
        context = f"""Enhanced Story:
{state.get('enhanced_story', '')}

Characters to create portraits for:
{state.get('characters', [])}

Generate portrait image for each character."""

        # Invoke subgraph
        subgraph = get_portrait_subgraph()
        result = await subgraph.ainvoke({
            "messages": [HumanMessage(content=context)]
        })

        # Check if any generate_character_portrait tool SUCCEEDED (has image_id in result)
        portrait_results = extract_from_tool_messages(result["messages"], "generate_character_portrait")
        portraits_generated = any(r.get("image_id") for r in portrait_results)
        
        logger.info(f"[NODE] Portrait results: {len(portrait_results)} calls, success={portraits_generated}")

        if portraits_generated:
            # Portraits generated - send interrupt for review
            logger.info(f"[NODE] Portraits generated, sending interrupt for review")
            user_response = interrupt({
                "type": "character_review",
                "intention": "next"
            })

            logger.info(f"[NODE] User response: {user_response}")

            if user_response == "APPROVED":
                # User approved → go to story stage
                logger.info(f"[NODE] APPROVED → routing to story")
                return Command(
                    goto="story",
                    update={
                        "messages": [AIMessage(content=f"Character portraits complete")],
                        "current_stage": "portrait",
                    }
                )
            else:
                # User provided feedback → continue portrait stage
                logger.info(f"[NODE] Feedback received → back to portrait")
                return Command(
                    goto="portrait",
                    update={
                        "messages": [
                            AIMessage(content=f"Character portraits generated"),
                            HumanMessage(content=user_response)
                        ],
                        "current_stage": "portrait",
                    }
                )
        else:
            # No portraits generated - just text conversation
            logger.info(f"[NODE] No portraits generated, sending text interrupt")
            user_response = interrupt({
                "type": "text",
                "intention": "self"
            })

            # Continue conversation
            return Command(
                goto="portrait",
                update={
                    "messages": [HumanMessage(content=user_response)],
                    "current_stage": "portrait",
                }
            )

    except GraphInterrupt:
        # Interrupt must propagate to LangGraph
        logger.info(f"[NODE] portrait_node interrupted (expected) - re-raising")
        raise
    except RuntimeError as e:
        logger.error(f"[NODE] portrait_node failed: {e}")
        return Command(
            goto="orchestrator",
            update={
                "messages": [AIMessage(content=f"Error: {e}")],
                "current_stage": "portrait",
            }
        )
    except Exception as e:
        logger.error(f"[NODE] portrait_node failed: {e}")
        return Command(
            goto="orchestrator",
            update={
                "messages": [AIMessage(content=f"Error: {e}")],
                "current_stage": "portrait",
            }
        )


async def story_node(state: StorybookState) -> dict:
    """
    Call story subgraph.

    Clean input: enhanced_story + characters with image_ids
    Clean output: pages + storybook_id
    """
    logger.info("[NODE] story_node - invoking subgraph")

    try:
        # Build minimal input
        context = f"""Enhanced Story:
{state.get('enhanced_story', '')}

Characters (use image_ids for visual consistency):
{state.get('characters', [])}

Create 6-12 storybook pages and save the storybook."""

        # Invoke subgraph
        subgraph = get_story_subgraph()
        result = await subgraph.ainvoke({
            "messages": [HumanMessage(content=context)]
        })

        # Extract pages and storybook_id
        pages = extract_from_tool_messages(
            result["messages"],
            "generate_page_image"
        )

        storybook_id = None
        saves = extract_from_tool_messages(
            result["messages"],
            "save_storybook"
        )
        if saves:
            storybook_id = saves[0].get("storybook_id")

        logger.info(f"[NODE] Story complete: {len(pages)} pages, ID={storybook_id}")

        return {
            "messages": [AIMessage(content=f"Storybook created: {len(pages)} pages")],
            "pages": pages,
            "storybook_id": storybook_id,
            "current_stage": "story",
        }

    except GraphInterrupt:
        # Interrupt must propagate to LangGraph
        logger.info(f"[NODE] story_node interrupted (expected) - re-raising")
        raise
    except RuntimeError as e:
        logger.error(f"[NODE] story_node failed: {e}")
        return {
            "messages": [AIMessage(content=f"Error: {e}")],
            "current_stage": "story",
        }
    except Exception as e:
        logger.error(f"[NODE] story_node failed: {e}")
        return {
            "messages": [AIMessage(content=f"Error: {e}")],
            "current_stage": "story",
        }


# =============================================================================
# PARENT GRAPH ROUTING
# =============================================================================

def route_after_stage(state: StorybookState, current_stage: str) -> str:
    """
    Route after stage completion.
    
    Check if escalate was called or if we should progress.
    """
    messages = state["messages"]
    
    # Check for escalation
    if get_tool_call(messages, "escalate"):
        logger.info(f"[ROUTE] {current_stage} escalated → orchestrator")
        return "orchestrator"
    
    # Check if stage completed successfully (has output)
    stage_completed = False
    
    if current_stage == "enhance" and state.get("enhanced_story"):
        stage_completed = True
    elif current_stage == "portrait" and state.get("characters"):
        stage_completed = True
    elif current_stage == "story" and state.get("storybook_id"):
        stage_completed = True
    
    if stage_completed:
        next_stage = NEXT_STAGE[current_stage]
        logger.info(f"[ROUTE] {current_stage} complete → {next_stage}")
        return next_stage
    
    # Default: back to self
    logger.info(f"[ROUTE] {current_stage} → back to self")
    return current_stage


# =============================================================================
# PARENT GRAPH BUILDER
# =============================================================================

def build_storybook_graph() -> StateGraph:
    """Build parent graph with subgraph calls."""
    builder = StateGraph(StorybookState)
    
    # Add nodes
    builder.add_node("orchestrator", orchestrator_node)
    builder.add_node("enhance", enhance_node)
    builder.add_node("portrait", portrait_node)
    builder.add_node("story", story_node)
    
    # Edges
    builder.add_edge(START, "orchestrator")

    # orchestrator, enhance, portrait all use Command API - no conditional edges needed
    # Command return value automatically routes to specified node
    
    # Only story uses conditional edges (returns dict, not Command)
    builder.add_conditional_edges(
        "story",
        lambda s: route_after_stage(s, "story"),
        {
            "story": "story",
            "orchestrator": "orchestrator",
        }
    )
    
    return builder


def compile_storybook_graph(checkpointer=None):
    """Compile graph with checkpointer."""
    builder = build_storybook_graph()
    return builder.compile(checkpointer=checkpointer or MemorySaver())


# =============================================================================
# GRAPH SINGLETON
# =============================================================================

_graph_instance = None

def get_graph():
    """
    Get or create the singleton graph instance with persistent checkpointer.

    This ensures:
    1. Checkpointer persists across requests
    2. Thread state is maintained between conversations
    3. Memory is reused efficiently
    """
    global _graph_instance
    if _graph_instance is None:
        logger.info("[GRAPH] Creating singleton graph instance with MemorySaver")
        _graph_instance = compile_storybook_graph(checkpointer=MemorySaver())
    return _graph_instance




async def run_storybook_generation(user_input: str, thread_id: Optional[str] = None) -> dict:
    """
    Run the complete storybook generation pipeline.

    Args:
        user_input: User's story idea or request
        thread_id: Optional thread ID for conversation continuity

    Returns:
        Final state dict with storybook_id, characters, pages, etc.
    """
    logger.info(f"[PIPELINE] Starting storybook generation: {user_input[:100]}...")

    # Get singleton graph instance
    graph = get_graph()

    # Config with thread_id
    config = {"configurable": {"thread_id": thread_id or "default"}}

    try:
        # Pass only new message - LangGraph will restore state from checkpointer
        final_state = await graph.ainvoke(
            {"messages": [{"role": "user", "content": user_input}]},
            config
        )
        logger.info(f"[PIPELINE] Complete: storybook_id={final_state.get('storybook_id')}")
        return final_state
    except Exception as e:
        logger.error(f"[PIPELINE] Failed: {e}")
        raise
