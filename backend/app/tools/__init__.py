"""Tools Module - V2 Architecture

Tool organization:
- hitl_tools: user_interaction, escalate
- story_tools: generate_character_portrait, generate_page_image, save_storybook
"""

from .hitl_tools import user_interaction, escalate, present_enhanced_story
from .story_tools import (
    generate_character_portrait,
    generate_page_image,
    save_storybook,
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

# Story Agent: page generation, saving, + HITL
STORY_TOOLS = [
    generate_page_image,
    save_storybook,
    user_interaction,
    escalate,
]


__all__ = [
    # HITL tools
    "user_interaction",
    "escalate",
    "present_enhanced_story",
    # Functional tools
    "generate_character_portrait",
    "generate_page_image",
    "save_storybook",
    # Tool sets
    "ENHANCE_TOOLS",
    "PORTRAIT_TOOLS",
    "STORY_TOOLS",
]
