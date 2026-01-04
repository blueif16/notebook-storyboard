"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useState } from "react";
import { ChevronLeft, ChevronRight, BookOpen } from "lucide-react";
import { Button } from "@/components/ui/button";

interface StoryPage {
  leftImage?: string;
  rightImage?: string;
  leftText?: string;
  rightText?: string;
}

interface StoryBookProps {
  pages: StoryPage[];
  title?: string;
}

export function StoryBook({ pages, title = "Story Book" }: StoryBookProps) {
  const [currentSpread, setCurrentSpread] = useState(0);
  const [direction, setDirection] = useState(0);

  const totalSpreads = Math.ceil(pages.length / 2);

  const paginate = (dir: number) => {
    const newSpread = currentSpread + dir;
    if (newSpread >= 0 && newSpread < totalSpreads) {
      setDirection(dir);
      setCurrentSpread(newSpread);
    }
  };

  const leftPageIndex = currentSpread * 2;
  const rightPageIndex = currentSpread * 2 + 1;
  const leftPage = pages[leftPageIndex];
  const rightPage = pages[rightPageIndex];

  return (
    <div className="w-full h-full flex flex-col items-center justify-center p-4 bg-gradient-to-br from-amber-50 to-orange-50">
      {/* Title */}
      <div className="flex items-center gap-2 mb-6">
        <BookOpen className="w-6 h-6 text-amber-700" />
        <h2 className="text-2xl font-serif font-bold text-amber-900">{title}</h2>
      </div>

      {/* Book Container */}
      <div className="relative w-full max-w-5xl aspect-[2/1] perspective-[2000px]">
        <AnimatePresence mode="wait" custom={direction}>
          <motion.div
            key={currentSpread}
            custom={direction}
            initial={{ rotateY: direction > 0 ? -15 : 15, opacity: 0 }}
            animate={{ rotateY: 0, opacity: 1 }}
            exit={{ rotateY: direction > 0 ? 15 : -15, opacity: 0 }}
            transition={{ duration: 0.6, ease: "easeInOut" }}
            className="absolute inset-0 flex shadow-2xl rounded-lg overflow-hidden"
            style={{ transformStyle: "preserve-3d" }}
          >
            {/* Left Page */}
            <div className="w-1/2 bg-white border-r-2 border-amber-200 p-8 flex flex-col">
              {leftPage?.leftImage && (
                <div className="flex-1 mb-4 rounded-md overflow-hidden shadow-md">
                  <img
                    src={leftPage.leftImage}
                    alt="Left page"
                    className="w-full h-full object-cover"
                  />
                </div>
              )}
              {leftPage?.leftText && (
                <div className="text-gray-800 font-serif leading-relaxed text-sm overflow-y-auto">
                  {leftPage.leftText}
                </div>
              )}
              {!leftPage && (
                <div className="flex items-center justify-center h-full text-gray-300">
                  <BookOpen className="w-16 h-16" />
                </div>
              )}
            </div>

            {/* Right Page */}
            <div className="w-1/2 bg-white p-8 flex flex-col">
              {rightPage?.rightImage && (
                <div className="flex-1 mb-4 rounded-md overflow-hidden shadow-md">
                  <img
                    src={rightPage.rightImage}
                    alt="Right page"
                    className="w-full h-full object-cover"
                  />
                </div>
              )}
              {rightPage?.rightText && (
                <div className="text-gray-800 font-serif leading-relaxed text-sm overflow-y-auto">
                  {rightPage.rightText}
                </div>
              )}
              {!rightPage && (
                <div className="flex items-center justify-center h-full text-gray-300">
                  <BookOpen className="w-16 h-16" />
                </div>
              )}
            </div>
          </motion.div>
        </AnimatePresence>
      </div>

      {/* Navigation Controls */}
      <div className="mt-8 flex items-center gap-6">
        <Button
          variant="outline"
          size="lg"
          onClick={() => paginate(-1)}
          disabled={currentSpread === 0}
          className="shadow-md hover:shadow-lg transition-shadow"
        >
          <ChevronLeft className="w-5 h-5" />
          <span className="ml-2">Previous</span>
        </Button>

        <div className="px-6 py-2 bg-white rounded-full shadow-md">
          <span className="text-amber-900 font-medium">
            Page {currentSpread * 2 + 1}-{Math.min(currentSpread * 2 + 2, pages.length)} of {pages.length}
          </span>
        </div>

        <Button
          variant="outline"
          size="lg"
          onClick={() => paginate(1)}
          disabled={currentSpread === totalSpreads - 1}
          className="shadow-md hover:shadow-lg transition-shadow"
        >
          <span className="mr-2">Next</span>
          <ChevronRight className="w-5 h-5" />
        </Button>
      </div>
    </div>
  );
}

