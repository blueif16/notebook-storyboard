import { HTMLContainer, ShapeUtil, TLBaseShape, Rectangle2d, RecordProps, T, TLShape } from '@tldraw/tldraw'
import { Character } from '@/types/storybook-state'
import { Loader2, Sparkles } from 'lucide-react'

declare module 'tldraw' {
  export interface TLGlobalShapePropsMap {
    'character-card': {
      w: number;
      h: number;
      character: Character;
      isReviewMode?: boolean;
      isStreaming?: boolean;
    }
  }
}

export type ICharacterShape = TLShape<'character-card'>

export class CharacterShapeUtil extends ShapeUtil<ICharacterShape> {
  static override type = 'character-card' as const

  static override props: RecordProps<ICharacterShape> = {
    w: T.number,
    h: T.number,
    character: T.object({
      index: T.number.optional(),
      name: T.string,
      description: T.string.optional(),
      imageId: T.string.optional(),
      imageUrl: T.string.optional(),
    }),
    isReviewMode: T.boolean.optional(),
    isStreaming: T.boolean.optional(),
  }

  override getDefaultProps(): ICharacterShape['props'] {
    return {
      w: 280,
      h: 380,
      character: { name: 'Unknown', description: '' },
      isReviewMode: false,
      isStreaming: false
    }
  }

  getGeometry(shape: ICharacterShape) {
    return new Rectangle2d({
      width: shape.props.w,
      height: shape.props.h,
      isFilled: true
    })
  }

  component(shape: ICharacterShape) {
    const { character, isReviewMode, isStreaming } = shape.props
    const hasImage = !!character.imageUrl

    // Review mode: show in grid layout with header
    if (isReviewMode) {
      return (
        <HTMLContainer className="pointer-events-all h-full w-full bg-white shadow-2xl rounded-2xl border border-gray-200 flex flex-col overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-500 to-purple-500 p-4 text-white">
            <h3 className="text-xl font-bold">角色审查</h3>
            <div className="text-sm opacity-90 mt-1">请在聊天框中批准或提供反馈</div>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-auto p-6">
            {isStreaming && (
              <div className="mb-4 text-sm text-gray-500 animate-pulse">
                角色生成中...
              </div>
            )}
            <div className="border rounded-lg p-4 bg-white shadow-sm">
              {/* Character Image */}
              {character.imageUrl ? (
                <img
                  src={character.imageUrl}
                  alt={character.name}
                  className="w-full aspect-square object-cover rounded-lg mb-3"
                />
              ) : (
                <div className="w-full aspect-square bg-gray-100 rounded-lg mb-3 flex items-center justify-center">
                  <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
                </div>
              )}

              {/* Character Info */}
              <h4 className="font-bold text-lg">{character.name}</h4>
              {character.description && (
                <p className="text-sm text-gray-600 mt-1">{character.description}</p>
              )}
            </div>
          </div>
        </HTMLContainer>
      )
    }

    // Normal mode: single character card
    return (
      <HTMLContainer className="pointer-events-all h-full w-full bg-white shadow-2xl rounded-2xl border border-gray-200 flex flex-col overflow-hidden">
        {/* Character name badge */}
        <div className="absolute top-3 left-3 z-10 bg-black/70 text-white px-3 py-1 rounded-full text-sm font-bold shadow-lg max-w-[calc(100%-60px)] truncate">
          {character.name}
        </div>
        
        {/* Streaming indicator badge */}
        {isStreaming && !hasImage && (
          <div className="absolute top-3 right-3 z-10 bg-blue-500 text-white px-3 py-1 rounded-full text-xs font-medium flex items-center gap-1.5 shadow-lg">
            <Sparkles className="w-3 h-3" />
            生成中
          </div>
        )}
        
        {/* Character Image */}
        <div className="relative w-full aspect-square bg-gradient-to-br from-purple-100 to-blue-100 overflow-hidden">
          {hasImage ? (
            <img
              src={character.imageUrl}
              alt={character.name}
              className="w-full h-full object-cover transition-opacity duration-500"
              style={{ opacity: 1 }}
            />
          ) : (
            <div className="w-full h-full flex flex-col items-center justify-center gap-3">
              {isStreaming ? (
                <>
                  <div className="relative">
                    <div className="absolute inset-0 bg-blue-400/20 rounded-full animate-ping" style={{ animationDuration: '1.5s' }} />
                    <Loader2 className="w-12 h-12 animate-spin text-blue-500 relative z-10" />
                  </div>
                  <span className="text-sm text-gray-500 font-medium">正在绘制...</span>
                </>
              ) : (
                <>
                  <div className="w-16 h-16 rounded-full bg-gray-200 flex items-center justify-center">
                    <span className="text-2xl">🎨</span>
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

        {/* Character Info */}
        <div className="p-4 flex-1 flex flex-col">
          {character.description && (
            <p className="text-sm text-gray-600 line-clamp-4">{character.description}</p>
          )}
          {!character.description && (
            <p className="text-sm text-gray-400 italic">暂无描述</p>
          )}
        </div>
      </HTMLContainer>
    )
  }

  indicator(shape: ICharacterShape) {
    return <rect width={shape.props.w} height={shape.props.h} />
  }
}
