"use client";

import { motion } from "framer-motion";

interface SceneCardProps {
    image?: string;
    text?: string;
    index: number;
}

export function SceneCard({ image, text, index }: SceneCardProps) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 50, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{ duration: 0.8, delay: index * 0.15, type: "spring", bounce: 0.4 }}
            className="relative w-[420px] h-[640px] flex-shrink-0 group perspective-1000"
        >
            {/* Main Glass Container - Tilt Effect wrapper can be added here if needed, but keeping it simple for perf */}
            <motion.div
                whileHover={{ y: -10, rotateX: 2, rotateY: 2, scale: 1.02 }}
                transition={{ duration: 0.4 }}
                className="w-full h-full relative"
            >
                {/* Back Glow - Ambient Light */}
                <div className="absolute inset-4 bg-gradient-to-tr from-purple-500/20 to-orange-500/20 rounded-[40px] blur-2xl group-hover:blur-3xl transition-all duration-700 opacity-60 group-hover:opacity-100" />

                {/* The Card Itself */}
                <div className="absolute inset-0 bg-white/60 backdrop-blur-2xl backdrop-saturate-150 border border-white/60 rounded-[40px] shadow-2xl overflow-hidden transition-all duration-500 ring-1 ring-white/40">

                    {/* Image Layer - Floating Parallax Effect */}
                    <div className="absolute top-3 left-3 right-3 bottom-[35%] rounded-[32px] overflow-hidden shadow-inner bg-gray-50/50 border border-white/50 relative group-hover:bottom-[38%] transition-all duration-500 ease-out-expo">
                        {image ? (
                            <motion.img
                                src={image}
                                alt="Scene"
                                className="w-full h-full object-cover"
                                initial={{ scale: 1.1 }}
                                whileHover={{ scale: 1 }}
                                transition={{ duration: 1.5, ease: "easeOut" }}
                            />
                        ) : (
                            <div className="w-full h-full flex flex-col items-center justify-center text-gray-400 bg-gray-100/50">
                                <div className="w-16 h-16 rounded-full bg-white/80 animate-pulse mb-3" />
                                <span className="text-sm font-medium tracking-widest uppercase opacity-70">Dreaming...</span>
                            </div>
                        )}

                        {/* Shimmer Overlay */}
                        <div className="absolute inset-0 bg-gradient-to-tr from-white/0 via-white/20 to-white/0 opacity-0 group-hover:opacity-100 transition-opacity duration-700 pointer-events-none" />
                    </div>

                    {/* Text Layer - "Caption Card" style */}
                    <div className="absolute inset-x-0 bottom-0 h-[38%] p-8 flex flex-col justify-center bg-gradient-to-b from-white/0 to-white/80">
                        <div className="bg-white/40 backdrop-blur-sm p-6 rounded-2xl border border-white/60 shadow-sm relative">
                            {/* Decorative quotes or lines */}
                            <div className="absolute top-2 left-1/2 -translate-x-1/2 w-12 h-1 rounded-full bg-gray-300/50" />

                            <p className="text-gray-800 font-serif text-lg leading-relaxed text-center line-clamp-5 drop-shadow-sm mt-2">
                                {text || "The empty canvas waits for your story to begin..."}
                            </p>
                        </div>
                    </div>
                </div>
            </motion.div>
        </motion.div>
    );
}
