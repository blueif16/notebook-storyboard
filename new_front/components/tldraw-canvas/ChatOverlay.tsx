'use client'
import { useState, useRef, useEffect } from 'react'
import { Minimize2, Maximize2, ArrowUp, Copy, ThumbsUp, ThumbsDown, Paperclip } from 'lucide-react'
import { useCopilotChatHeadless_c, useLangGraphInterrupt } from '@copilotkit/react-core'
import { createLogger } from '@/lib/logger'
import Markdown from 'react-markdown'

const logger = createLogger('ChatOverlay')

interface ChatOverlayProps {
  threadId?: string;
}

interface InterruptData {
  type: 'text' | 'enhance_story' | 'generate_images' | 'story_review' | 'character_review' | 'pages_review';
}

export function ChatOverlay({ threadId }: ChatOverlayProps) {
  const [isMinimized, setIsMinimized] = useState(false)
  const [input, setInput] = useState('')
  const scrollRef = useRef<HTMLDivElement>(null)
  const [currentInterrupt, setCurrentInterrupt] = useState<{
    type: string;
    resolve: (response: any) => void;
  } | null>(null)
  const [approvedMessageIndices, setApprovedMessageIndices] = useState<Set<number>>(new Set())

  const { messages, sendMessage, isLoading } = useCopilotChatHeadless_c()
  const displayMessages = (messages || []).filter(msg =>
    msg.content && (typeof msg.content === 'string' ? msg.content.trim() : true)
  )

  // Handle ONLY non-text interrupts (story_review, character_review, pages_review)
  // Text interrupts are handled naturally by the chat flow - user's next message resumes the graph.
  //
  // IMPORTANT: Using `enabled` to filter out text interrupts prevents CopilotKit from
  // auto-triggering new runs when we don't call resolve().
  //
  useLangGraphInterrupt<InterruptData>({
    enabled: ({ eventValue }) => {
      // Only handle non-text interrupts
      const shouldHandle = eventValue?.type !== 'text'
      logger.info('useLangGraphInterrupt enabled check', {
        type: eventValue?.type,
        enabled: shouldHandle
      })
      return shouldHandle
    },
    handler: ({ event, resolve }) => {
      const interruptData = event.value
      logger.info('收到需要处理的 interrupt 事件', interruptData)

      const { type } = interruptData

      // Store the resolve function so we can show approval UI
      setCurrentInterrupt({ type, resolve })
      logger.info('设置当前 interrupt (需要用户批准)', { type })
    }
  })

  // 监听 currentInterrupt 变化
  useEffect(() => {
    logger.info('currentInterrupt 状态变化', {
      hasInterrupt: currentInterrupt !== null,
      type: currentInterrupt?.type,
      messagesCount: displayMessages.length
    })
  }, [currentInterrupt, displayMessages.length])

  // 监听消息变化
  useEffect(() => {
    if (displayMessages.length > 0) {
      const lastMessage = displayMessages[displayMessages.length - 1]
      logger.info('收到新消息', {
        messageCount: displayMessages.length,
        lastMessage: {
          role: lastMessage.role,
          content: lastMessage.content,
          type: typeof lastMessage
        }
      })
    }
  }, [displayMessages])

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [displayMessages, currentInterrupt, isMinimized])

  const handleSend = async () => {
    // Guard: Don't send if empty or already loading
    if (!input.trim() || isLoading) {
      if (isLoading) {
        logger.warn('已阻止发送 - 上一个请求仍在进行中')
      }
      return
    }

    const messageContent = input
    setInput('')

    logger.info('用户发送消息', {
      content: messageContent,
      threadId,
      isLoading
    })

    try {
      await sendMessage({
        id: `msg-${Date.now()}`,
        role: 'user',
        content: messageContent,
      })
      logger.info('消息已发送到 CopilotKit')
    } catch (error) {
      logger.error('发送消息失败', { error })
    }
  }

  const handleApprove = async () => {
    logger.info('用户点击 Agree')

    if (currentInterrupt?.resolve) {
      // 记录当前最后一条 assistant 消息的索引
      const lastAssistantIndex = displayMessages.length - 1
      setApprovedMessageIndices(prev => new Set(prev).add(lastAssistantIndex))

      currentInterrupt.resolve('APPROVED')
      logger.info('Approval 已通过 resolve 发送', { messageIndex: lastAssistantIndex })

      setCurrentInterrupt(null)
    }
  }

  return (
    <div
      className={`absolute right-6 top-6 transition-all duration-300 ease-in-out shadow-2xl border border-gray-200 bg-white/95 backdrop-blur rounded-xl flex flex-col overflow-hidden z-[99999]
        ${isMinimized ? 'h-16 w-16 rounded-full cursor-pointer' : 'bottom-6 w-[400px]'}
      `}
    >
      <div
        className={`flex items-center justify-between p-4 border-b border-gray-100 ${isMinimized && 'h-full justify-center border-0'}`}
        onClick={() => isMinimized && setIsMinimized(false)}
      >
        {!isMinimized && <h2 className="font-semibold text-gray-800">Agent Chat</h2>}
        <button
          onClick={(e) => { e.stopPropagation(); setIsMinimized(!isMinimized); }}
          className="p-2 hover:bg-gray-100 rounded-lg text-gray-500 transition-colors"
        >
          {isMinimized ? <Maximize2 size={18}/> : <Minimize2 size={18}/>}
        </button>
      </div>

      {!isMinimized && (
        <>
          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50/50" ref={scrollRef}>
            {displayMessages.length === 0 && (
              <div className="text-center text-gray-400 text-sm mt-10">
                <p>告诉我你的故事创意...</p>
              </div>
            )}

            {displayMessages.map((msg: any, idx: number) => {
              const isLastAssistantMessage = msg.role === 'assistant' && idx === displayMessages.length - 1
              const isApproved = approvedMessageIndices.has(idx)
              const hasActiveInterrupt = isLastAssistantMessage && currentInterrupt !== null

              return (
                <div key={msg.id || idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  {msg.role === 'user' ? (
                    <div className="max-w-[85%] rounded-2xl p-3 text-sm bg-gray-200 text-gray-800 rounded-tr-none">
                      {typeof msg.content === 'string' ? msg.content : JSON.stringify(msg.content)}
                    </div>
                  ) : (
                    <div className="max-w-[85%]">
                      <div className="text-sm text-gray-800 mb-2 prose prose-sm max-w-none">
                        {typeof msg.content === 'string' ? (
                          <Markdown>{msg.content}</Markdown>
                        ) : (
                          JSON.stringify(msg.content)
                        )}
                      </div>

                      <div className="flex gap-2 mt-2">
                        {/* Agree 按钮 - 显示当前状态或已批准状态 */}
                        {hasActiveInterrupt && (
                          <button
                            onClick={handleApprove}
                            className="px-3 py-1 text-xs bg-gray-500 hover:bg-gray-600 text-white rounded-full transition-colors"
                          >
                            Agree
                          </button>
                        )}
                        {isApproved && (
                          <div className="px-3 py-1 text-xs bg-green-500 text-white rounded-full">
                            ✓ Approved
                          </div>
                        )}

                        <button
                          onClick={() => navigator.clipboard.writeText(typeof msg.content === 'string' ? msg.content : JSON.stringify(msg.content))}
                          className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
                        >
                          <Copy size={14} />
                        </button>
                        <button className="p-1 text-gray-400 hover:text-gray-600 transition-colors">
                          <ThumbsUp size={14} />
                        </button>
                        <button className="p-1 text-gray-400 hover:text-gray-600 transition-colors">
                          <ThumbsDown size={14} />
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              )
            })}

            {/* 加载指示器 - unified loading state from CopilotKit */}
            {isLoading && (
              <div className="flex justify-start">
                <div className="max-w-[85%]">
                  <div className="flex items-center gap-1 text-gray-400">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                  </div>
                </div>
              </div>
            )}
          </div>

          <div className="p-4 bg-white border-t border-gray-100">
            <div className="relative">
              <button
                className="absolute left-2 bottom-3 p-1.5 text-gray-400 hover:text-gray-600 disabled:opacity-50"
                disabled={isLoading}
              >
                <Paperclip size={18} />
              </button>
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && !isLoading && handleSend()}
                placeholder={isLoading ? "正在处理..." : "描述你的故事..."}
                disabled={isLoading}
                className="w-full pl-12 pr-12 py-4 bg-transparent border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-all text-sm disabled:opacity-50 disabled:cursor-not-allowed"
              />
              <button
                onClick={handleSend}
                disabled={isLoading || !input.trim()}
                className="absolute right-2 bottom-3 p-1.5 text-gray-400 hover:text-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <ArrowUp size={18} />
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
