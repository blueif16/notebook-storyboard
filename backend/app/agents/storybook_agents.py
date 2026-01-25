"""Storybook Agents"""
from langgraph.prebuilt import create_react_agent
from google import genai

from ..config import GOOGLE_API_KEY, GEMINI_TEXT_MODEL
from ..tools import ORCHESTRATOR_TOOLS, STORY_GENERATOR_TOOLS


def create_orchestrator_agent():
    """Main agent: handles chat, character prep, delegation."""
    client = genai.Client(api_key=GOOGLE_API_KEY)
    
    return create_react_agent(
        model=client.models.get(GEMINI_TEXT_MODEL),
        tools=ORCHESTRATOR_TOOLS,
        name="orchestrator",
        prompt="""You are a storybook creator. User describes a story, you make it.

PROCESS (flexible):
1. User describes story → enhance_and_extract(story_text)
2. For each character → generate_character_portrait(description, character_name)
3. Optional: request_user_input("Here are your characters", images=[...]) if user asked or you think they want to see
4. Delegate to Story Generator with full context

Prepare final message for Story Generator with:
- Enhanced story
- Characters with image_id and image_url
- Any style/page count preferences mentioned

NO FIXED FLOW. Adapt to conversation."""
    )


def create_story_generator_agent():
    """Sequential page illustrator with dynamic references."""
    client = genai.Client(api_key=GOOGLE_API_KEY)
    
    return create_react_agent(
        model=client.models.get(GEMINI_TEXT_MODEL),
        tools=STORY_GENERATOR_TOOLS,
        name="story_generator",
        prompt="""You are a storybook illustrator creating pages sequentially.

FOR EACH PAGE:
1. Decide what scene to depict
2. Identify which characters appear → grab their image_ids
3. Decide if previous page reference needed for continuity
4. Call generate_page_image(prompt, [char_ids, prev_page_id?], page_number)

REFERENCE DECISIONS (your judgment):
- Character appears → use their image_id
- Same setting as previous → reference previous page_id
- New setting → only character references

PAGE COUNT: Decide based on story length (typically 6-12), honor if user specified

COMPLETION:
save_storybook(title="...", description="...", pages=[{page_number, image_id, image_url, plot}])

YOU decide everything. Make coherent, beautiful storybooks."""
    )
