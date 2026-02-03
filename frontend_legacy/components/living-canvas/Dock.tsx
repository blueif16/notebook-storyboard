"use client";

import { motion } from "framer-motion";
import { Plus, LayoutGrid, Settings, Share, Play } from "lucide-react";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

interface DockProps {
    onAddSource: () => void;
    onViewSources: () => void;
    onGenerate: () => void;
}

export function Dock({ onAddSource, onViewSources, onGenerate }: DockProps) {
    const items = [
        { icon: Plus, label: "Add Source", onClick: onAddSource },
        { icon: LayoutGrid, label: "Sources", onClick: onViewSources },
        { icon: Play, label: "Generate", onClick: onGenerate, primary: true },
        { icon: Settings, label: "Settings", onClick: () => { } },
        { icon: Share, label: "Share", onClick: () => { } },
    ];

    return (
        <div className="fixed bottom-8 left-1/2 -translate-x-1/2 z-40">
            <motion.div
                initial={{ y: 100, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                className="flex items-center gap-2 p-2 bg-white/70 backdrop-blur-2xl border border-white/50 rounded-full shadow-2xl"
            >
                <TooltipProvider>
                    {items.map((item, idx) => (
                        <Tooltip key={idx}>
                            <TooltipTrigger asChild>
                                <motion.button
                                    whileHover={{ scale: 1.2, y: -5 }}
                                    whileTap={{ scale: 0.9 }}
                                    onClick={item.onClick}
                                    className={`relative p-3 rounded-full transition-all duration-200 ${item.primary
                                            ? "bg-black text-white hover:bg-gray-800"
                                            : "hover:bg-white/50 text-gray-600 hover:text-black"
                                        }`}
                                >
                                    <item.icon className="w-5 h-5" />
                                </motion.button>
                            </TooltipTrigger>
                            <TooltipContent>
                                <p>{item.label}</p>
                            </TooltipContent>
                        </Tooltip>
                    ))}
                </TooltipProvider>
            </motion.div>
        </div>
    );
}
