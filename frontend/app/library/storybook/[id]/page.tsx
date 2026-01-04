"use client";

import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import { ArrowLeft, Download, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { StoryBook } from "@/components/StoryBook";
import { getStorybookById, deleteAsset, exportStorybookAsJSON } from "@/lib/storage";
import { StoredStorybook } from "@/lib/types";
import { useToast } from "@/hooks/use-toast";

export default function StorybookViewPage() {
  const router = useRouter();
  const params = useParams();
  const { toast } = useToast();
  const [storybook, setStorybook] = useState<StoredStorybook | null>(null);

  useEffect(() => {
    const id = params.id as string;
    if (id) {
      const loaded = getStorybookById(id);
      if (loaded) {
        setStorybook(loaded);
      } else {
        toast({ title: "Storybook not found", variant: "destructive" });
        router.push("/library");
      }
    }
  }, [params.id, router, toast]);

  const handleDelete = () => {
    if (storybook && confirm("Are you sure you want to delete this storybook?")) {
      deleteAsset(storybook.id);
      toast({ title: "Storybook deleted" });
      router.push("/library");
    }
  };

  const handleExport = () => {
    if (storybook) {
      exportStorybookAsJSON(storybook);
      toast({ title: "Storybook exported" });
    }
  };

  if (!storybook) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-500">Loading storybook...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 to-orange-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => router.push("/library")}
                className="hover:bg-gray-100"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Library
              </Button>
              <div>
                <h1 className="text-xl font-bold text-black">{storybook.title}</h1>
                <p className="text-sm text-gray-500">
                  {storybook.pages.length} pages • Created {new Date(storybook.createdAt).toLocaleDateString()}
                </p>
              </div>
            </div>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handleExport}
              >
                <Download className="w-4 h-4 mr-2" />
                Export
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={handleDelete}
                className="text-red-600 hover:text-red-700 hover:bg-red-50"
              >
                <Trash2 className="w-4 h-4 mr-2" />
                Delete
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Storybook Viewer */}
      <div className="py-8">
        <StoryBook pages={storybook.pages} title={storybook.title} />
      </div>
    </div>
  );
}
