import { Character } from "@/types/storybook-state";
import { Loader2 } from "lucide-react";

interface CharacterReviewContentProps {
  characters: Character[];
}

export function CharacterReviewContent({ characters }: CharacterReviewContentProps) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
      {characters.map((char, i) => (
        <div key={i} className="border rounded-lg p-4 bg-white">
          {/* Character Image */}
          {char.image_url ? (
            <img
              src={char.image_url}
              alt={char.name}
              className="w-full aspect-square object-cover rounded-lg mb-3"
            />
          ) : (
            <div className="w-full aspect-square bg-gray-100 rounded-lg mb-3 flex items-center justify-center">
              <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
            </div>
          )}

          {/* Character Info */}
          <h4 className="font-bold text-lg">{char.name}</h4>
          {char.description && (
            <p className="text-sm text-gray-600 mt-1 line-clamp-3">
              {char.description}
            </p>
          )}
        </div>
      ))}
    </div>
  );
}
