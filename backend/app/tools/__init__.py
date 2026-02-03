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

# Enhance Agent: HITL tools + present tool
ENHANCE_TOOLS = [
    present_enhanced_story,
    user_interaction,
    escalate,
]

# Portrait Agent: character generation + HITL
PORTRAIT_TOOLS = [
    generate_character_portrait,
    user_interaction,
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
