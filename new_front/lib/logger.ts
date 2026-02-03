/**
 * 统一日志工具
 * 用于追踪用户操作、前后端通信和状态更新
 */

type LogLevel = 'info' | 'warn' | 'error' | 'debug'

interface LogContext {
  timestamp: string
  [key: string]: any
}

class Logger {
  private prefix: string

  constructor(prefix: string) {
    this.prefix = prefix
  }

  private formatLog(level: LogLevel, message: string, context?: any) {
    const logContext: LogContext = {
      timestamp: new Date().toISOString(),
      ...context
    }

    const style = this.getStyle(level)
    console.log(
      `%c[${this.prefix}]%c ${message}`,
      style,
      'color: inherit',
      logContext
    )
  }

  private getStyle(level: LogLevel): string {
    switch (level) {
      case 'info':
        return 'color: #3b82f6; font-weight: bold'
      case 'warn':
        return 'color: #f59e0b; font-weight: bold'
      case 'error':
        return 'color: #ef4444; font-weight: bold'
      case 'debug':
        return 'color: #8b5cf6; font-weight: bold'
      default:
        return 'color: inherit'
    }
  }

  info(message: string, context?: any) {
    this.formatLog('info', message, context)
  }

  warn(message: string, context?: any) {
    this.formatLog('warn', message, context)
  }

  error(message: string, context?: any) {
    this.formatLog('error', message, context)
  }

  debug(message: string, context?: any) {
    this.formatLog('debug', message, context)
  }
}

export const createLogger = (prefix: string) => new Logger(prefix)
