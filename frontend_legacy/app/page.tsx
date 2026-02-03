"use client";

import { useState, useEffect } from "react";
import { CanvasWrapper } from "@/components/living-canvas/CanvasWrapper";
import { SceneCard } from "@/components/living-canvas/SceneCard";
import { FloatingCompanion } from "@/components/living-canvas/FloatingCompanion";
import { Dock } from "@/components/living-canvas/Dock";
import { SourcesOverlay } from "@/components/living-canvas/SourcesOverlay";
import { CharactersPanel } from "@/components/storybook/CharactersPanel";
import { HITLModal } from "@/components/storybook/HITLModal";
import { Source } from "@/lib/types";
import { useToast } from "@/hooks/use-toast";
import { useCoAgent, useCopilotChat } from "@copilotkit/react-core";
import { StorybookState, initialStorybookState } from "@/types/storybook-state";

export default function Home() {
  const { toast } = useToast();

  // Thread Management
  const [threadId, setThreadId] = useState<string>("");
  useEffect(() => {
    setThreadId(`storybook-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`);
  }, []);

  // Agent State - auto-synced with backend
  const { state } = useCoAgent<StorybookState>({
    name: "storybookAgent",
    initialState: initialStorybookState,
    ...(threadId && { threadId }),
  });

  const { appendMessage } = useCopilotChat();

  // Local State for Sources
  const [sources, setSources] = useState<Source[]>([]);
  const [isSourcesOpen, setIsSourcesOpen] = useState(false);

  // Debug: Log state changes
  useEffect(() => {
    console.log("[STATE]", {
      stage: state.current_stage,
      characters: state.characters.length,
      pages: state.pages.length,
      enhanced_story: state.enhanced_story ? "✓" : "✗",
    });
  }, [state]);

  // --- Source Handlers ---

  const handleAddUrl = async (url: string) => {
    const tempId = `source-${Date.now()}`;
    const newSource: Source = {
      id: tempId, url, status: "loading", addedAt: Date.now()
    };
    setSources(prev => [...prev, newSource]);

    try {
      const res = await fetch("/api/scrape", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Failed to scrape");

      setSources(prev => prev.map(s => s.id === tempId ? {
        ...newSource, status: "success", title: data.title, content: data.content, text: data.text
      } : s));
      toast({ title: "Source added successfully" });
    } catch {
      setSources(prev => prev.map(s => s.id === tempId ? { ...s, status: "error", error: "Failed to load" } : s));
      toast({ title: "Failed to add source", variant: "destructive" });
    }
  };

  const handleAddFile = async (file: File) => {
    const tempId = `file-${Date.now()}`;
    const newSource: Source = {
      id: tempId, url: file.name, title: file.name, status: "loading", addedAt: Date.now(),
    };
    setSources(prev => [...prev, newSource]);

    try {
      const formData = new FormData();
      formData.append("file", file);
      const res = await fetch("/api/upload", { method: "POST", body: formData });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Failed to upload");

      setSources(prev => prev.map(s => s.id === tempId ? {
        ...newSource, status: "success", title: data.title || file.name, text: data.text, content: data.content
      } : s));
      toast({ title: "File added successfully" });
    } catch {
      setSources(prev => prev.map(s => s.id === tempId ? { ...s, status: "error", error: "Failed to upload" } : s));
      toast({ title: "Failed to add PDF", variant: "destructive" });
    }
  };

  const handleRemoveSource = (id: string) => {
    setSources(prev => prev.filter(s => s.id !== id));
  };

  // --- Generation Handler ---

  const handleGenerate = async () => {
    if (sources.filter(s => s.status === "success").length === 0) {
      toast({ title: "No valid sources", description: "Please add a source first!" });
      setIsSourcesOpen(true);
      return;
    }

    const context = sources
      .filter(s => s.status === "success")
      .map(s => `Title: ${s.title}\nContent: ${s.text?.slice(0, 3000)}`)
      .join("\n\n");

    toast({ title: "Starting Creative Process", description: "The agent is reading your sources..." });

    // @ts-expect-error - CopilotKit API compatibility
    await appendMessage(`I have added the following sources. Please create a storybook based on them:\n\n${context}`);
  };

  return (
    <>
      <CanvasWrapper>
        {/* Empty State */}
        {state.pages.length === 0 && (
          <div className="flex flex-col items-center justify-center p-12 bg-white/30 backdrop-blur-md rounded-3xl border border-white/40">
            <h1 className="text-4xl font-serif font-medium text-gray-800 mb-4">
              The Living Canvas
            </h1>
            <p className="text-gray-500 mb-8 max-w-md text-center">
              Add content sources via the dock, then ask the creative companion to weave a story for you.
            </p>
            <div className="w-24 h-24 rounded-full bg-gradient-to-tr from-orange-200 to-purple-200 blur-xl opacity-60 animate-pulse" />
          </div>
        )}

        {/* Characters Panel - appears during portrait stage */}
        {state.characters.length > 0 && (
          <CharactersPanel characters={state.characters} />
        )}

        {/* Pages appear one by one as they're generated */}
        {state.pages.map((page, index) => (
          <SceneCard
            key={page.page_number || index}
            index={index}
            image={page.image_url || ""}
            text={page.plot || ""}
          />
        ))}
      </CanvasWrapper>

      {/* HITL Modal - type-driven */}
      <HITLModal state={state} threadId={threadId} />

      {/* Chat Companion - always visible on right */}
      <FloatingCompanion threadId={threadId} />

      <Dock
        onAddSource={() => setIsSourcesOpen(true)}
        onViewSources={() => setIsSourcesOpen(true)}
        onGenerate={handleGenerate}
      />

      <SourcesOverlay
        isOpen={isSourcesOpen}
        onClose={() => setIsSourcesOpen(false)}
        sources={sources}
        onAddUrl={handleAddUrl}
        onAddFile={handleAddFile}
        onRemoveSource={handleRemoveSource}
      />
    </>
  );
}
