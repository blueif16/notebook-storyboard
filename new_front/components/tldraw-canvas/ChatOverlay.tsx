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

  const { messages, sendMessage } = useCopilotChatHeadless_c()
  const displayMessages = (messages || []).filter(msg =>
    msg.content && (typeof msg.content === 'string' ? msg.content.trim() : true)
  )

  // 使用 useLangGraphInterrupt 处理 interrupt
  useLangGraphInterrupt<InterruptData>({
    handler: ({ event, resolve }) => {
      const interruptData = event.value
      logger.info('收到 interrupt 事件', interruptData)

      const { type } = interruptData

      // 只保存 type 和 resolve 函数
      // 文本内容已经通过消息流显示了
      if (type !== 'text') {
        setCurrentInterrupt({ type, resolve })
        logger.info('设置当前 interrupt', { type })
      } else {
        // type="text" 不需要任何交互，直接 resolve
        resolve('CONTINUE')
      }
    }
  })

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
    if (!input.trim()) return

    const messageContent = input
    setInput('')

    logger.info('用户发送消息', {
      content: messageContent,
      threadId
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
      // 使用 resolve 函数恢复执行
      currentInterrupt.resolve('APPROVED')
      logger.info('Approval 已通过 resolve 发送')
    }

    // 清除当前 interrupt
    setCurrentInterrupt(null)
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
                        {/* Agree 按钮 - 只在最后一条 assistant 消息且有 interrupt 时显示 */}
                        {isLastAssistantMessage && currentInterrupt && (
                          <button
                            onClick={handleApprove}
                            className="px-3 py-1 text-xs bg-gray-500 hover:bg-gray-600 text-white rounded-full transition-colors"
                          >
                            Agree
                          </button>
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
          </div>

          <div className="p-4 bg-white border-t border-gray-100">
            <div className="relative">
              <button
                className="absolute left-2 bottom-3 p-1.5 text-gray-400 hover:text-gray-600"
              >
                <Paperclip size={18} />
              </button>
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                placeholder="描述你的故事..."
                className="w-full pl-12 pr-12 py-4 bg-transparent border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-all text-sm"
              />
              <button
                onClick={handleSend}
                className="absolute right-2 bottom-3 p-1.5 text-gray-400 hover:text-blue-600"
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
