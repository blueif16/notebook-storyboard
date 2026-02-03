"use client";

import { motion, AnimatePresence } from "framer-motion";
import { X, Globe, FileText, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useState } from "react";
import { Source } from "@/lib/types";

interface SourcesOverlayProps {
    isOpen: boolean;
    onClose: () => void;
    sources: Source[];
    onAddUrl: (url: string) => void;
    onAddFile: (file: File) => void;
    onRemoveSource: (id: string) => void;
}

export function SourcesOverlay({ isOpen, onClose, sources, onAddUrl, onAddFile, onRemoveSource }: SourcesOverlayProps) {
    const [urlInput, setUrlInput] = useState("");

    const handleUrlSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (urlInput.trim()) {
            onAddUrl(urlInput);
            setUrlInput("");
        }
    };

    const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            onAddFile(e.target.files[0]);
        }
    };

    return (
        <AnimatePresence>
            {isOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                    {/* Backdrop */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={onClose}
                        className="absolute inset-0 bg-black/20 backdrop-blur-sm"
                    />

                    {/* Modal */}
                    <motion.div
                        initial={{ scale: 0.9, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        exit={{ scale: 0.9, opacity: 0 }}
                        className="relative bg-white rounded-3xl shadow-2xl w-full max-w-2xl overflow-hidden flex flex-col max-h-[80vh]"
                    >
                        {/* Header */}
                        <div className="p-6 border-b border-gray-100 flex justify-between items-center bg-gray-50/50">
                            <h2 className="text-2xl font-serif font-bold text-gray-800">Knowledge Sources</h2>
                            <Button variant="ghost" size="icon" onClick={onClose} className="hover:bg-gray-200/50 rounded-full">
                                <X className="w-5 h-5" />
                            </Button>
                        </div>

                        {/* Content */}
                        <div className="p-6 overflow-y-auto space-y-8">
                            {/* Add New Section */}
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <form onSubmit={handleUrlSubmit} className="space-y-3 p-4 rounded-2xl bg-blue-50/50 border border-blue-100">
                                    <h3 className="font-semibold text-blue-900 flex items-center gap-2">
                                        <Globe className="w-4 h-4" /> Add Web Link
                                    </h3>
                                    <div className="flex gap-2">
                                        <input
                                            type="text"
                                            value={urlInput}
                                            onChange={(e) => setUrlInput(e.target.value)}
                                            placeholder="https://example.com"
                                            className="flex-1 rounded-xl border-gray-200 text-sm p-2 focus:ring-2 focus:ring-blue-200 outline-none"
                                        />
                                        <Button type="submit" size="sm" className="rounded-xl bg-blue-600 hover:bg-blue-700 text-white">Add</Button>
                                    </div>
                                </form>

                                <div className="space-y-3 p-4 rounded-2xl bg-orange-50/50 border border-orange-100">
                                    <h3 className="font-semibold text-orange-900 flex items-center gap-2">
                                        <FileText className="w-4 h-4" /> Upload PDF
                                    </h3>
                                    <div className="relative">
                                        <input
                                            type="file"
                                            accept=".pdf"
                                            onChange={handleFileUpload}
                                            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                                        />
                                        <Button variant="outline" className="w-full rounded-xl border-orange-200 text-orange-700 hover:bg-orange-100 hover:text-orange-800">
                                            Choose File...
                                        </Button>
                                    </div>
                                </div>
                            </div>

                            {/* List Section */}
                            <div>
                                <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">Active Sources</h3>
                                <div className="space-y-3">
                                    {sources.length === 0 && (
                                        <div className="text-center py-8 text-gray-400 border-2 border-dashed border-gray-100 rounded-2xl">
                                            No sources added yet.
                                        </div>
                                    )}
                                    {sources.map((source) => (
                                        <div key={source.id} className="flex items-center justify-between p-4 bg-white border border-gray-100 rounded-2xl shadow-sm group hover:shadow-md transition-all">
                                            <div className="flex items-center gap-3 overflow-hidden">
                                                <div className={`p-2 rounded-lg ${source.url.startsWith("http") ? "bg-blue-100 text-blue-600" : "bg-orange-100 text-orange-600"}`}>
                                                    {source.url.startsWith("http") ? <Globe className="w-4 h-4" /> : <FileText className="w-4 h-4" />}
                                                </div>
                                                <div className="min-w-0">
                                                    <p className="font-medium text-gray-800 truncate">{source.title || source.url}</p>
                                                    <p className="text-xs text-gray-400">
                                                        {source.status === "loading" ? "Analyzing..." : "Ready"}
                                                    </p>
                                                </div>
                                            </div>
                                            <Button
                                                variant="ghost"
                                                size="icon"
                                                onClick={() => onRemoveSource(source.id)}
                                                className="opacity-0 group-hover:opacity-100 text-red-400 hover:text-red-600 hover:bg-red-50 rounded-full transition-all"
                                            >
                                                <Trash2 className="w-4 h-4" />
                                            </Button>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </motion.div>
                </div>
            )}
        </AnimatePresence>
    );
}
