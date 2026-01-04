import { StoredAsset, StoredStorybook, StoryPage } from "./types";

const STORAGE_KEY = "hyperbooklm_assets";
const STORYBOOKS_KEY = "hyperbooklm_storybooks";

// Generic asset storage
export const saveAsset = (asset: StoredAsset): void => {
  if (typeof window === "undefined") return;

  try {
    const existing = getAllAssets();
    const updated = [asset, ...existing.filter(a => a.id !== asset.id)];
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
  } catch (error) {
    console.error("Failed to save asset:", error);
  }
};

export const getAllAssets = (): StoredAsset[] => {
  if (typeof window === "undefined") return [];

  try {
    const data = localStorage.getItem(STORAGE_KEY);
    return data ? JSON.parse(data) : [];
  } catch (error) {
    console.error("Failed to load assets:", error);
    return [];
  }
};

export const getAssetById = (id: string): StoredAsset | null => {
  const assets = getAllAssets();
  return assets.find(a => a.id === id) || null;
};

export const deleteAsset = (id: string): void => {
  if (typeof window === "undefined") return;

  try {
    const assets = getAllAssets();
    const filtered = assets.filter(a => a.id !== id);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(filtered));
  } catch (error) {
    console.error("Failed to delete asset:", error);
  }
};

export const getAssetsByType = (type: StoredAsset["type"]): StoredAsset[] => {
  return getAllAssets().filter(a => a.type === type);
};

// Storybook-specific storage
export const saveStorybook = (
  title: string,
  pages: StoryPage[],
  sourceTitles: string[] = []
): StoredStorybook => {
  const storybook: StoredStorybook = {
    id: `storybook-${Date.now()}`,
    title,
    pages,
    createdAt: Date.now(),
    sourceCount: sourceTitles.length,
    sourceTitles,
  };

  // Save as generic asset
  const asset: StoredAsset = {
    id: storybook.id,
    type: "storybook",
    title: storybook.title,
    createdAt: storybook.createdAt,
    data: storybook,
    metadata: {
      sourceCount: storybook.sourceCount,
      sourceTitles: storybook.sourceTitles,
    },
  };

  saveAsset(asset);
  return storybook;
};

export const getAllStorybooks = (): StoredStorybook[] => {
  return getAssetsByType("storybook").map(a => a.data as StoredStorybook);
};

export const getStorybookById = (id: string): StoredStorybook | null => {
  const asset = getAssetById(id);
  return asset?.type === "storybook" ? (asset.data as StoredStorybook) : null;
};

// Export storybook as JSON
export const exportStorybookAsJSON = (storybook: StoredStorybook): void => {
  const json = JSON.stringify(storybook, null, 2);
  const blob = new Blob([json], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `${storybook.title.replace(/\s+/g, "-")}-${storybook.id}.json`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
};
