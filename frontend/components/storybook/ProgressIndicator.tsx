"use client";

import { motion } from "framer-motion";
import { Sparkles, Users, BookOpen, CheckCircle, Loader2 } from "lucide-react";

interface ProgressIndicatorProps {
  stage: string;
  progress: number;
  charactersCount?: number;
  pagesCount?: number;
}

const STAGE_INFO = {
  idle: { label: "Ready", icon: Sparkles, color: "gray" },
  starting: { label: "Starting", icon: Loader2, color: "blue" },
  enhancing: { label: "Enhancing Story", icon: Sparkles, color: "purple" },
  characters_generated: { label: "Characters Created", icon: Users, color: "green" },
  generating_pages: { label: "Creating Pages", icon: BookOpen, color: "blue" },
  complete: { label: "Complete!", icon: CheckCircle, color: "green" },
  error: { label: "Error", icon: Sparkles, color: "red" },
};

export function ProgressIndicator({ 
  stage, 
  progress, 
  charactersCount = 0,
  pagesCount = 0 
}: ProgressIndicatorProps) {
  const stageInfo = STAGE_INFO[stage as keyof typeof STAGE_INFO] || STAGE_INFO.idle;
  const Icon = stageInfo.icon;
  const isAnimating = stage === "starting" || stage === "enhancing" || stage === "generating_pages";

  return (
    <div className="p-4 bg-white rounded-lg shadow-sm border border-gray-200">
      <div className="flex items-center gap-3 mb-3">
        <motion.div
          animate={isAnimating ? { rotate: 360 } : {}}
          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
        >
          <Icon className={`w-5 h-5 text-${stageInfo.color}-500`} />
        </motion.div>
        <span className="font-medium text-gray-900">{stageInfo.label}</span>
        <span className="ml-auto text-sm text-gray-500">{progress}%</span>
      </div>

      {/* Progress bar */}
      <div className="w-full bg-gray-200 rounded-full h-2 mb-3">
        <motion.div
          className={`h-2 rounded-full bg-gradient-to-r from-purple-500 to-pink-500`}
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.5 }}
        />
      </div>

      {/* Status details */}
      {(charactersCount > 0 || pagesCount > 0) && (
        <div className="flex gap-4 text-xs text-gray-600">
          {charactersCount > 0 && (
            <div className="flex items-center gap-1">
              <Users className="w-3 h-3" />
              <span>{charactersCount} characters</span>
            </div>
          )}
          {pagesCount > 0 && (
            <div className="flex items-center gap-1">
              <BookOpen className="w-3 h-3" />
              <span>{pagesCount} pages</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
