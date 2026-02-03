"use client";

import { useState, useEffect } from "react";
import { useCoAgent } from "@copilotkit/react-core";
import { StorybookState } from "@/types/storybook-state";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { StoryReviewContent } from "./StoryReviewContent";
import { CharacterReviewContent } from "./CharacterReviewContent";
import { PagesReviewContent } from "./PagesReviewContent";
import { X } from "lucide-react";

interface HITLInterrupt {
  type: "story_review" | "character_review" | "pages_review";
  intention: "self" | "next";
  prompt: string;
}

interface HITLModalProps {
  state: StorybookState;
  threadId: string;
}

export function HITLModal({ state, threadId }: HITLModalProps) {
  const [interrupt, setInterrupt] = useState<HITLInterrupt | null>(null);
  const [feedback, setFeedback] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { run } = useCoAgent<StorybookState>({
    name: "storybookAgent",
    ...(threadId && { threadId }),
  });

  // TODO: 实际的 interrupt 监听需要根据 CopilotKit 的 API 实现
  // 这里是伪代码示例
  useEffect(() => {
    // 监听来自 LangGraph 的 interrupt 事件
    // const unsubscribe = subscribeToInterrupts((data: HITLInterrupt) => {
    //   console.log("[INTERRUPT]", data);
    //   setInterrupt(data);
    //   setFeedback("");
    // });
    // return unsubscribe;
  }, [threadId]);

  const handleApprove = async () => {
    setIsSubmitting(true);
    try {
      // 恢复图执行，传递 "APPROVED"
      await run({
        resume: {
          value: "APPROVED"
        }
      });
      setInterrupt(null);
    } catch (error) {
      console.error("[HITL] 批准失败:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSubmitFeedback = async () => {
    if (!feedback.trim()) return;

    setIsSubmitting(true);
    try {
      // 恢复图执行，传递反馈文本
      await run({
        resume: {
          value: feedback
        }
      });
      setInterrupt(null);
    } catch (error) {
      console.error("[HITL] 反馈提交失败:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!interrupt) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="bg-white rounded-2xl shadow-2xl max-w-5xl max-h-[85vh] overflow-hidden flex flex-col w-full mx-4">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-2xl font-semibold text-gray-800">
            {interrupt.prompt}
          </h2>
          <button
            onClick={() => setInterrupt(null)}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content - 根据 type 渲染不同的审查内容 */}
        <div className="flex-1 overflow-y-auto p-6">
          {interrupt.type === "story_review" && (
            <StoryReviewContent
              enhancedStory={state.enhanced_story}
              characters={state.characters}
            />
          )}

          {interrupt.type === "character_review" && (
            <CharacterReviewContent characters={state.characters} />
          )}

          {interrupt.type === "pages_review" && (
            <PagesReviewContent pages={state.pages} />
          )}
        </div>

        {/* Footer - 反馈输入和操作按钮 */}
        <div className="p-6 border-t border-gray-200 space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700">
              提供反馈（可选）
            </label>
            <Textarea
              placeholder="留空表示批准，或提供具体的修改建议..."
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
              rows={3}
              className="resize-none"
            />
          </div>

          <div className="flex gap-3 justify-end">
            <Button
              onClick={handleSubmitFeedback}
              disabled={!feedback.trim() || isSubmitting}
              variant="outline"
              className="min-w-[120px]"
            >
              发送反馈
            </Button>
            <Button
              onClick={handleApprove}
              disabled={isSubmitting}
              className="bg-green-600 hover:bg-green-700 min-w-[120px]"
            >
              ✓ 批准并继续
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
