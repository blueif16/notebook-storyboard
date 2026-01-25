/**
 * Storybook State Types for AG-UI
 * Mirrors backend StorybookState from storybook_graph.py
 */

export interface Character {
  name: string;
  description?: string;
  image_id: string;
  image_url: string;
}

export interface Page {
  page_number: number;
  image_id: string;
  image_url: string;
  plot?: string;
}

export interface StorybookState {
  // Pipeline stage
  stage: "idle" | "starting" | "enhancing" | "characters_generated" | "generating_pages" | "complete" | "error";
  progress: number; // 0-100
  
  // Generated content
  characters: Character[];
  pages: Page[];
  
  // Final result
  storybook_id: string | null;
  title: string | null;
  
  // Counts for progress display
  characters_count: number;
  pages_count: number;
}

export const initialStorybookState: StorybookState = {
  stage: "idle",
  progress: 0,
  characters: [],
  pages: [],
  storybook_id: null,
  title: null,
  characters_count: 0,
  pages_count: 0,
};

// Interrupt payload types
export interface UserInputInterrupt {
  type: "user_input";
  question: string;
  images?: Array<{
    url: string;
    caption: string;
  }>;
}
