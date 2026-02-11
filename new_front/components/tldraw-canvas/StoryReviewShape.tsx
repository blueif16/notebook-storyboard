import { HTMLContainer, ShapeUtil, Rectangle2d, T, RecordProps, TLShape } from '@tldraw/tldraw'
import ReactMarkdown from 'react-markdown'

declare module 'tldraw' {
  export interface TLGlobalShapePropsMap {
    'story-review': {
      w: number;
      h: number;
      enhancedStory?: string;
      enhancedStoryPartial?: string;
      characters: Array<{
        index?: number;
        name: string;
        description?: string;
        imageId?: string;
        imageUrl?: string;
      }>;
      isStreaming: boolean;
    }
  }
}

export type IStoryReviewShape = TLShape<'story-review'>

export class StoryReviewShapeUtil extends ShapeUtil<IStoryReviewShape> {
  static override type = 'story-review' as const

  static override props: RecordProps<IStoryReviewShape> = {
    w: T.number,
    h: T.number,
    enhancedStory: T.string.optional(),
    enhancedStoryPartial: T.string.optional(),
    characters: T.arrayOf(T.object({
      index: T.number.optional(),
      name: T.string,
      description: T.string.optional(),
      imageId: T.string.optional(),
      imageUrl: T.string.optional(),
    })),
    isStreaming: T.boolean,
  }

  override getDefaultProps(): IStoryReviewShape['props'] {
    return {
      w: 1000,
      h: 700,
      enhancedStory: '',
      enhancedStoryPartial: '',
      characters: [],
      isStreaming: false
    }
  }

  getGeometry(shape: IStoryReviewShape) {
    return new Rectangle2d({
      width: shape.props.w,
      height: shape.props.h,
      isFilled: true
    })
  }

  component(shape: IStoryReviewShape) {
    const { enhancedStory, enhancedStoryPartial, characters, isStreaming } = shape.props
    const displayStory = enhancedStory || enhancedStoryPartial

    return (
      <HTMLContainer className="pointer-events-all h-full w-full bg-white shadow-lg rounded-lg border border-gray-300 flex flex-col overflow-hidden">
        <div className="flex-1 overflow-auto p-12 space-y-8">
          {/* Enhanced Story */}
          <div className="prose prose-lg max-w-none">
            <div className="flex items-center justify-between mb-6 pb-4 border-b border-gray-200">
              <h3 className="text-2xl font-serif font-bold text-black">完整故事</h3>
              {/* {isStreaming && (
                <span className="text-sm text-gray-400 animate-pulse">生成中...</span>
              )} */}
            </div>
            <div className="text-black leading-relaxed">
              <ReactMarkdown>{displayStory || "*故事生成中...*"}</ReactMarkdown>
              {isStreaming && <span className="animate-pulse">▊</span>}
            </div>
          </div>

          {/* Characters */}
          {characters.length > 0 && (
            <div className="pt-6 border-t border-gray-200">
              <h3 className="text-2xl font-serif font-bold text-black mb-6">
                角色 ({characters.length})
              </h3>
              <div className="space-y-4">
                {characters.map((char, i) => (
                  <div key={i} className="border-l-4 border-gray-300 pl-6 py-2">
                    <h4 className="font-semibold text-xl text-black mb-2">{char.name}</h4>
                    {char.description && (
                      <p className="text-gray-700 leading-relaxed">{char.description}</p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </HTMLContainer>
    )
  }

  indicator(shape: IStoryReviewShape) {
    return <rect width={shape.props.w} height={shape.props.h} />
  }
}
