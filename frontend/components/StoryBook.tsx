"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useState } from "react";
import { ChevronLeft, ChevronRight, BookOpen, Maximize2, BookOpenCheck } from "lucide-react";
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

type ViewMode = "single" | "double";

export function StoryBook({ pages, title = "Story Book" }: StoryBookProps) {
  const [currentPage, setCurrentPage] = useState(0);
  const [direction, setDirection] = useState(0);
  const [viewMode, setViewMode] = useState<ViewMode>("single");

  const paginate = (dir: number) => {
    if (viewMode === "single") {
      const newPage = currentPage + dir;
      if (newPage >= 0 && newPage < pages.length) {
        setDirection(dir);
        setCurrentPage(newPage);
      }
    } else {
      // 双图模式，每次翻2页
      const newPage = currentPage + dir * 2;
      if (newPage >= 0 && newPage < pages.length) {
        setDirection(dir);
        setCurrentPage(newPage);
      }
    }
  };

  const page = pages[currentPage];
  const nextPage = pages[currentPage + 1];
  const imageUrl = page?.leftImage || page?.rightImage;
  const text = page?.leftText || page?.rightText;

  return (
    <div className="w-full h-full flex flex-col items-center justify-center p-4 bg-gradient-to-br from-amber-50 to-orange-50">
      {/* Title and Mode Toggle */}
      <div className="flex items-center gap-4 mb-6">
        <BookOpen className="w-6 h-6 text-amber-700" />
        <h2 className="text-2xl font-serif font-bold text-amber-900">{title}</h2>

        {/* View Mode Toggle */}
        <Button
          variant="outline"
          size="sm"
          onClick={() => setViewMode(viewMode === "single" ? "double" : "single")}
          className="ml-4"
        >
          {viewMode === "single" ? (
            <>
              <BookOpenCheck className="w-4 h-4 mr-2" />
              双图模式
            </>
          ) : (
            <>
              <Maximize2 className="w-4 h-4 mr-2" />
              单图模式
            </>
          )}
        </Button>
      </div>

      {/* Main Content Container */}
      <div className="relative w-full max-w-6xl flex items-center gap-4">
        {/* Left Arrow Button */}
        <Button
          variant="outline"
          size="icon"
          onClick={() => paginate(-1)}
          disabled={currentPage === 0}
          className="h-12 w-12 rounded-full shadow-lg hover:shadow-xl transition-all disabled:opacity-30"
        >
          <ChevronLeft className="w-6 h-6" />
        </Button>

        {/* Image Display Area */}
        {viewMode === "single" ? (
          // 单图模式
          <div className="flex-1 relative aspect-video bg-white rounded-lg shadow-2xl overflow-hidden">
            <AnimatePresence mode="wait" custom={direction}>
              <motion.div
                key={currentPage}
                custom={direction}
                initial={{ x: direction > 0 ? 300 : -300, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                exit={{ x: direction > 0 ? -300 : 300, opacity: 0 }}
                transition={{ duration: 0.3, ease: "easeInOut" }}
                className="absolute inset-0 flex items-center justify-center"
              >
                {imageUrl ? (
                  <img
                    src={imageUrl}
                    alt={`Page ${currentPage + 1}`}
                    className="w-full h-full object-contain"
                  />
                ) : (
                  <div className="flex items-center justify-center h-full text-gray-300">
                    <BookOpen className="w-24 h-24" />
                  </div>
                )}
              </motion.div>
            </AnimatePresence>
          </div>
        ) : (
          // 双图模式
          <div className="flex-1 relative aspect-[2/1] bg-white rounded-lg shadow-2xl overflow-hidden">
            <AnimatePresence mode="wait" custom={direction}>
              <motion.div
                key={currentPage}
                custom={direction}
                initial={{ rotateY: direction > 0 ? -15 : 15, opacity: 0 }}
                animate={{ rotateY: 0, opacity: 1 }}
                exit={{ rotateY: direction > 0 ? 15 : -15, opacity: 0 }}
                transition={{ duration: 0.5, ease: "easeInOut" }}
                className="absolute inset-0 flex"
                style={{ transformStyle: "preserve-3d" }}
              >
                {/* Left Page */}
                <div className="w-1/2 border-r-2 border-amber-200 flex items-center justify-center p-4">
                  {imageUrl ? (
                    <img
                      src={imageUrl}
                      alt={`Page ${currentPage + 1}`}
                      className="w-full h-full object-contain"
                    />
                  ) : (
                    <div className="flex items-center justify-center h-full text-gray-300">
                      <BookOpen className="w-16 h-16" />
                    </div>
                  )}
                </div>

                {/* Right Page */}
                <div className="w-1/2 flex items-center justify-center p-4">
                  {nextPage ? (
                    <img
                      src={nextPage.leftImage || nextPage.rightImage || ""}
                      alt={`Page ${currentPage + 2}`}
                      className="w-full h-full object-contain"
                    />
                  ) : (
                    <div className="flex items-center justify-center h-full text-gray-300">
                      <BookOpen className="w-16 h-16" />
                    </div>
                  )}
                </div>
              </motion.div>
            </AnimatePresence>
          </div>
        )}

        {/* Right Arrow Button */}
        <Button
          variant="outline"
          size="icon"
          onClick={() => paginate(1)}
          disabled={
            viewMode === "single"
              ? currentPage === pages.length - 1
              : currentPage >= pages.length - 2
          }
          className="h-12 w-12 rounded-full shadow-lg hover:shadow-xl transition-all disabled:opacity-30"
        >
          <ChevronRight className="w-6 h-6" />
        </Button>
      </div>

      {/* Page Counter */}
      <div className="mt-6 px-6 py-2 bg-white rounded-full shadow-md">
        <span className="text-amber-900 font-medium">
          {viewMode === "single" ? (
            <>Page {currentPage + 1} of {pages.length}</>
          ) : (
            <>
              Page {currentPage + 1}
              {nextPage && `-${currentPage + 2}`} of {pages.length}
            </>
          )}
        </span>
      </div>
    </div>
  );
}

