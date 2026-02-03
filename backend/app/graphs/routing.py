"""Routing logic for hierarchical agent system"""
from typing import Optional, Literal
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# STAGE PROGRESSION TABLE
# =============================================================================

NEXT_STAGE = {
    "enhance": "portrait",
    "portrait": "story",
    "story": "orchestrator",  # Returns to orchestrator, never ends
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_tool_call(messages: list, tool_name: str) -> Optional[dict]:
    """
    Extract tool call from last AI message if present.

    Returns:
        Tool call dict with 'name' and 'args', or None
    """
    if not messages:
        logger.debug(f"[ROUTE] No messages to check for tool: {tool_name}")
        return None

    last_msg = messages[-1]
    logger.debug(f"[ROUTE] Checking last message for tool: {tool_name}")
    logger.debug(f"[ROUTE] Last message type: {type(last_msg)}")
    logger.debug(f"[ROUTE] Has tool_calls attr: {hasattr(last_msg, 'tool_calls')}")

    if hasattr(last_msg, "tool_calls"):
        logger.debug(f"[ROUTE] tool_calls value: {last_msg.tool_calls}")
        if last_msg.tool_calls:
            for tc in last_msg.tool_calls:
                logger.debug(f"[ROUTE] Checking tool call: {tc}")
                if tc.get("name") == tool_name:
                    logger.info(f"[ROUTE] ✓ Found tool call: {tool_name} with args: {tc.get('args')}")
                    return tc
            logger.debug(f"[ROUTE] Tool {tool_name} not found in tool_calls")
        else:
            logger.debug(f"[ROUTE] tool_calls is empty list")

    return None


def get_tool_result(messages: list, tool_name: str) -> Optional[str]:
    """
    Get result of most recent tool call from messages.
    
    Returns:
        Tool result content as string, or None
    """
    for msg in reversed(messages):
        if hasattr(msg, "type") and msg.type == "tool":
            if hasattr(msg, "name") and msg.name == tool_name:
                logger.debug(f"[ROUTE] Found tool result: {tool_name}")
                return msg.content
    
    return None


# =============================================================================
# ROUTING FUNCTIONS
# =============================================================================

def route_after_stage(
    state: dict, 
    current_stage: Literal["enhance", "portrait", "story"]
) -> str:
    """
    Routing logic for all stage nodes.
    
    Decision tree:
    1. escalate called → "orchestrator"
    2. user_interaction(intention="next") + "APPROVED" → NEXT_STAGE[current]
    3. otherwise → current_stage (back to self)
    
    Args:
        state: Current graph state
        current_stage: Name of the current stage
        
    Returns:
        Next node name: current_stage, next_stage, or "orchestrator"
    """
    messages = state.get("messages", [])
    logger.info(f"[ROUTE] Evaluating routing from stage: {current_stage}")
    
    # 1. Check for escalation
    if get_tool_call(messages, "escalate"):
        escalate_call = get_tool_call(messages, "escalate")
        reason = escalate_call.get("args", {}).get("reason", "")
        logger.info(f"[ROUTE] Escalation detected: {reason[:100]}")
        return "orchestrator"
    
    # 2. Check for user_interaction with intention="next"
    interaction_call = get_tool_call(messages, "user_interaction")
    if interaction_call:
        args = interaction_call.get("args", {})
        intention = args.get("intention", "self")
        logger.debug(f"[ROUTE] user_interaction called with intention={intention}")
        
        if intention == "next":
            # Check if user approved
            response = get_tool_result(messages, "user_interaction")
            logger.debug(f"[ROUTE] User response: {response}")
            
            if response == "APPROVED":
                next_stage = NEXT_STAGE[current_stage]
                logger.info(f"[ROUTE] APPROVED → progressing to {next_stage}")
                return next_stage
            else:
                logger.info(f"[ROUTE] User provided feedback → back to {current_stage}")
                return current_stage
        else:
            # intention="self" - always back to current stage
            logger.info(f"[ROUTE] intention=self → back to {current_stage}")
            return current_stage
    
    # 3. Default: back to self (continue working)
    logger.info(f"[ROUTE] No routing trigger → back to {current_stage}")
    return current_stage


def route_from_orchestrator(state: dict) -> str:
    """
    Routing logic for orchestrator.
    
    Simply check if route_to_stage was called and return target.
    If not, stay in orchestrator (waiting for user input or thinking).
    
    Args:
        state: Current graph state
        
    Returns:
        Next node name: target stage or "orchestrator"
    """
    messages = state.get("messages", [])
    logger.info("[ROUTE] Evaluating routing from orchestrator")
    
    route_call = get_tool_call(messages, "route_to_stage")
    if route_call:
        args = route_call.get("args", {})
        target_stage = args.get("stage", "orchestrator")
        context = args.get("context", "")
        logger.info(f"[ROUTE] route_to_stage called → {target_stage}")
        if context:
            logger.debug(f"[ROUTE] Context: {context[:100]}")
        return target_stage
    
    # No routing tool called - stay at orchestrator
    logger.info("[ROUTE] No routing → staying at orchestrator")
    return "orchestrator"
