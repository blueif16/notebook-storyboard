// Type definitions matching backend models

export interface Character {
  name: string;
  description: string;
  image_id?: string;
  image_url?: string;
}

export interface StoryPage {
  page_number: number;
  plot: string;
  character_names: string[];
  reference_page_numbers: number[];
  generated_image_id?: string;
  generated_image_url?: string;
}

export interface Story {
  story_id?: string;
  characters: Character[];
  pages: StoryPage[];
}

// API Request/Response types
export interface GenerateCharactersRequest {
  story_text: string;
  style: string;
}

export interface GenerateCharactersResponse {
  story_id: string;
  characters: Character[];
}

export interface GenerateStoryRequest {
  story_id: string;
  aspect_ratio?: string;
}

export interface GenerateStoryResponse {
  story: Story;
}

// UI-specific types
export interface StoryPageUI {
  imageUrl: string;
  text: string;
}

// Style options
export const STYLE_OPTIONS = [
  { id: 'whimsical', label: 'Whimsical & Playful', description: 'Colorful, hand-drawn watercolor aesthetic' },
  { id: 'adventure', label: 'Adventure & Brave', description: 'Bold, dynamic, cinematic action scenes' },
  { id: 'gentle', label: 'Gentle & Calm', description: 'Soft, calming, pastel watercolor style' },
  { id: 'magical', label: 'Magical & Dreamy', description: 'Dreamy, sparkly, fantasy 3D render' },
  { id: 'realistic', label: 'Realistic & Cinematic', description: 'Photorealistic, cinematic quality' },
  { id: 'anime', label: 'Anime Style', description: 'Vibrant anime with bold outlines' },
] as const;

export type StyleId = typeof STYLE_OPTIONS[number]['id'];
