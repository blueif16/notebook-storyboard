"use client";

import { Page } from "@/types/storybook-state";
import { motion } from "framer-motion";
import { BookOpen } from "lucide-react";

interface PageGridProps {
  pages: Page[];
}

export function PageGrid({ pages }: PageGridProps) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
      {pages.map((page, index) => (
        <motion.div
          key={page.image_id}
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: index * 0.05 }}
          className="relative group"
        >
          <div className="relative aspect-[3/4] rounded-lg overflow-hidden bg-white shadow-md border border-blue-200 hover:border-blue-400 transition-all hover:shadow-lg">
            <img
              src={page.image_url}
              alt={`Page ${page.page_number}`}
              className="w-full h-full object-cover"
            />
            <div className="absolute top-2 left-2 bg-blue-600 text-white px-2 py-1 rounded-full text-xs font-bold flex items-center gap-1">
              <BookOpen className="w-3 h-3" />
              {page.page_number}
            </div>
            {page.plot && (
              <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/90 to-transparent p-2 opacity-0 group-hover:opacity-100 transition-opacity">
                <p className="text-white text-xs line-clamp-2">
                  {page.plot}
                </p>
              </div>
            )}
          </div>
        </motion.div>
      ))}
    </div>
  );
}
