/**
 * Storybook State Types for AG-UI
 * Mirrors backend StorybookState from storybook_graph.py
 * 
 * NOTE: Uses camelCase to match AG-UI protocol (backend converts snake_case to camelCase)
 */

export interface Character {
  index?: number;  // Auto-generated in enhance stage
  name: string;
  description?: string;
  imageId?: string;
  imageUrl?: string;
}

export interface Page {
  pageNumber: number;
  plot?: string;
  imageId?: string;
  imageUrl?: string;
}

export interface StorybookState {
  messages: Array<any>;

  // Core outputs
  enhancedStory?: string;
  characters: Character[];
  pages: Page[];
  storybookId?: string;
  title?: string;

  // Streaming partials (for real-time updates)
  // Empty string "" means no active review
  reviewType?: "" | "story_review" | "character_review" | "pages_review";
  enhancedStoryPartial?: string;
  charactersPartial?: Character[];
  pagesPartial?: Page[];
  isStreaming?: boolean;
  
  // Portrait generation tracking
  portraitGeneratingIndex?: number;

  // Metadata
  currentStage?: "orchestrator" | "enhance" | "portrait" | "story";
  
  // Progress counters
  charactersCount?: number;
  pagesCount?: number;
}

export const initialStorybookState: StorybookState = {
  messages: [],
  enhancedStory: "",
  characters: [],
  pages: [],
  storybookId: "",
  title: "",
  currentStage: "orchestrator",
  charactersCount: 0,
  pagesCount: 0,
  // Streaming fields
  reviewType: "",
  isStreaming: false,
  portraitGeneratingIndex: -1,
  enhancedStoryPartial: "",
  charactersPartial: [],
};

// HITL Interrupt types
export interface HITLInterrupt {
  type: "story_review" | "character_review" | "pages_review";
  intention: "self" | "next";
  prompt: string;
}

// View configuration for canvas navigation
export interface ViewConfig {
  id: string;
  label: string;
  icon: string;
  reviewType: "story_review" | "character_review" | "pages_review";
  y: number;  // Y position on canvas
}

export const CANVAS_VIEWS: ViewConfig[] = [
  { id: "story", label: "故事", icon: "📖", reviewType: "story_review", y: 0 },
  { id: "characters", label: "角色", icon: "🎨", reviewType: "character_review", y: 900 },
  { id: "pages", label: "页面", icon: "📄", reviewType: "pages_review", y: 1800 },
];
