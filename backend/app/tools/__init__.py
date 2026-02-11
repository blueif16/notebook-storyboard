"""Tools Module - V2 Architecture

Tool organization:
- hitl_tools: escalate, present_enhanced_story
- story_tools: generate_character_portrait, generate_page_image
"""

from .hitl_tools import escalate, present_enhanced_story, present_style_options
from .story_tools import (
    generate_character_portrait,
    generate_page_image,
)


# =============================================================================
# TOOL SETS BY AGENT
# =============================================================================

# Enhance Agent: 只需要 present_enhanced_story 和 escalate
# user_interaction 已移到 parent node 中处理
ENHANCE_TOOLS = [
    present_enhanced_story,
    escalate,
]

# Portrait Agent: character generation only (no user_interaction)
PORTRAIT_TOOLS = [
    generate_character_portrait,
    escalate,
]

# Style Agent: style selection
STYLE_TOOLS = [
    present_style_options,
    escalate,
]

# Story Agent: page generation only (no save_storybook - pages saved to state automatically)
STORY_TOOLS = [
    generate_page_image,
    escalate,
]


__all__ = [
    # HITL tools
    "escalate",
    "present_enhanced_story",
    "present_style_options",
    # Functional tools
    "generate_character_portrait",
    "generate_page_image",
    # Tool sets
    "ENHANCE_TOOLS",
    "STYLE_TOOLS",
    "PORTRAIT_TOOLS",
    "STORY_TOOLS",
]
