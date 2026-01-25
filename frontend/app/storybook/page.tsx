"use client";

import { useCoAgent, useCoAgentStateRender, useLangGraphInterrupt } from "@copilotkit/react-core";
import { CopilotChat } from "@copilotkit/react-ui";
import { StorybookState, initialStorybookState, UserInputInterrupt } from "@/types/storybook-state";
import { CharacterGrid } from "@/components/storybook/CharacterGrid";
import { PageGrid } from "@/components/storybook/PageGrid";
import { ProgressIndicator } from "@/components/storybook/ProgressIndicator";
import { InterruptCard } from "@/components/storybook/InterruptCard";

export default function StorybookPage() {
  const { state } = useCoAgent<StorybookState>({
    name: "storybookAgent",
    initialState: initialStorybookState,
  });

  // Render state updates in chat
  useCoAgentStateRender({
    name: "storybookAgent",
    render: ({ state }) => {
      // Show character grid when characters are generated
      if (state.stage === "characters_generated" && state.characters.length > 0) {
        return (
          <div className="my-4 p-4 bg-gradient-to-br from-purple-50 to-pink-50 rounded-lg border-2 border-purple-200">
            <h3 className="text-lg font-semibold text-purple-900 mb-3">
              ✨ Characters Created ({state.characters.length})
            </h3>
            <CharacterGrid characters={state.characters} />
          </div>
        );
      }

      // Show page grid during generation
      if ((state.stage === "generating_pages" || state.stage === "complete") && state.pages.length > 0) {
        return (
          <div className="my-4 p-4 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg border-2 border-blue-200">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-lg font-semibold text-blue-900">
                📖 Pages Generated ({state.pages.length})
              </h3>
              {state.stage === "complete" && state.storybook_id && (
                <a
                  href={`/library/storybook/${state.storybook_id}`}
                  className="text-sm text-blue-600 hover:text-blue-800 hover:underline font-medium"
                >
                  View Storybook →
                </a>
              )}
            </div>
            <PageGrid pages={state.pages} />
          </div>
        );
      }

      // Show progress for other stages
      if (state.stage !== "idle" && state.stage !== "complete") {
        return (
          <div className="my-4">
            <ProgressIndicator 
              stage={state.stage} 
              progress={state.progress}
              charactersCount={state.characters_count}
              pagesCount={state.pages_count}
            />
          </div>
        );
      }

      return null;
    },
  });

  // Handle HITL interrupts
  useLangGraphInterrupt<UserInputInterrupt>({
    render: ({ event, resolve }) => {
      const data = event.value;
      
      return (
        <InterruptCard
          question={data.question}
          images={data.images}
          onSubmit={(response) => resolve(response)}
        />
      );
    },
  });

  return (
    <div className="flex h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50">
      <div className="flex-1 flex flex-col">
        <header className="p-6 border-b border-purple-200 bg-white/80 backdrop-blur-sm">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
            ✨ AI Storybook Creator
          </h1>
          <p className="text-sm text-gray-600 mt-1">
            Describe your story and I'll bring it to life with illustrations
          </p>
        </header>
        
        <div className="flex-1 overflow-hidden">
          <CopilotChat
            className="h-full"
            labels={{
              initial: "Hi! I'm your AI storybook creator. Tell me a story and I'll illustrate it!\n\nExample: \"Create a magical story about a brave mouse exploring a mysterious forest\"",
              placeholder: "Describe your story...",
            }}
          />
        </div>
      </div>
    </div>
  );
}
