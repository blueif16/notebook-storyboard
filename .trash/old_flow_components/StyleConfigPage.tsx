'use client';

import { useEffect, useRef, useState } from 'react';
import { gsap } from 'gsap';
import { motion } from 'framer-motion';
import Image from 'next/image';
import { ProgressIndicator } from './ProgressIndicator';
import { WobblyButton } from './WobblyButton';
import { STYLE_OPTIONS } from '@/types/storybook';

interface StyleConfigPageProps {
  onNext: (style: string) => void;
  onBack: () => void;
}

export function StyleConfigPage({ onNext, onBack }: StyleConfigPageProps) {
  const cardRef = useRef<HTMLDivElement>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [selectedStyle, setSelectedStyle] = useState<string | null>(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      const tl = gsap.timeline({ defaults: { ease: "power2.out" } });

      // Progress indicator - first dot fills
      tl.fromTo(".progress-dot",
        { scale: 0, opacity: 0 },
        {
          scale: 1,
          opacity: 1,
          duration: 0.4,
          stagger: 0.1,
          ease: "back.out(2)"
        }
      );

      // Card "placed down"
      tl.fromTo(".config-card",
        {
          opacity: 0,
          y: -20,
          scale: 0.95,
        },
        {
          opacity: 1,
          y: 0,
          scale: 1,
          duration: 0.6,
          ease: "back.out(1.2)"
        },
        "-=0.2"
      );

      // Card content fades up
      tl.fromTo(".card-content > *",
        { opacity: 0, y: 15 },
        {
          opacity: 1,
          y: 0,
          duration: 0.4,
          stagger: 0.08
        },
        "-=0.3"
      );

      // Decorative dots breathe (infinite)
      gsap.to(".dots-cluster", {
        scale: 1.1,
        opacity: 0.8,
        duration: 2,
        repeat: -1,
        yoyo: true,
        ease: "sine.inOut"
      });

    }, cardRef);

    return () => ctx.revert();
  }, []);

  // Recording pulse animation
  useEffect(() => {
    if (isRecording) {
      gsap.to(".sound-wave", {
        scaleY: gsap.utils.wrap([1, 1.5, 1.2, 1.7, 1]),
        duration: 0.4,
        repeat: -1,
        stagger: 0.1,
        ease: "sine.inOut"
      });
    } else {
      gsap.to(".sound-wave", {
        scaleY: 1,
        duration: 0.3
      });
    }
  }, [isRecording]);

  return (
    <div ref={cardRef} className="style-page relative min-h-screen bg-[#F5F1E8] flex flex-col items-center justify-center px-6">
      {/* Progress Indicator */}
      <ProgressIndicator step={1} />

      {/* Main Card */}
      <div className="config-card relative bg-white rounded-3xl shadow-xl p-8 max-w-2xl w-full border-4 border-[#8B7355]">
        <div className="card-content space-y-6">
          <div className="section-header flex items-center gap-3 mb-6">
            <Image src="/icons/paintbrush.png" alt="" width={40} height={40} />
            <h2 className="text-3xl font-bold text-[#8B7355]" style={{ fontFamily: 'Comic Sans MS, cursive' }}>
              Choose your style
            </h2>
          </div>

          {/* Style options */}
          <div className="style-options grid grid-cols-2 gap-4">
            {STYLE_OPTIONS.map((style) => (
              <motion.button
                key={style.id}
                className={`style-option p-6 rounded-2xl border-3 transition-all ${
                  selectedStyle === style.id
                    ? 'bg-[#6B8FA3] text-white border-[#8B7355]'
                    : 'bg-[#F5F1E8] text-[#8B7355] border-[#D4C4B0]'
                } border-2`}
                onClick={() => setSelectedStyle(style.id)}
                whileHover={{
                  scale: 1.03,
                  y: -4,
                }}
                whileTap={{ scale: 0.98 }}
                transition={{ type: "spring", stiffness: 300, damping: 20 }}
              >
                <div className="font-bold mb-1">{style.label}</div>
                <div className="text-xs opacity-75">{style.description}</div>
              </motion.button>
            ))}
          </div>

          {/* Voice Recording */}
          <div className="voice-section flex flex-col items-center gap-4 mt-8">
            <p className="text-sm text-[#8B7355]/70">Or record your own style preference</p>
            <motion.button
              className={`mic-button relative p-6 rounded-full ${
                isRecording ? 'bg-red-100' : 'bg-[#F5F1E8]'
              } border-2 border-[#8B7355]`}
              onClick={() => setIsRecording(!isRecording)}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Image src="/icons/microphone.png" alt="" width={40} height={40} />
              {/* Sound wave dots */}
              {isRecording && (
                <div className="sound-waves absolute -right-12 top-1/2 -translate-y-1/2 flex gap-1">
                  {[...Array(5)].map((_, i) => (
                    <span
                      key={i}
                      className="sound-wave w-1 h-8 bg-[#6B8FA3] rounded-full"
                    />
                  ))}
                </div>
              )}
            </motion.button>
            <Image
              src="/icons/music-notes.png"
              alt=""
              width={60}
              height={60}
              className="opacity-50"
            />
          </div>
        </div>

        {/* Decorative cluster */}
        <Image
          src="/icons/dots.png"
          alt=""
          width={80}
          height={80}
          className="dots-cluster absolute -bottom-4 -right-4 opacity-40"
        />
      </div>

      {/* Navigation */}
      <nav className="page-nav flex justify-between w-full max-w-2xl mt-8">
        <motion.button
          className="nav-back p-3 rounded-full bg-white border-2 border-[#8B7355]"
          onClick={onBack}
          whileHover={{ x: -3 }}
          whileTap={{ scale: 0.95 }}
        >
          <Image src="/icons/home.png" alt="Home" width={24} height={24} />
        </motion.button>
        <WobblyButton
          onClick={() => selectedStyle && onNext(selectedStyle)}
          disabled={!selectedStyle}
          variant="primary"
        >
          Next
          <Image src="/icons/right_arrow.png" alt="" width={20} height={20} />
        </WobblyButton>
      </nav>
    </div>
  );
}
