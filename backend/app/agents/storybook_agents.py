"""Storybook Agents - V2 Hierarchical Architecture

Uses agent caching pattern for efficiency.
Each agent has specific tools and responsibilities.
"""
from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
import logging

from ..config import GOOGLE_API_KEY, GEMINI_TEXT_MODEL
from ..tools import (
    ENHANCE_TOOLS,
    PORTRAIT_TOOLS,
    STORY_TOOLS,
)

logger = logging.getLogger(__name__)


# =============================================================================
# MODEL FACTORY
# =============================================================================

def get_gemini_model():
    """Get Gemini model with streaming enabled."""
    return ChatGoogleGenerativeAI(
        model=GEMINI_TEXT_MODEL,
        google_api_key=GOOGLE_API_KEY,
        temperature=0.7,
        streaming=True,  # Critical for real-time updates
    )


# =============================================================================
# AGENT CACHE
# =============================================================================

class AgentCache:
    """
    Agent caching pattern from LangGraph guide Section 3.2.
    Avoids recreating agent instances on every node call.
    """
    _agents = {}
    
    @classmethod
    def get_agent(cls, name: str):
        """Get or create agent by name."""
        if name not in cls._agents:
            logger.info(f"[AGENT CACHE] Creating new agent: {name}")
            creators = {
                "enhance": create_enhance_agent,
                "portrait": create_portrait_agent,
                "story": create_story_agent,
            }
            if name not in creators:
                raise ValueError(f"Unknown agent: {name}")
            cls._agents[name] = creators[name]()
        else:
            logger.debug(f"[AGENT CACHE] Using cached agent: {name}")
        return cls._agents[name]
    
    @classmethod
    def clear_cache(cls):
        """Clear all cached agents (for testing)."""
        cls._agents = {}
        logger.info("[AGENT CACHE] Cache cleared")


# =============================================================================
# AGENT DEFINITIONS
# =============================================================================

def create_enhance_agent():
    """
    Enhance Agent: Story enhancement specialist.
    
    Tools: user_interaction, escalate
    Role: Enhance story ideas with vivid details
    """
    model = get_gemini_model()
    
    prompt = """You are a Story Enhancement specialist.

YOUR JOB:
1. Take user's story idea and enhance it with vivid details
2. Add visual descriptions for characters and scenes
3. Extract all main characters with physical descriptions
4. Make sure everything is writeen in user's language

YOUR TOOLS:
- present_enhanced_story: Mark story as ready for review (REQUIRED when done)
- escalate: If user wants something completely different

WORKFLOW:
1. User gives story idea
2. Enhance the story with vivid details
3. Extract characters with physical descriptions
4. Call present_enhanced_story(enhanced_story="...", characters=[...])
5. Stream a prompt asking user to review:
   "I've enhanced your story and identified X characters. Please review and approve to continue."

CRITICAL RULES:
- You MUST call present_enhanced_story when story is ready
- After calling the tool, stream a text prompt for the user
- DO NOT put story content in the text prompt - it's already in the tool call
- The tool call stores the data, your text message asks for review
- If user provides feedback, revise the story and call present_enhanced_story again

EXAMPLE:
Step 1: Call present_enhanced_story(
    enhanced_story="In the frozen Antarctic, a young penguin named Pip...",
    characters=[
        {"name": "Pip", "description": "A young emperor penguin with fluffy gray feathers..."},
        {"name": "Sila", "description": "A wise seal with silver whiskers..."}
    ]
)
Step 2: Stream text: "I've enhanced your story about Pip the penguin and identified 2 characters. Please review and approve to continue."

REMEMBER: Tool call stores data, text message asks for review."""
    
    return create_react_agent(
        model=model,
        tools=ENHANCE_TOOLS,
        name="enhance_agent",
        prompt=prompt
    )


def create_portrait_agent():
    """
    Portrait Agent: Character portrait specialist.
    
    Tools: generate_character_portrait, user_interaction, escalate
    Role: Generate portrait images for each character
    """
    model = get_gemini_model()
    
    prompt = """You are a Character Portrait specialist.

YOUR JOB:
1. Generate portrait image for EACH character
2. Show each portrait as it's ready (state updates automatically)
3. Output text to prompt user for review

YOUR TOOLS:
- generate_character_portrait: Creates portrait, auto-updates state with image_url
- escalate: If user wants to change story direction

WORKFLOW:
1. Read character info from conversation history (each character has an "index" field)
2. Generate portraits one by one using:
   generate_character_portrait(
       description=character["description"],
       character_name=character["name"],
       character_index=character["index"]  # IMPORTANT: Pass the index!
   )
3. After all portraits are generated, output text to prompt user:
   "I've generated portraits for all X characters. Please review and approve to continue to story pages."

IMPORTANT:
- ALWAYS pass character_index parameter when calling generate_character_portrait
- The index comes from the character object (character["index"])
- Frontend sees portraits appear one by one as you create them (via state updates)
- Each generate_character_portrait call updates state.characters[index] automatically
- Keep track of image_ids for later use in story pages
- DO NOT call user_interaction tool - just output text naturally
- After generating all portraits, output a text prompt asking user to review
- If user provides feedback, regenerate specific characters as needed"""
    
    return create_react_agent(
        model=model,
        tools=PORTRAIT_TOOLS,
        name="portrait_agent",
        prompt=prompt
    )


def create_story_agent():
    """
    Story Agent: Storybook illustrator and saver.
    
    Tools: generate_page_image, save_storybook, user_interaction, escalate
    Role: Create page illustrations and save final storybook
    """
    model = get_gemini_model()
    
    prompt = """You are a Storybook Illustrator.

YOUR JOB:
1. Break story into 6-12 pages
2. Generate illustration for each page using generate_page_image
3. Show pages as they're ready (state updates automatically)
4. Save complete storybook to database
5. Ask for final approval

YOUR TOOLS:
- generate_page_image: Creates page illustration, auto-updates state
- save_storybook: Saves to database when all pages ready
- user_interaction: Get user feedback
- escalate: If user wants to change direction

WORKFLOW:
1. Read story and character image_ids from conversation history
2. Plan 6-12 page breakdown with plot for each page
3. Generate pages one by one (use character image_ids for consistency!):
   generate_page_image(prompt="scene description", reference_image_ids=[char_ids], page_number=1)
4. After all pages ready, save storybook:
   save_storybook(title="...", description="...", pages=[...])
5. Call:
   user_interaction(
       type="pages_review",
       intention="next",
       prompt="Please review the complete storybook. Approve to finish."
   )

IMPORTANT:
- Frontend sees pages appear one by one as you create them (via state updates)
- Each generate_page_image call updates state.pages automatically
- Use character image_ids for visual consistency across pages
- Frontend reads pages from state, not from this tool
- Save storybook before final approval"""
    
    return create_react_agent(
        model=model,
        tools=STORY_TOOLS,
        name="story_agent",
        prompt=prompt
    )
