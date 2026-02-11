"use client";

import { StorybookState, CANVAS_VIEWS, ViewConfig } from "@/types/storybook-state";
import { useEffect, useRef, useCallback, useState } from "react";

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
  const [showDemo, setShowDemo] = useState(false);

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

  // Demo data for testing shapes
  const createDemoShapes = useCallback((type: 'story' | 'characters' | 'pages') => {
    if (!editor) return;

    console.log(`[HITLModal] 🎭 Creating demo ${type} shapes`);

    if (type === 'story') {
      const shapeId = `shape:demo-story-review` as any;
      editor.createShape({
        id: shapeId,
        type: 'story-review' as any,
        x: CANVAS_LAYOUT.STORY_REVIEW.x,
        y: CANVAS_LAYOUT.STORY_REVIEW.y,
        props: {
          w: CANVAS_LAYOUT.STORY_REVIEW.w,
          h: CANVAS_LAYOUT.STORY_REVIEW.h,
          enhancedStory: '从前，在一片被薰衣草环绕的小村庄里，住着一只名叫皮普的小企鹅。皮普与众不同——他对"大蓝"有着无尽的向往，那是村里的老者们口中传说的神秘海洋。\n\n每天清晨，皮普都会爬上村庄最高的山丘，凝视着地平线上那抹神秘的蓝色。他的心中燃烧着探险的火焰，渴望踏上寻找大蓝的旅程。',
          enhancedStoryPartial: '',
          characters: [
            { index: 0, name: '皮普', description: '一只充满好奇心的小企鹅，梦想着探索神秘的大蓝' },
            { index: 1, name: '智者乌龟', description: '村里最年长的居民，知道关于大蓝的古老传说' },
          ],
          isStreaming: false
        }
      });
      
      // Navigate directly to shape position
      setTimeout(() => {
        editor.setCamera(
          { x: -CANVAS_LAYOUT.STORY_REVIEW.x + 50, y: -CANVAS_LAYOUT.STORY_REVIEW.y + 50, z: 0.8 },
          { animation: { duration: 500 } }
        );
      }, 100);
    }

    if (type === 'characters') {
      const demoCharacters = [
        { index: 0, name: '皮普', description: '一只充满好奇心的小企鹅', imageUrl: 'https://picsum.photos/seed/pip/400/400' },
        { index: 1, name: '智者乌龟', description: '村里最年长的居民', imageUrl: 'https://picsum.photos/seed/turtle/400/400' },
        { index: 2, name: '蝴蝶精灵', description: '森林中的神秘向导', imageUrl: '' }, // No image to test loading state
      ];

      demoCharacters.forEach((character, index) => {
        const shapeId = `shape:demo-character-${index}` as any;
        const x = CANVAS_LAYOUT.CHARACTER_REVIEW.x + index * (CANVAS_LAYOUT.CHARACTER_CARD.w + CANVAS_LAYOUT.CHARACTER_CARD.gap);
        editor.createShape({
          id: shapeId,
          type: 'character-card' as any,
          x,
          y: CANVAS_LAYOUT.CHARACTER_REVIEW.y,
          props: {
            w: CANVAS_LAYOUT.CHARACTER_CARD.w,
            h: CANVAS_LAYOUT.CHARACTER_CARD.h,
            character,
            isReviewMode: false,
            isStreaming: index === 2 // Last one shows streaming state
          }
        });
      });
      
      // Navigate directly to shape position
      setTimeout(() => {
        editor.setCamera(
          { x: -CANVAS_LAYOUT.CHARACTER_REVIEW.x + 50, y: -CANVAS_LAYOUT.CHARACTER_REVIEW.y + 50, z: 0.6 },
          { animation: { duration: 500 } }
        );
      }, 100);
    }

    if (type === 'pages') {
      const demoPages = [
        { pageNumber: 1, prompt: '皮普站在山丘上，凝视着远方的地平线', imageUrl: 'https://picsum.photos/seed/page1/800/600' },
        { pageNumber: 2, prompt: '皮普踏上了前往大蓝的旅程', imageUrl: 'https://picsum.photos/seed/page2/800/600' },
        { pageNumber: 3, prompt: '在森林中遇到了智者乌龟', imageUrl: '' }, // No image to test loading state
        { pageNumber: 4, prompt: '终于看到了神秘的大蓝', imageUrl: 'https://picsum.photos/seed/page4/800/600' },
      ];

      demoPages.forEach((page, index) => {
        const shapeId = `shape:demo-page-${page.pageNumber}` as any;
        const col = index % 4;
        const row = Math.floor(index / 4);
        const x = CANVAS_LAYOUT.PAGES_REVIEW.x + col * (CANVAS_LAYOUT.PAGE_CARD.w + CANVAS_LAYOUT.PAGE_CARD.gap);
        const y = CANVAS_LAYOUT.PAGES_REVIEW.y + row * (CANVAS_LAYOUT.PAGE_CARD.h + CANVAS_LAYOUT.PAGE_CARD.gap);
        
        editor.createShape({
          id: shapeId,
          type: 'storybook-page' as any,
          x,
          y,
          props: {
            w: CANVAS_LAYOUT.PAGE_CARD.w,
            h: CANVAS_LAYOUT.PAGE_CARD.h,
            page,
            isStreaming: index === 2 // Third one shows streaming state
          }
        });
      });
      
      // Navigate directly to shape position
      setTimeout(() => {
        editor.setCamera(
          { x: -CANVAS_LAYOUT.PAGES_REVIEW.x + 50, y: -CANVAS_LAYOUT.PAGES_REVIEW.y + 50, z: 0.5 },
          { animation: { duration: 500 } }
        );
      }, 100);
    }
  }, [editor]);

  // Clear all demo shapes
  const clearDemoShapes = useCallback(() => {
    if (!editor) return;
    const allShapeIds = editor.getCurrentPageShapeIds();
    const demoIds = [...allShapeIds].filter((id: string) => id.includes('demo-'));
    if (demoIds.length > 0) {
      editor.deleteShapes(demoIds);
      console.log(`[HITLModal] 🗑️ Cleared ${demoIds.length} demo shapes`);
    }
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
      
      // Check if this page is currently being generated
      const isGenerating = state.pageGeneratingIndex === index && state.isStreaming;
      
      const shapeProps = {
        w: CANVAS_LAYOUT.PAGE_CARD.w,
        h: CANVAS_LAYOUT.PAGE_CARD.h,
        page: page,
        isStreaming: isGenerating
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
  }, [editor, state.pages, state.pageGeneratingIndex, state.isStreaming, state.reviewType]);

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

  return (
    <>
      {/* Demo Panel - Bottom Left, above Logs */}
      <div
        style={{
          position: 'fixed',
          bottom: 56,
          left: 16,
          zIndex: 99999,
        }}
      >
        {/* Toggle Button */}
        <button
          onClick={() => setShowDemo(!showDemo)}
          style={{
            padding: '8px 12px',
            backgroundColor: showDemo ? '#ef4444' : '#8b5cf6',
            color: 'white',
            border: 'none',
            borderRadius: 8,
            cursor: 'pointer',
            fontSize: 12,
            fontWeight: 600,
            boxShadow: '0 2px 10px rgba(0,0,0,0.2)',
          }}
        >
          {showDemo ? '✕ Close Demo' : '🎭 Demo Shapes'}
        </button>
        
        {/* Demo Panel */}
        {showDemo && (
          <div
            style={{
              position: 'absolute',
              bottom: 44,
              left: 0,
              backgroundColor: 'white',
              padding: 16,
              borderRadius: 12,
              boxShadow: '0 4px 20px rgba(0,0,0,0.2)',
              minWidth: 200,
            }}
          >
            <div style={{ fontWeight: 600, marginBottom: 12, fontSize: 14 }}>
              Test Shape Rendering
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              <button
                onClick={() => createDemoShapes('story')}
                style={{
                  padding: '8px 12px',
                  backgroundColor: '#10b981',
                  color: 'white',
                  border: 'none',
                  borderRadius: 6,
                  cursor: 'pointer',
                  fontSize: 13,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                }}
              >
                <span>📖</span> Story Review
              </button>
              <button
                onClick={() => createDemoShapes('characters')}
                style={{
                  padding: '8px 12px',
                  backgroundColor: '#3b82f6',
                  color: 'white',
                  border: 'none',
                  borderRadius: 6,
                  cursor: 'pointer',
                  fontSize: 13,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                }}
              >
                <span>🎨</span> Character Cards
              </button>
              <button
                onClick={() => createDemoShapes('pages')}
                style={{
                  padding: '8px 12px',
                  backgroundColor: '#f59e0b',
                  color: 'white',
                  border: 'none',
                  borderRadius: 6,
                  cursor: 'pointer',
                  fontSize: 13,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                }}
              >
                <span>📄</span> Page Cards
              </button>
              <hr style={{ border: 'none', borderTop: '1px solid #e5e7eb', margin: '4px 0' }} />
              <button
                onClick={clearDemoShapes}
                style={{
                  padding: '8px 12px',
                  backgroundColor: '#6b7280',
                  color: 'white',
                  border: 'none',
                  borderRadius: 6,
                  cursor: 'pointer',
                  fontSize: 13,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                }}
              >
                <span>🗑️</span> Clear Demo Shapes
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Navigator - Only show if multiple views available */}
      {availableViews.length > 1 && (
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
      )}
    </>
  );
}
