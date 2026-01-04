"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import {
  BookOpen,
  Presentation,
  Network,
  Music,
  FileText,
  Trash2,
  Download,
  ArrowLeft,
  Calendar,
  Layers
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { StoredAsset } from "@/lib/types";
import { getAllAssets, deleteAsset, exportStorybookAsJSON } from "@/lib/storage";
import { useToast } from "@/hooks/use-toast";

const assetTypeConfig = {
  storybook: { icon: BookOpen, color: "text-amber-600", bg: "bg-amber-50", label: "Storybook" },
  slides: { icon: Presentation, color: "text-blue-600", bg: "bg-blue-50", label: "Slides" },
  mindmap: { icon: Network, color: "text-purple-600", bg: "bg-purple-50", label: "Mindmap" },
  audio: { icon: Music, color: "text-green-600", bg: "bg-green-50", label: "Audio" },
  summary: { icon: FileText, color: "text-gray-600", bg: "bg-gray-50", label: "Summary" },
};

export default function LibraryPage() {
  const router = useRouter();
  const { toast } = useToast();
  const [assets, setAssets] = useState<StoredAsset[]>([]);
  const [filter, setFilter] = useState<StoredAsset["type"] | "all">("all");

  useEffect(() => {
    loadAssets();
  }, []);

  const loadAssets = () => {
    const allAssets = getAllAssets();
    setAssets(allAssets);
  };

  const handleDelete = (id: string) => {
    if (confirm("Are you sure you want to delete this asset?")) {
      deleteAsset(id);
      loadAssets();
      toast({ title: "Asset deleted successfully" });
    }
  };

  const handleExport = (asset: StoredAsset) => {
    if (asset.type === "storybook") {
      exportStorybookAsJSON(asset.data);
      toast({ title: "Storybook exported" });
    }
  };

  const handleView = (asset: StoredAsset) => {
    if (asset.type === "storybook") {
      router.push(`/library/storybook/${asset.id}`);
    }
  };

  const filteredAssets = filter === "all"
    ? assets
    : assets.filter(a => a.type === filter);

  const assetCounts = {
    all: assets.length,
    storybook: assets.filter(a => a.type === "storybook").length,
    slides: assets.filter(a => a.type === "slides").length,
    mindmap: assets.filter(a => a.type === "mindmap").length,
    audio: assets.filter(a => a.type === "audio").length,
    summary: assets.filter(a => a.type === "summary").length,
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => router.push("/")}
                className="hover:bg-gray-100"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back
              </Button>
              <div>
                <h1 className="text-2xl font-bold text-black">Asset Library</h1>
                <p className="text-sm text-gray-500">
                  {assetCounts.all} {assetCounts.all === 1 ? "asset" : "assets"} saved
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Filter Tabs */}
        <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
          <Button
            variant={filter === "all" ? "default" : "outline"}
            size="sm"
            onClick={() => setFilter("all")}
            className="whitespace-nowrap"
          >
            <Layers className="w-4 h-4 mr-2" />
            All ({assetCounts.all})
          </Button>
          {Object.entries(assetTypeConfig).map(([type, config]) => {
            const Icon = config.icon;
            const count = assetCounts[type as keyof typeof assetCounts];
            return (
              <Button
                key={type}
                variant={filter === type ? "default" : "outline"}
                size="sm"
                onClick={() => setFilter(type as StoredAsset["type"])}
                className="whitespace-nowrap"
              >
                <Icon className="w-4 h-4 mr-2" />
                {config.label} ({count})
              </Button>
            );
          })}
        </div>

        {/* Assets Grid */}
        {filteredAssets.length === 0 ? (
          <div className="text-center py-16">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-100 mb-4">
              <Layers className="w-8 h-8 text-gray-400" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No assets yet</h3>
            <p className="text-gray-500 mb-4">
              Generate storybooks, slides, and more to see them here
            </p>
            <Button onClick={() => router.push("/")}>
              Go to Home
            </Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredAssets.map((asset) => {
              const config = assetTypeConfig[asset.type];
              const Icon = config.icon;

              return (
                <div
                  key={asset.id}
                  className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-lg transition-shadow cursor-pointer group"
                  onClick={() => handleView(asset)}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className={`p-2 rounded-lg ${config.bg}`}>
                      <Icon className={`w-5 h-5 ${config.color}`} />
                    </div>
                    <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      {asset.type === "storybook" && (
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleExport(asset);
                          }}
                        >
                          <Download className="w-4 h-4" />
                        </Button>
                      )}
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-8 w-8 text-red-600 hover:text-red-700 hover:bg-red-50"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDelete(asset.id);
                        }}
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>

                  <h3 className="font-semibold text-black mb-2 line-clamp-2">
                    {asset.title}
                  </h3>

                  <div className="flex items-center gap-2 text-xs text-gray-500 mb-2">
                    <Calendar className="w-3 h-3" />
                    {new Date(asset.createdAt).toLocaleDateString()}
                  </div>

                  {asset.metadata?.sourceCount && (
                    <div className="text-xs text-gray-500">
                      From {asset.metadata.sourceCount} source{asset.metadata.sourceCount !== 1 ? "s" : ""}
                    </div>
                  )}

                  <div className="mt-3 pt-3 border-t border-gray-100">
                    <span className={`text-xs font-medium ${config.color}`}>
                      {config.label}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

