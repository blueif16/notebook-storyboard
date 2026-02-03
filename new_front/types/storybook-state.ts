/**
 * Storybook State Types for AG-UI
 * Mirrors backend StorybookState from storybook_graph.py
 */

export interface Character {
  name: string;
  description?: string;
  image_id?: string;
  image_url?: string;
}

export interface Page {
  page_number: number;
  plot?: string;
  image_id?: string;
  image_url?: string;
}

export interface StorybookState {
  messages: Array<any>;

  // Core outputs
  enhanced_story?: string;
  characters: Character[];
  pages: Page[];
  storybook_id?: string;

  // Streaming partials (for real-time updates)
  review_type?: "story_review" | "character_review" | "pages_review";
  enhanced_story_partial?: string;
  characters_partial?: Character[];
  pages_partial?: Page[];
  is_streaming?: boolean;

  // Metadata
  current_stage?: "orchestrator" | "enhance" | "portrait" | "story";
}

export const initialStorybookState: StorybookState = {
  messages: [],
  enhanced_story: undefined,
  characters: [],
  pages: [],
  storybook_id: undefined,
  current_stage: "orchestrator",
};

// HITL Interrupt types
export interface HITLInterrupt {
  type: "story_review" | "character_review" | "pages_review";
  intention: "self" | "next";
  prompt: string;
}
