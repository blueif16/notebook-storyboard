'use client'

import { useState, useEffect } from 'react'
import { Tldraw, Editor } from '@tldraw/tldraw'
import '@tldraw/tldraw/tldraw.css'
import { useCoAgent } from '@copilotkit/react-core'
import { ChatOverlay } from '@/components/tldraw-canvas/ChatOverlay'
import { MarkdownShapeUtil } from '@/components/tldraw-canvas/MarkdownShape'
import { CharacterShapeUtil } from '@/components/tldraw-canvas/CharacterShape'
import { PageShapeUtil } from '@/components/tldraw-canvas/PageShape'
import { StoryReviewShapeUtil } from '@/components/tldraw-canvas/StoryReviewShape'
import { HITLModal } from '@/components/storybook/HITLModal'
import { StorybookState, initialStorybookState } from '@/types/storybook-state'
import { createLogger } from '@/lib/logger'
import { DevLogViewer } from '@/components/DevLogViewer'

const logger = createLogger('Page')

const customShapeUtils = [
  MarkdownShapeUtil,
  CharacterShapeUtil,
  PageShapeUtil,
  StoryReviewShapeUtil
]

export default function Home() {
  const [editor, setEditor] = useState<Editor | null>(null)
  const [threadId, setThreadId] = useState<string>("")

  useEffect(() => {
    setThreadId(`storybook-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`)
  }, [])

  // Agent State - auto-synced with backend
  const { state } = useCoAgent<StorybookState>({
    name: "storybook_agent",
    initialState: initialStorybookState,
    ...(threadId && { threadId }),
  })

  // Log state changes for debugging
  useEffect(() => {
    logger.info('Agent 状态更新', {
      threadId,
      state: {
        currentStage: state.currentStage,
        reviewType: state.reviewType,
        isStreaming: state.isStreaming,
        enhancedStoryPartial: state.enhancedStoryPartial?.substring(0, 50),
        charactersPartialCount: state.charactersPartial?.length || 0,
        charactersCount: state.characters?.length || 0,
        pagesCount: state.pages?.length || 0,
        enhancedStory: state.enhancedStory ? '已生成' : '未生成',
        storybookId: state.storybookId,
        portraitGeneratingIndex: state.portraitGeneratingIndex,
      }
    })
  }, [state, threadId])

  return (
    <div className="fixed inset-0 overflow-hidden bg-gray-50">
      <div className="absolute inset-0 z-0">
        <Tldraw
          shapeUtils={customShapeUtils}
          hideUi={false}
          onMount={(editor) => {
            setEditor(editor)
            
            // Set initial camera position
            editor.setCamera({ x: 0, y: 0, z: 1 })
          }}
        />
      </div>

      <ChatOverlay threadId={threadId} />
      <HITLModal state={state} threadId={threadId} editor={editor} />
      <DevLogViewer />
    </div>
  )
}
