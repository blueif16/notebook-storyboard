"""Storybook Graph - Linear: orchestrator → story_generator → end"""
from typing import Annotated, Optional, List, Dict, Any
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

from ..agents import create_orchestrator_agent, create_story_generator_agent


class StorybookState(TypedDict):
    """Minimal state - everything in messages, derived fields for UI."""
    messages: Annotated[list, add_messages]
    characters: list[dict]
    pages: list[dict]
    stage: str
    progress: float
    storybook_id: Optional[str]
    title: Optional[str]


def create_initial_state(user_message: str) -> StorybookState:
    return StorybookState(
        messages=[{"role": "user", "content": user_message}],
        characters=[],
        pages=[],
        stage="idle",
        progress=0,
        storybook_id=None,
        title=None,
    )


def extract_characters_from_messages(messages: list) -> list[dict]:
    """Extract character data from tool results."""
    characters = []
    for msg in messages:
        if hasattr(msg, "type") and msg.type == "tool":
            if hasattr(msg, "name") and msg.name == "generate_character_portrait":
                if hasattr(msg, "content"):
                    import json
                    try:
                        result = json.loads(msg.content) if isinstance(msg.content, str) else msg.content
                        characters.append(result)
                    except:
                        pass
    return characters


def extract_pages_from_messages(messages: list) -> list[dict]:
    """Extract page data from tool results."""
    pages = []
    page_number = 1
    for msg in messages:
        if hasattr(msg, "type") and msg.type == "tool":
            if hasattr(msg, "name") and msg.name == "generate_page_image":
                if hasattr(msg, "content"):
                    import json
                    try:
                        result = json.loads(msg.content) if isinstance(msg.content, str) else msg.content
                        pages.append({"page_number": page_number, **result})
                        page_number += 1
                    except:
                        pass
    return pages


def orchestrator_node(state: StorybookState) -> dict:
    """Execute orchestrator agent."""
    agent = create_orchestrator_agent()
    result = agent.invoke({"messages": state["messages"]})
    
    characters = extract_characters_from_messages(result["messages"])
    
    return {
        "messages": result["messages"],
        "characters": characters,
        "stage": "characters_generated",
        "progress": 40,
    }


def story_generator_node(state: StorybookState) -> dict:
    """Execute story generator agent."""
    agent = create_story_generator_agent()
    
    last_message = state["messages"][-1].content
    result = agent.invoke({"messages": [{"role": "user", "content": last_message}]})
    
    pages = extract_pages_from_messages(result["messages"])
    
    storybook_id = None
    title = None
    for msg in result["messages"]:
        if hasattr(msg, "type") and msg.type == "tool":
            if hasattr(msg, "name") and msg.name == "save_storybook":
                if hasattr(msg, "content"):
                    import json
                    try:
                        save_result = json.loads(msg.content) if isinstance(msg.content, str) else msg.content
                        storybook_id = save_result.get("storybook_id")
                    except:
                        pass
    
    return {
        "messages": result["messages"],
        "pages": pages,
        "stage": "complete",
        "progress": 100,
        "storybook_id": storybook_id,
        "title": title,
    }


def build_storybook_graph() -> StateGraph:
    """Build graph: START → orchestrator → story_generator → END"""
    builder = StateGraph(StorybookState)
    
    builder.add_node("orchestrator", orchestrator_node)
    builder.add_node("story_generator", story_generator_node)
    
    builder.add_edge(START, "orchestrator")
    builder.add_edge("orchestrator", "story_generator")
    builder.add_edge("story_generator", END)
    
    return builder


def compile_storybook_graph(checkpointer=None):
    """Compile graph with optional checkpointer."""
    builder = build_storybook_graph()
    return builder.compile(checkpointer=checkpointer or MemorySaver())


async def run_storybook_generation(user_input: str, thread_id: Optional[str] = None) -> Dict[str, Any]:
    """Run storybook generation pipeline."""
    import uuid
    
    graph = compile_storybook_graph()
    initial_state = create_initial_state(user_input)
    config = {"configurable": {"thread_id": thread_id or str(uuid.uuid4())}}
    
    result = await graph.ainvoke(initial_state, config=config)
    return result
