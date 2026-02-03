import ReactMarkdown from "react-markdown";
import { Character } from "@/types/storybook-state";

interface StoryReviewContentProps {
  enhancedStory?: string;
  characters: Character[];
}

export function StoryReviewContent({
  enhancedStory,
  characters
}: StoryReviewContentProps) {
  return (
    <div className="space-y-6">
      {/* Enhanced Story as Markdown */}
      <div className="prose prose-lg max-w-none bg-amber-50 rounded-lg p-6">
        <h3 className="text-xl font-semibold mb-4">增强后的故事</h3>
        <ReactMarkdown>
          {enhancedStory || "*故事生成中...*"}
        </ReactMarkdown>
      </div>

      {/* Character List */}
      <div className="bg-blue-50 rounded-lg p-6">
        <h3 className="text-xl font-semibold mb-4">
          角色 ({characters.length})
        </h3>
        <div className="space-y-3">
          {characters.map((char, i) => (
            <div key={i} className="bg-white rounded-lg p-4">
              <h4 className="font-bold text-lg">{char.name}</h4>
              {char.description && (
                <p className="text-gray-600 mt-1">{char.description}</p>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
