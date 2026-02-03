"use client";

import { Character } from "@/types/storybook-state";
import { motion } from "framer-motion";

interface CharacterGridProps {
  characters: Character[];
}

export function CharacterGrid({ characters }: CharacterGridProps) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
      {characters.map((char, index) => (
        <motion.div
          key={char.image_id}
          initial={{ opacity: 0, scale: 0.8, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          transition={{ delay: index * 0.1 }}
          className="relative group"
        >
          <div className="relative aspect-square rounded-xl overflow-hidden bg-white shadow-lg border-2 border-purple-200 hover:border-purple-400 transition-all hover:shadow-xl">
            <img
              src={char.image_url}
              alt={char.name}
              className="w-full h-full object-cover"
            />
            <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-3">
              <p className="text-white font-semibold text-sm truncate">
                {char.name}
              </p>
              {char.description && (
                <p className="text-white/80 text-xs truncate">
                  {char.description}
                </p>
              )}
            </div>
          </div>
        </motion.div>
      ))}
    </div>
  );
}
