"use client";

import { motion } from "framer-motion";
import { useRef } from "react";

interface CanvasWrapperProps {
  children: React.ReactNode;
}

export function CanvasWrapper({ children }: CanvasWrapperProps) {
  const constraintsRef = useRef(null);

  return (
    <div className="relative w-screen h-screen overflow-hidden bg-[#faf9f6]">
      {/* Architectural Grid Overlay */}
      <div
        className="absolute inset-0 z-0 pointer-events-none opacity-[0.03]"
        style={{
          backgroundImage: `linear-gradient(#000 1px, transparent 1px), linear-gradient(90deg, #000 1px, transparent 1px)`,
          backgroundSize: '40px 40px'
        }}
      />

      {/* Animated Background Mesh - More organic and fluid */}
      <div className="absolute inset-0 z-0 opacity-40 pointer-events-none overflow-hidden">
        <motion.div
          animate={{
            x: [0, 100, 0],
            y: [0, -50, 0],
            scale: [1, 1.1, 1]
          }}
          transition={{ duration: 20, repeat: Infinity, ease: "easeInOut" }}
          className="absolute top-[-20%] left-[-10%] w-[70%] h-[70%] rounded-full bg-gradient-to-r from-orange-200 to-rose-200 blur-[130px]"
        />
        <motion.div
          animate={{
            x: [0, -100, 0],
            y: [0, 50, 0],
            scale: [1, 1.2, 1]
          }}
          transition={{ duration: 25, repeat: Infinity, ease: "easeInOut", delay: 2 }}
          className="absolute bottom-[-20%] right-[-10%] w-[70%] h-[70%] rounded-full bg-gradient-to-r from-indigo-200 to-purple-200 blur-[130px]"
        />
        <motion.div
          animate={{ opacity: [0.3, 0.6, 0.3] }}
          transition={{ duration: 15, repeat: Infinity, ease: "easeInOut" }}
          className="absolute top-[40%] left-[40%] w-[40%] h-[40%] rounded-full bg-cyan-100 blur-[150px] mix-blend-multiply"
        />
      </div>

      <motion.div
        ref={constraintsRef}
        className="w-full h-full cursor-grab active:cursor-grabbing z-10 relative"
      >
        <motion.div
          drag
          dragConstraints={{ left: -2000, right: 2000, top: -2000, bottom: 2000 }}
          className="flex items-center gap-16 p-32 w-max h-full"
          initial={{ x: 0, y: 0 }}
        >
          {children}
        </motion.div>
      </motion.div>

      {/* Vignette & Grain for Texture */}
      <div className="absolute inset-0 pointer-events-none bg-radial-gradient from-transparent via-transparent to-white/40 z-20" />
      <div className="absolute inset-0 pointer-events-none opacity-[0.02] mix-blend-overlay" style={{ backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")` }} />
    </div>
  );
}
