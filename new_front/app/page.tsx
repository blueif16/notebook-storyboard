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

  // 监听 state 变化
  useEffect(() => {
    logger.info('Agent 状态更新', {
      threadId,
      state: {
        current_stage: state.current_stage,
        review_type: state.review_type,
        enhanced_story_partial: state.enhanced_story_partial?.substring(0, 50),
        characters_partial_count: state.characters_partial?.length || 0,
        characters_count: state.characters?.length || 0,
        pages_count: state.pages?.length || 0,
        enhanced_story: state.enhanced_story ? '已生成' : '未生成',
        storybook_id: state.storybook_id,
        full_state: state
      }
    })
  }, [state, threadId])

  // 监听 state 变化，动态创建 shapes
  useEffect(() => {
    if (!editor) return

    logger.debug('检查 shapes 更新', {
      stage: state.current_stage,
      characters: state.characters?.length || 0,
      pages: state.pages?.length || 0,
    })

    // 创建角色卡片
    if (state.characters?.length > 0) {
      state.characters.forEach((character: any, index: number) => {
        const shapeId = `shape:character-${character.name}` as any
        const existingShape = editor.getShape(shapeId)

        if (!existingShape) {
          editor.createShape({
            id: shapeId,
            type: 'character-card' as any,
            x: 100 + index * 320,
            y: 100,
            props: { character }
          })
        } else {
          editor.updateShape({
            id: shapeId,
            type: 'character-card' as any,
            props: { character }
          })
        }
      })
    }

    // 创建页面卡片
    if (state.pages?.length > 0) {
      state.pages.forEach((page: any, index: number) => {
        const shapeId = `shape:page-${page.page_number}` as any
        const existingShape = editor.getShape(shapeId)

        if (!existingShape) {
          editor.createShape({
            id: shapeId,
            type: 'storybook-page' as any,
            x: 100 + (index % 3) * 450,
            y: 600 + Math.floor(index / 3) * 550,
            props: { page }
          })
        } else {
          editor.updateShape({
            id: shapeId,
            type: 'storybook-page' as any,
            props: { page }
          })
        }
      })
    }

    // 创建故事审查卡片
    if (state.enhanced_story && state.current_stage === 'enhance') {
      const shapeId = 'shape:story-review' as any
      const existingShape = editor.getShape(shapeId)

      if (!existingShape) {
        editor.createShape({
          id: shapeId,
          type: 'story-review' as any,
          x: 800,
          y: 100,
          props: {
            enhancedStory: state.enhanced_story,
            characters: state.characters
          }
        })
      } else {
        editor.updateShape({
          id: shapeId,
          type: 'story-review' as any,
          props: {
            enhancedStory: state.enhanced_story,
            characters: state.characters
          }
        })
      }
    }
  }, [editor, state])

  return (
    <div className="fixed inset-0 overflow-hidden bg-gray-50">
      <div className="absolute inset-0 z-0">
        <Tldraw
          shapeUtils={customShapeUtils}
          hideUi={false}
          onMount={(editor) => {
            setEditor(editor)
          }}
        />
      </div>

      <ChatOverlay threadId={threadId} />
      <HITLModal state={state} threadId={threadId} editor={editor} />
      <DevLogViewer />
    </div>
  )
}
