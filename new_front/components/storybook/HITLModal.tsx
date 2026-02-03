"use client";

import { StorybookState } from "@/types/storybook-state";
import { useEffect } from "react";

interface HITLModalProps {
  state: StorybookState;
  threadId: string;
  editor: any; // tldraw Editor
}

// 演示数据
const DEMO_STORY_REVIEW_DATA = {
  enhancedStory: "从前，在一个遥远的森林里，住着一只聪明的小狐狸。它每天都在森林中探险，寻找新的朋友和有趣的故事。有一天，小狐狸遇到了一只迷路的小兔子，它决定帮助小兔子找到回家的路。经过一番努力，它们终于找到了小兔子的家，从此成为了最好的朋友。",
  characters: [
    {
      name: "小狐狸",
      description: "聪明勇敢的森林探险家，喜欢帮助别人"
    },
    {
      name: "小兔子",
      description: "可爱害羞的森林居民，善良友好"
    }
  ]
};

export function HITLModal({ state, editor }: HITLModalProps) {
  // 开发用：创建演示 story review shape
  const createDemoStoryReview = () => {
    if (!editor) return;

    const reviewShapeId = `shape:review-demo` as any;
    const existingShape = editor.getShape(reviewShapeId);

    if (!existingShape) {
      editor.createShape({
        id: reviewShapeId,
        type: 'story-review' as any,
        x: 100,
        y: 100,
        props: {
          enhancedStory: DEMO_STORY_REVIEW_DATA.enhancedStory,
          enhancedStoryPartial: "",
          characters: DEMO_STORY_REVIEW_DATA.characters,
          isStreaming: false
        }
      });
    }
  };

  // 当检测到 review_type 时，在 canvas 中创建相应的 shape
  useEffect(() => {
    if (!editor || !state.review_type) return;

    const reviewShapeId = `shape:review-${state.review_type}` as any;

    if (state.review_type === "story_review") {
      const existingShape = editor.getShape(reviewShapeId);

      if (!existingShape) {
        editor.createShape({
          id: reviewShapeId,
          type: 'story-review' as any,
          x: 100,
          y: 100,
          props: {
            enhancedStory: state.enhanced_story,
            enhancedStoryPartial: state.enhanced_story_partial,
            characters: state.characters_partial ?? state.characters,
            isStreaming: state.is_streaming ?? false
          }
        });
      } else {
        editor.updateShape({
          id: reviewShapeId,
          type: 'story-review' as any,
          props: {
            enhancedStory: state.enhanced_story,
            enhancedStoryPartial: state.enhanced_story_partial,
            characters: state.characters_partial ?? state.characters,
            isStreaming: state.is_streaming ?? false
          }
        });
      }
    }
  }, [editor, state.review_type, state.enhanced_story, state.enhanced_story_partial, state.characters, state.characters_partial]);

  // 渲染开发用按钮
  return (
    <div style={{ position: 'fixed', top: 10, left: 10, zIndex: 9999 }}>
      <button
        onClick={createDemoStoryReview}
        style={{
          padding: '8px 16px',
          backgroundColor: '#4CAF50',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer',
          fontSize: '14px',
          fontWeight: 'bold',
          boxShadow: '0 2px 4px rgba(0,0,0,0.2)'
        }}
      >
        [DEV] 测试 Story Review
      </button>
    </div>
  );
}
