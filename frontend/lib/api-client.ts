// API client for backend storage
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface ApiStoredAsset {
  id: string;
  type: 'storybook' | 'slides' | 'mindmap' | 'audio' | 'summary';
  title: string;
  createdAt: number;
  data: any;
  metadata?: {
    sourceCount?: number;
    sourceTitles?: string[];
  };
}

export interface ApiStoredStorybook {
  id: string;
  title: string;
  pages: Array<{
    leftImage?: string;
    rightImage?: string;
    leftText?: string;
    rightText?: string;
    imagePrompt?: string;
  }>;
  createdAt: number;
  sourceCount: number;
  sourceTitles: string[];
}

// Asset API
export const assetApi = {
  async createAsset(asset: Omit<ApiStoredAsset, 'id' | 'createdAt'>): Promise<ApiStoredAsset> {
    const response = await fetch(`${API_BASE_URL}/api/assets/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(asset),
    });
    if (!response.ok) throw new Error('Failed to create asset');
    return response.json();
  },

  async getAllAssets(): Promise<ApiStoredAsset[]> {
    const response = await fetch(`${API_BASE_URL}/api/assets/`);
    if (!response.ok) throw new Error('Failed to fetch assets');
    return response.json();
  },

  async getAssetById(id: string): Promise<ApiStoredAsset> {
    const response = await fetch(`${API_BASE_URL}/api/assets/${id}`);
    if (!response.ok) throw new Error('Failed to fetch asset');
    return response.json();
  },

  async deleteAsset(id: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/assets/${id}`, {
      method: 'DELETE',
    });
    if (!response.ok) throw new Error('Failed to delete asset');
  },

  async getAssetsByType(type: string): Promise<ApiStoredAsset[]> {
    const response = await fetch(`${API_BASE_URL}/api/assets/type/${type}`);
    if (!response.ok) throw new Error('Failed to fetch assets by type');
    return response.json();
  },
};

// Storybook API
export const storybookApi = {
  async createStorybook(data: {
    title: string;
    pages: ApiStoredStorybook['pages'];
    sourceTitles?: string[];
  }): Promise<ApiStoredStorybook> {
    const response = await fetch(`${API_BASE_URL}/api/storybooks/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to create storybook');
    return response.json();
  },

  async getAllStorybooks(): Promise<ApiStoredStorybook[]> {
    const response = await fetch(`${API_BASE_URL}/api/storybooks/`);
    if (!response.ok) throw new Error('Failed to fetch storybooks');
    return response.json();
  },

  async getStorybookById(id: string): Promise<ApiStoredStorybook> {
    const response = await fetch(`${API_BASE_URL}/api/storybooks/${id}`);
    if (!response.ok) throw new Error('Failed to fetch storybook');
    return response.json();
  },

  async deleteStorybook(id: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/storybooks/${id}`, {
      method: 'DELETE',
    });
    if (!response.ok) throw new Error('Failed to delete storybook');
  },
};
