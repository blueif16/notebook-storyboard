"use client";

import { StorybookState, CANVAS_VIEWS, ViewConfig } from "@/types/storybook-state";
import { useEffect, useRef, useCallback } from "react";

interface HITLModalProps {
  state: StorybookState;
  threadId: string;
  editor: any; // tldraw Editor
}

// Canvas layout constants
const CANVAS_LAYOUT = {
  STORY_REVIEW: { x: 100, y: 100, w: 1000, h: 700 },
  CHARACTER_REVIEW: { x: 100, y: 1000, w: 1400, h: 500 },
  PAGES_REVIEW: { x: 100, y: 1900, w: 1600, h: 800 },
  CHARACTER_CARD: { w: 280, h: 380, gap: 40 },
  PAGE_CARD: { w: 400, h: 500, gap: 50 },
};

export function HITLModal({ state, editor }: HITLModalProps) {
  const lastReviewType = useRef<string | null>(null);
  const hasNavigatedToCharacters = useRef(false);
  const hasNavigatedToPages = useRef(false);

  // Navigate to a specific view on canvas
  const navigateToView = useCallback((view: ViewConfig) => {
    if (!editor) return;
    
    console.log(`[HITLModal] 🧭 Navigating to view: ${view.id} (y=${view.y})`);
    
    editor.setCamera(
      { 
        x: -50,  // Small offset from left 
        y: -view.y - 50,  // Navigate to the view's Y position
        z: editor.getCamera().z || 1 
      },
      { 
        animation: { 
          duration: 500,
          easing: (t: number) => 1 - Math.pow(1 - t, 3)  // Ease out cubic
        } 
      }
    );
  }, [editor]);

  // Auto-navigate when reviewType changes
  useEffect(() => {
    if (!editor || !state.reviewType) return;
    
    // Only navigate on reviewType change
    if (state.reviewType === lastReviewType.current) return;
    lastReviewType.current = state.reviewType;
    
    const view = CANVAS_VIEWS.find(v => v.reviewType === state.reviewType);
    if (view) {
      // Delay navigation slightly to let shapes render first
      setTimeout(() => navigateToView(view), 100);
    }
  }, [editor, state.reviewType, navigateToView]);

  // Create/update story review shape
  useEffect(() => {
    if (!editor) return;
    if (state.reviewType !== "story_review" && !state.enhancedStory && !state.enhancedStoryPartial) return;

    const reviewShapeId = `shape:review-story_review` as any;
    const displayStory = state.enhancedStory || state.enhancedStoryPartial;
    const displayCharacters = state.charactersPartial ?? state.characters ?? [];

    if (!displayStory && displayCharacters.length === 0) return;

    const existingShape = editor.getShape(reviewShapeId);
    const shapeProps = {
      enhancedStory: state.enhancedStory,
      enhancedStoryPartial: state.enhancedStoryPartial,
      characters: displayCharacters,
      isStreaming: state.isStreaming ?? false
    };

    if (!existingShape) {
      console.log('[HITLModal] 📖 Creating story review shape');
      editor.createShape({
        id: reviewShapeId,
        type: 'story-review' as any,
        x: CANVAS_LAYOUT.STORY_REVIEW.x,
        y: CANVAS_LAYOUT.STORY_REVIEW.y,
        props: shapeProps
      });
    } else {
      editor.updateShape({
        id: reviewShapeId,
        type: 'story-review' as any,
        props: shapeProps
      });
    }
  }, [
    editor, 
    state.reviewType, 
    state.enhancedStory, 
    state.enhancedStoryPartial, 
    state.characters, 
    state.charactersPartial,
    state.isStreaming
  ]);

  // Create/update character card shapes for character_review
  useEffect(() => {
    if (!editor) return;
    if (!state.characters || state.characters.length === 0) return;

    // Create character cards in the character review area
    state.characters.forEach((character, index) => {
      const shapeId = `shape:character-review-${index}` as any;
      const existingShape = editor.getShape(shapeId);
      
      const x = CANVAS_LAYOUT.CHARACTER_REVIEW.x + index * (CANVAS_LAYOUT.CHARACTER_CARD.w + CANVAS_LAYOUT.CHARACTER_CARD.gap);
      const y = CANVAS_LAYOUT.CHARACTER_REVIEW.y;
      
      const isGenerating = state.portraitGeneratingIndex === index && state.isStreaming;
      
      const shapeProps = {
        w: CANVAS_LAYOUT.CHARACTER_CARD.w,
        h: CANVAS_LAYOUT.CHARACTER_CARD.h,
        character: character,
        isReviewMode: false,
        isStreaming: isGenerating
      };

      if (!existingShape) {
        console.log(`[HITLModal] 🎨 Creating character card: ${character.name}`);
        editor.createShape({
          id: shapeId,
          type: 'character-card' as any,
          x,
          y,
          props: shapeProps
        });
        
        // Track that we've created character cards
        if (!hasNavigatedToCharacters.current && state.reviewType === "character_review") {
          hasNavigatedToCharacters.current = true;
        }
      } else {
        editor.updateShape({
          id: shapeId,
          type: 'character-card' as any,
          props: shapeProps
        });
      }
    });
  }, [editor, state.characters, state.portraitGeneratingIndex, state.isStreaming, state.reviewType]);

  // Create/update page shapes for pages_review
  useEffect(() => {
    if (!editor) return;
    if (!state.pages || state.pages.length === 0) return;

    // Create page cards in the pages review area
    state.pages.forEach((page, index) => {
      const shapeId = `shape:page-review-${page.pageNumber}` as any;
      const existingShape = editor.getShape(shapeId);
      
      const col = index % 4;
      const row = Math.floor(index / 4);
      const x = CANVAS_LAYOUT.PAGES_REVIEW.x + col * (CANVAS_LAYOUT.PAGE_CARD.w + CANVAS_LAYOUT.PAGE_CARD.gap);
      const y = CANVAS_LAYOUT.PAGES_REVIEW.y + row * (CANVAS_LAYOUT.PAGE_CARD.h + CANVAS_LAYOUT.PAGE_CARD.gap);
      
      const shapeProps = {
        w: CANVAS_LAYOUT.PAGE_CARD.w,
        h: CANVAS_LAYOUT.PAGE_CARD.h,
        page: page
      };

      if (!existingShape) {
        console.log(`[HITLModal] 📄 Creating page card: Page ${page.pageNumber}`);
        editor.createShape({
          id: shapeId,
          type: 'storybook-page' as any,
          x,
          y,
          props: shapeProps
        });
        
        // Track that we've created page cards
        if (!hasNavigatedToPages.current && state.reviewType === "pages_review") {
          hasNavigatedToPages.current = true;
        }
      } else {
        editor.updateShape({
          id: shapeId,
          type: 'storybook-page' as any,
          props: shapeProps
        });
      }
    });
  }, [editor, state.pages, state.reviewType]);

  // Determine which views are available
  const getAvailableViews = () => {
    const available: ViewConfig[] = [];
    
    // Story view is always available if we have story content
    if (state.enhancedStory || state.enhancedStoryPartial) {
      available.push(CANVAS_VIEWS[0]);
    }
    
    // Characters view available if we have characters
    if (state.characters && state.characters.length > 0) {
      available.push(CANVAS_VIEWS[1]);
    }
    
    // Pages view available if we have pages
    if (state.pages && state.pages.length > 0) {
      available.push(CANVAS_VIEWS[2]);
    }
    
    return available;
  };

  const availableViews = getAvailableViews();
  const currentView = CANVAS_VIEWS.find(v => v.reviewType === state.reviewType);

  // Don't render navigator if only one or no views available
  if (availableViews.length <= 1) {
    return null;
  }

  return (
    <div 
      style={{ 
        position: 'fixed', 
        top: 16, 
        left: '50%', 
        transform: 'translateX(-50%)',
        zIndex: 9999,
        display: 'flex',
        gap: 8,
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        padding: '8px 12px',
        borderRadius: 12,
        boxShadow: '0 4px 20px rgba(0,0,0,0.15)',
        backdropFilter: 'blur(10px)',
      }}
    >
      {availableViews.map((view) => {
        const isActive = currentView?.id === view.id;
        return (
          <button
            key={view.id}
            onClick={() => navigateToView(view)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              padding: '8px 16px',
              backgroundColor: isActive ? '#3b82f6' : 'transparent',
              color: isActive ? 'white' : '#374151',
              border: 'none',
              borderRadius: 8,
              cursor: 'pointer',
              fontSize: 14,
              fontWeight: isActive ? 600 : 500,
              transition: 'all 0.2s ease',
            }}
            onMouseEnter={(e) => {
              if (!isActive) {
                e.currentTarget.style.backgroundColor = '#f3f4f6';
              }
            }}
            onMouseLeave={(e) => {
              if (!isActive) {
                e.currentTarget.style.backgroundColor = 'transparent';
              }
            }}
          >
            <span style={{ fontSize: 16 }}>{view.icon}</span>
            <span>{view.label}</span>
            {view.reviewType === "character_review" && state.charactersCount !== undefined && state.charactersCount > 0 && (
              <span style={{
                backgroundColor: isActive ? 'rgba(255,255,255,0.3)' : '#e5e7eb',
                padding: '2px 6px',
                borderRadius: 10,
                fontSize: 12,
              }}>
                {state.charactersCount}
              </span>
            )}
            {view.reviewType === "pages_review" && state.pagesCount !== undefined && state.pagesCount > 0 && (
              <span style={{
                backgroundColor: isActive ? 'rgba(255,255,255,0.3)' : '#e5e7eb',
                padding: '2px 6px',
                borderRadius: 10,
                fontSize: 12,
              }}>
                {state.pagesCount}
              </span>
            )}
          </button>
        );
      })}
      
      {/* Progress indicator when streaming */}
      {state.isStreaming && (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          marginLeft: 8,
          color: '#6b7280',
          fontSize: 12,
        }}>
          <span style={{
            width: 8,
            height: 8,
            backgroundColor: '#3b82f6',
            borderRadius: '50%',
            marginRight: 6,
            animation: 'pulse 1.5s infinite',
          }} />
          生成中...
        </div>
      )}
      
      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
      `}</style>
    </div>
  );
}
