import { HTMLContainer, ShapeUtil, useIsEditing, Rectangle2d, RecordProps, T, TLShape } from '@tldraw/tldraw'
import ReactMarkdown from 'react-markdown'

declare module 'tldraw' {
  export interface TLGlobalShapePropsMap {
    'markdown-window': {
      w: number;
      h: number;
      content: string;
      title: string;
    }
  }
}

export type IMarkdownShape = TLShape<'markdown-window'>

export class MarkdownShapeUtil extends ShapeUtil<IMarkdownShape> {
  static override type = 'markdown-window' as const

  static override props: RecordProps<IMarkdownShape> = {
    w: T.number,
    h: T.number,
    content: T.string,
    title: T.string,
  }

  override getDefaultProps(): IMarkdownShape['props'] {
    return { w: 400, h: 500, content: '# 无标题', title: '文档' }
  }

  getGeometry(shape: IMarkdownShape) {
    return new Rectangle2d({
      width: shape.props.w,
      height: shape.props.h,
      isFilled: true
    })
  }

  component(shape: IMarkdownShape) {
    const isEditing = useIsEditing(shape.id)

    return (
      <HTMLContainer className="pointer-events-all h-full w-full bg-white shadow-xl rounded-lg border border-gray-200 flex flex-col overflow-hidden">
        <div className="bg-gray-50 p-3 border-b border-gray-200 flex items-center gap-2 select-none">
          <div className="flex gap-1.5">
            <div className="w-3 h-3 rounded-full bg-red-400/80" />
            <div className="w-3 h-3 rounded-full bg-yellow-400/80" />
            <div className="w-3 h-3 rounded-full bg-green-400/80" />
          </div>
          <span className="text-xs font-semibold text-gray-500 ml-2 uppercase tracking-wide">
            {shape.props.title}
          </span>
        </div>

        <div className="flex-1 overflow-auto p-5 prose prose-sm max-w-none">
          <ReactMarkdown>{shape.props.content}</ReactMarkdown>
        </div>
      </HTMLContainer>
    )
  }

  indicator(shape: IMarkdownShape) {
    return <rect width={shape.props.w} height={shape.props.h} />
  }
}
