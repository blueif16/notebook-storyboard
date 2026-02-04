import { HTMLContainer, ShapeUtil, TLBaseShape, Rectangle2d, RecordProps, T, TLShape } from '@tldraw/tldraw'
import { Page } from '@/types/storybook-state'
import { Loader2, Sparkles, BookOpen } from 'lucide-react'

declare module 'tldraw' {
  export interface TLGlobalShapePropsMap {
    'storybook-page': {
      w: number;
      h: number;
      page: Page;
      isReviewMode?: boolean;
      isStreaming?: boolean;
    }
  }
}

export type IPageShape = TLShape<'storybook-page'>

export class PageShapeUtil extends ShapeUtil<IPageShape> {
  static override type = 'storybook-page' as const

  static override props: RecordProps<IPageShape> = {
    w: T.number,
    h: T.number,
    page: T.object as any,
    isReviewMode: T.boolean.optional(),
    isStreaming: T.boolean.optional(),
  }

  override getDefaultProps(): IPageShape['props'] {
    return {
      w: 400,
      h: 500,
      page: { pageNumber: 1, plot: '', imageUrl: '' },
      isReviewMode: false,
      isStreaming: false
    }
  }

  getGeometry(shape: IPageShape) {
    return new Rectangle2d({
      width: shape.props.w,
      height: shape.props.h,
      isFilled: true
    })
  }

  component(shape: IPageShape) {
    const { page, isReviewMode, isStreaming } = shape.props
    const hasImage = !!page.imageUrl

    // Review mode: show in grid layout with header
    if (isReviewMode) {
      return (
        <HTMLContainer className="pointer-events-all h-full w-full bg-white shadow-2xl rounded-2xl border border-gray-200 flex flex-col overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-green-500 to-teal-500 p-4 text-white">
            <h3 className="text-xl font-bold">页面审查</h3>
            <div className="text-sm opacity-90 mt-1">请在聊天框中批准或提供反馈</div>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-auto p-6">
            <div className="text-sm text-gray-600 mb-4">
              第 {page.pageNumber} 页
              {isStreaming && <span className="ml-2 animate-pulse">生成中...</span>}
            </div>

            <div className="border rounded-lg p-3 bg-white shadow-sm">
              {/* Page Image */}
              {page.imageUrl ? (
                <img
                  src={page.imageUrl}
                  alt={`第 ${page.pageNumber} 页`}
                  className="w-full aspect-video object-cover rounded-lg mb-2"
                />
              ) : (
                <div className="w-full aspect-video bg-gray-100 rounded-lg mb-2 flex items-center justify-center">
                  <Loader2 className="w-6 h-6 animate-spin text-gray-400" />
                </div>
              )}

              {/* Page Info */}
              <div className="text-sm font-semibold mb-1">
                第 {page.pageNumber} 页
              </div>
              {page.plot && (
                <p className="text-xs text-gray-600">
                  {page.plot}
                </p>
              )}
            </div>
          </div>
        </HTMLContainer>
      )
    }

    // Normal mode: single page card
    return (
      <HTMLContainer className="pointer-events-all h-full w-full bg-white shadow-2xl rounded-2xl border border-gray-200 flex flex-col overflow-hidden">
        {/* Page number badge */}
        <div className="absolute top-3 left-3 z-10 bg-black/70 text-white px-3 py-1 rounded-full text-sm font-bold shadow-lg">
          {page.pageNumber}
        </div>
        
        {/* Streaming indicator badge */}
        {isStreaming && !hasImage && (
          <div className="absolute top-3 right-3 z-10 bg-amber-500 text-white px-3 py-1 rounded-full text-xs font-medium flex items-center gap-1.5 shadow-lg">
            <Sparkles className="w-3 h-3" />
            生成中
          </div>
        )}
        
        {/* Page Image */}
        <div className="relative w-full flex-1 bg-gradient-to-br from-amber-50 to-orange-50 overflow-hidden">
          {hasImage ? (
            <img
              src={page.imageUrl}
              alt={`Page ${page.pageNumber}`}
              className="w-full h-full object-cover transition-opacity duration-500"
            />
          ) : (
            <div className="w-full h-full flex flex-col items-center justify-center gap-3">
              {isStreaming ? (
                <>
                  <div className="relative">
                    <div className="absolute inset-0 bg-amber-400/20 rounded-full animate-ping" style={{ animationDuration: '1.5s' }} />
                    <Loader2 className="w-12 h-12 animate-spin text-amber-500 relative z-10" />
                  </div>
                  <span className="text-sm text-gray-500 font-medium">正在绘制...</span>
                </>
              ) : (
                <>
                  <div className="w-16 h-16 rounded-full bg-gray-200 flex items-center justify-center">
                    <BookOpen className="w-8 h-8 text-gray-400" />
                  </div>
                  <span className="text-sm text-gray-400">等待生成</span>
                </>
              )}
            </div>
          )}
          
          {/* Completion checkmark */}
          {hasImage && (
            <div className="absolute bottom-2 right-2 bg-green-500 text-white w-6 h-6 rounded-full flex items-center justify-center shadow-lg">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
          )}
        </div>

        {/* Page Info */}
        <div className="p-4 bg-white border-t border-gray-200">
          {page.plot && (
            <p className="text-sm text-gray-700 line-clamp-3">{page.plot}</p>
          )}
          {!page.plot && (
            <p className="text-sm text-gray-400 italic">暂无剧情描述</p>
          )}
        </div>
      </HTMLContainer>
    )
  }

  indicator(shape: IPageShape) {
    return <rect width={shape.props.w} height={shape.props.h} />
  }
}
