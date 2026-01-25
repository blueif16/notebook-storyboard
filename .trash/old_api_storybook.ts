// API client for storybook generation

import type {
  GenerateCharactersRequest,
  GenerateCharactersResponse,
  GenerateStoryRequest,
  GenerateStoryResponse,
} from '@/types/storybook';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class StorybookAPIError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public details?: string
  ) {
    super(message);
    this.name = 'StorybookAPIError';
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new StorybookAPIError(
      errorData.detail || `API Error: ${response.statusText}`,
      response.status,
      errorData.detail
    );
  }
  return response.json();
}

export const storybookAPI = {
  /**
   * Phase 1: Generate characters from story text
   * Duration: ~30-60 seconds
   */
  async generateCharacters(
    request: GenerateCharactersRequest
  ): Promise<GenerateCharactersResponse> {
    const response = await fetch(`${API_BASE_URL}/api/storybooks/generate-characters`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    return handleResponse<GenerateCharactersResponse>(response);
  },

  /**
   * Phase 2: Generate complete story from characters
   * Duration: ~2-3 minutes
   */
  async generateStory(
    request: GenerateStoryRequest
  ): Promise<GenerateStoryResponse> {
    const response = await fetch(`${API_BASE_URL}/api/storybooks/generate-story`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    return handleResponse<GenerateStoryResponse>(response);
  },
};

export { StorybookAPIError };
