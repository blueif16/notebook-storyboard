"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { AlertCircle, Send } from "lucide-react";

interface InterruptCardProps {
  question: string;
  images?: Array<{
    url: string;
    caption: string;
  }>;
  onSubmit: (response: string) => void;
}

export function InterruptCard({ question, images, onSubmit }: InterruptCardProps) {
  const [response, setResponse] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (response.trim()) {
      onSubmit(response.trim());
      setResponse("");
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="my-4 p-4 bg-gradient-to-br from-yellow-50 to-orange-50 border-2 border-yellow-400 rounded-lg shadow-lg"
    >
      <div className="flex items-start gap-3 mb-3">
        <AlertCircle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
        <div className="flex-1">
          <p className="text-yellow-900 font-medium mb-2">{question}</p>
          
          {/* Show images if provided */}
          {images && images.length > 0 && (
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mb-3">
              {images.map((img, i) => (
                <div key={i} className="relative group">
                  <img
                    src={img.url}
                    alt={img.caption}
                    className="w-full aspect-square object-cover rounded-lg border-2 border-yellow-300"
                  />
                  <div className="absolute bottom-0 left-0 right-0 bg-black/60 text-white text-xs p-1 rounded-b-lg">
                    {img.caption}
                  </div>
                </div>
              ))}
            </div>
          )}
          
          {/* Input form */}
          <form onSubmit={handleSubmit} className="flex gap-2">
            <input
              type="text"
              value={response}
              onChange={(e) => setResponse(e.target.value)}
              placeholder="Your response..."
              className="flex-1 px-3 py-2 bg-white border-2 border-yellow-300 rounded-lg text-sm focus:outline-none focus:border-yellow-500 transition-colors"
              autoFocus
            />
            <button
              type="submit"
              disabled={!response.trim()}
              className="px-4 py-2 bg-yellow-500 hover:bg-yellow-600 disabled:bg-gray-300 disabled:cursor-not-allowed text-white rounded-lg font-medium text-sm flex items-center gap-2 transition-colors"
            >
              <Send className="w-4 h-4" />
              Send
            </button>
          </form>
        </div>
      </div>
    </motion.div>
  );
}
