"use client";

import { Character } from "@/types/storybook-state";
import { motion, AnimatePresence } from "framer-motion";

interface CharactersPanelProps {
  characters: Character[];
}

export function CharactersPanel({ characters }: CharactersPanelProps) {
  if (characters.length === 0) return null;

  return (
    <div className="fixed top-20 left-4 bg-white/90 backdrop-blur-sm rounded-2xl p-4 shadow-lg max-w-xs z-40">
      <h3 className="text-lg font-semibold mb-3">角色</h3>

      <div className="space-y-2">
        <AnimatePresence>
          {characters.map((char, i) => (
            <motion.div
              key={char.name}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.2 }}
              className="flex items-center gap-3 p-2 rounded-lg hover:bg-gray-50 transition-colors"
            >
              {/* Portrait thumbnail - 生成后出现 */}
              {char.image_url ? (
                <img
                  src={char.image_url}
                  alt={char.name}
                  className="w-12 h-12 rounded-full object-cover"
                />
              ) : (
                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-purple-200 to-blue-200 animate-pulse" />
              )}

              <div className="flex-1 min-w-0">
                <div className="font-medium truncate">{char.name}</div>
                {char.description && (
                  <div className="text-xs text-gray-500 truncate">
                    {char.description}
                  </div>
                )}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
}
