"use client";

import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Sparkles, Send, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useCopilotChat } from "@copilotkit/react-core";

interface FloatingCompanionProps {
    className?: string;
    threadId?: string;
}

export function FloatingCompanion({ className }: FloatingCompanionProps) {
    const [isOpen, setIsOpen] = useState(false);
    const [input, setInput] = useState("");
    const scrollRef = useRef<HTMLDivElement>(null);

    const { visibleMessages, appendMessage } = useCopilotChat();

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [visibleMessages, isOpen]);

    const handleSend = async () => {
        if (!input.trim()) return;
        // @ts-expect-error - CopilotKit API compatibility
        await appendMessage({ role: "user", content: input });
        setInput("");
    };

    return (
        <div className={`fixed bottom-8 right-8 z-50 flex flex-col items-end pointer-events-none ${className}`}>
            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ opacity: 0, scale: 0.8, y: 20 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.8, y: 20 }}
                        className="bg-white/90 backdrop-blur-2xl border border-white/50 rounded-3xl shadow-2xl w-[380px] h-[600px] mb-4 pointer-events-auto flex flex-col overflow-hidden"
                    >
                        {/* Header */}
                        <div className="flex justify-between items-center p-4 border-b border-gray-100/50 bg-white/50">
                            <div className="flex items-center gap-2">
                                <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
                                <span className="font-semibold text-gray-700">Creative Companion</span>
                            </div>
                            <Button variant="ghost" size="icon" onClick={() => setIsOpen(false)} className="h-8 w-8 rounded-full hover:bg-gray-100/50">
                                <X className="w-4 h-4 text-gray-500" />
                            </Button>
                        </div>

                        {/* Messages Area */}
                        <div className="flex-1 overflow-y-auto p-4 space-y-4" ref={scrollRef}>
                            {visibleMessages.length === 0 && (
                                <div className="text-center text-gray-400 text-sm mt-10">
                                    <Sparkles className="w-8 h-8 mx-auto mb-2 opacity-50" />
                                    <p>Tell me a story idea to begin...</p>
                                </div>
                            )}

                            {visibleMessages.map((msg, idx) => (
                                <div key={idx} className={`flex ${msg.isTextMessage() && msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                                    <div className={`max-w-[85%] rounded-2xl p-3 text-sm ${msg.isTextMessage() && msg.role === 'user'
                                        ? 'bg-black text-white rounded-br-none'
                                        : 'bg-white shadow-sm border border-gray-100 text-gray-800 rounded-bl-none'
                                        }`}>
                                        {msg.isTextMessage() ? msg.content : "..."}
                                    </div>
                                </div>
                            ))}
                        </div>

                        {/* Input Area */}
                        <div className="p-4 bg-white/50 border-t border-gray-100/50">
                            <form onSubmit={(e) => { e.preventDefault(); handleSend(); }} className="relative">
                                <input
                                    type="text"
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    placeholder="Describe your story..."
                                    className="w-full bg-gray-50 border border-gray-200 rounded-full py-3 pl-4 pr-12 text-sm focus:outline-none focus:ring-2 focus:ring-purple-100 transition-all"
                                />
                                <div className="absolute right-1 top-1 flex items-center">
                                    <Button size="icon" type="submit" className="h-8 w-8 rounded-full bg-black text-white hover:bg-gray-800 ml-1">
                                        <Send className="w-3 h-3" />
                                    </Button>
                                </div>
                            </form>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Orb Trigger */}
            <div className="relative group">
                <div className="absolute inset-0 rounded-full bg-blue-400 blur-xl opacity-20 group-hover:opacity-40 animate-pulse duration-1000" />
                <div className="absolute -inset-2 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 blur-2xl opacity-0 group-hover:opacity-30 transition-opacity duration-500" />

                <motion.button
                    onClick={() => setIsOpen(!isOpen)}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="w-16 h-16 rounded-full bg-white/60 backdrop-blur-xl backdrop-saturate-150 shadow-2xl border border-white/50 flex items-center justify-center relative z-10 overflow-hidden ring-1 ring-white/60 pointer-events-auto"
                >
                    <div className="absolute inset-0 rounded-full bg-gradient-to-tr from-indigo-300/30 via-purple-300/30 to-orange-200/30 animate-spin-slow opacity-100" />

                    <Sparkles
                        className={`w-7 h-7 text-indigo-900 drop-shadow-sm transition-all duration-500 ${isOpen ? 'rotate-90 opacity-0 scale-50' : 'rotate-0 opacity-100 scale-100'}`}
                    />

                    <X
                        className={`absolute w-7 h-7 text-gray-500 transition-all duration-500 ${isOpen ? 'rotate-0 opacity-100 scale-100' : '-rotate-90 opacity-0 scale-50'}`}
                    />
                </motion.button>
            </div>
        </div>
    );
}
