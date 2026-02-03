import { HTMLContainer, ShapeUtil, TLBaseShape, Rectangle2d, RecordProps, T, TLShape } from '@tldraw/tldraw'
import { Character } from '@/types/storybook-state'
import { Loader2 } from 'lucide-react'

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
      name: T.string,
      description: T.string.optional(),
      image_id: T.string.optional(),
      image_url: T.string.optional(),
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
              {character.image_url ? (
                <img
                  src={character.image_url}
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
        {/* Character Image */}
        <div className="relative w-full aspect-square bg-gradient-to-br from-purple-100 to-blue-100">
          {character.image_url ? (
            <img
              src={character.image_url}
              alt={character.name}
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center">
              <Loader2 className="w-12 h-12 animate-spin text-gray-400" />
            </div>
          )}
        </div>

        {/* Character Info */}
        <div className="p-4 flex-1 flex flex-col">
          <h3 className="font-bold text-xl text-gray-800 mb-2">{character.name}</h3>
          {character.description && (
            <p className="text-sm text-gray-600 line-clamp-4">{character.description}</p>
          )}
        </div>
      </HTMLContainer>
    )
  }

  indicator(shape: ICharacterShape) {
    return <rect width={shape.props.w} height={shape.props.h} />
  }
}
