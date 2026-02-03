import { HTMLContainer, ShapeUtil, TLBaseShape, Rectangle2d, RecordProps, T, TLShape } from '@tldraw/tldraw'
import { Page } from '@/types/storybook-state'
import { Loader2 } from 'lucide-react'

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
      page: { page_number: 1, plot: '', image_url: '' },
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
              第 {page.page_number} 页
              {isStreaming && <span className="ml-2 animate-pulse">生成中...</span>}
            </div>

            <div className="border rounded-lg p-3 bg-white shadow-sm">
              {/* Page Image */}
              {page.image_url ? (
                <img
                  src={page.image_url}
                  alt={`第 ${page.page_number} 页`}
                  className="w-full aspect-video object-cover rounded-lg mb-2"
                />
              ) : (
                <div className="w-full aspect-video bg-gray-100 rounded-lg mb-2 flex items-center justify-center">
                  <Loader2 className="w-6 h-6 animate-spin text-gray-400" />
                </div>
              )}

              {/* Page Info */}
              <div className="text-sm font-semibold mb-1">
                第 {page.page_number} 页
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
        {/* Page Image */}
        <div className="relative w-full flex-1 bg-gradient-to-br from-amber-50 to-orange-50">
          {page.image_url ? (
            <img
              src={page.image_url}
              alt={`Page ${page.page_number}`}
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center">
              <Loader2 className="w-12 h-12 animate-spin text-gray-400" />
            </div>
          )}
        </div>

        {/* Page Info */}
        <div className="p-4 bg-white border-t border-gray-200">
          <div className="text-sm font-bold text-gray-500 mb-2">
            Page {page.page_number}
          </div>
          {page.plot && (
            <p className="text-sm text-gray-700 line-clamp-3">{page.plot}</p>
          )}
        </div>
      </HTMLContainer>
    )
  }

  indicator(shape: IPageShape) {
    return <rect width={shape.props.w} height={shape.props.h} />
  }
}
