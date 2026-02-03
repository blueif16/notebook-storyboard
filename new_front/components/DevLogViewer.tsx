'use client'
import { useState, useEffect } from 'react'
import { X, ChevronDown, ChevronUp } from 'lucide-react'

interface LogEntry {
  timestamp: string
  level: string
  prefix: string
  message: string
  context?: any
}

export function DevLogViewer() {
  const [isOpen, setIsOpen] = useState(false)
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [isMinimized, setIsMinimized] = useState(false)

  useEffect(() => {
    if (process.env.NODE_ENV !== 'development') return

    // 拦截 console.log
    const originalLog = console.log
    const originalError = console.error
    const originalWarn = console.warn

    const interceptLog = (level: string, originalFn: any) => {
      return (...args: any[]) => {
        originalFn(...args)

        // 解析日志
        const firstArg = args[0]
        if (typeof firstArg === 'string' && firstArg.includes('[')) {
          const match = firstArg.match(/\[([^\]]+)\]/)
          if (match) {
            const prefix = match[1]
            const message = firstArg.replace(/\[([^\]]+)\]/, '').trim()
            const context = args[1]

            setLogs(prev => [...prev.slice(-99), {
              timestamp: new Date().toISOString(),
              level,
              prefix,
              message,
              context
            }])
          }
        }
      }
    }

    console.log = interceptLog('info', originalLog)
    console.error = interceptLog('error', originalError)
    console.warn = interceptLog('warn', originalWarn)

    return () => {
      console.log = originalLog
      console.error = originalError
      console.warn = originalWarn
    }
  }, [])

  if (process.env.NODE_ENV !== 'development') return null

  return (
    <>
      {/* 触发按钮 */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-4 left-4 z-[99998] bg-gray-800 text-white px-4 py-2 rounded-lg shadow-lg hover:bg-gray-700 transition-colors text-sm font-mono"
        >
          📋 Logs ({logs.length})
        </button>
      )}

      {/* 日志面板 */}
      {isOpen && (
        <div className={`fixed left-4 z-[99998] bg-gray-900 text-white rounded-lg shadow-2xl border border-gray-700 flex flex-col transition-all ${
          isMinimized ? 'bottom-4 w-80 h-12' : 'bottom-4 w-[600px] h-[500px]'
        }`}>
          {/* 头部 */}
          <div className="flex items-center justify-between p-3 border-b border-gray-700">
            <h3 className="font-mono text-sm font-bold">开发日志</h3>
            <div className="flex gap-2">
              <button
                onClick={() => setIsMinimized(!isMinimized)}
                className="p-1 hover:bg-gray-700 rounded"
              >
                {isMinimized ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
              </button>
              <button
                onClick={() => setLogs([])}
                className="p-1 hover:bg-gray-700 rounded text-xs"
              >
                清空
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="p-1 hover:bg-gray-700 rounded"
              >
                <X size={16} />
              </button>
            </div>
          </div>

          {/* 日志列表 */}
          {!isMinimized && (
            <div className="flex-1 overflow-y-auto p-3 space-y-2 font-mono text-xs">
              {logs.length === 0 && (
                <div className="text-gray-500 text-center py-10">暂无日志</div>
              )}
              {logs.map((log, idx) => (
                <div key={idx} className="border-l-2 border-gray-700 pl-2 py-1">
                  <div className="flex items-center gap-2">
                    <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                      log.level === 'error' ? 'bg-red-600' :
                      log.level === 'warn' ? 'bg-yellow-600' :
                      'bg-blue-600'
                    }`}>
                      {log.level.toUpperCase()}
                    </span>
                    <span className="text-purple-400 font-bold">[{log.prefix}]</span>
                    <span className="text-gray-400 text-[10px]">
                      {new Date(log.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                  <div className="text-gray-200 mt-1">{log.message}</div>
                  {log.context && (
                    <details className="mt-1">
                      <summary className="text-gray-500 cursor-pointer hover:text-gray-400">
                        查看详情
                      </summary>
                      <pre className="text-gray-400 text-[10px] mt-1 overflow-x-auto bg-gray-800 p-2 rounded">
                        {JSON.stringify(log.context, null, 2)}
                      </pre>
                    </details>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </>
  )
}
