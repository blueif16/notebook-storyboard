'use client';

import { useEffect, useRef } from 'react';
import { gsap } from 'gsap';
import { motion } from 'framer-motion';
import Image from 'next/image';
import { ProgressIndicator } from './ProgressIndicator';
import { WobblyButton } from './WobblyButton';
import type { Character } from '@/types/storybook';

interface CharacterApprovalProps {
  characters: Character[];
  onContinue: () => void;
}

export function CharacterApproval({ characters, onContinue }: CharacterApprovalProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      const tl = gsap.timeline();

      // 1. Title fades in
      tl.fromTo(".approval-title",
        { opacity: 0, y: -20 },
        {
          opacity: 1,
          y: 0,
          duration: 0.6,
          ease: "power2.out"
        }
      );

      // 2. Character cards appear in sequence
      tl.fromTo(".character-card",
        {
          opacity: 0,
          scale: 0.8,
          y: 30
        },
        {
          opacity: 1,
          scale: 1,
          y: 0,
          duration: 0.6,
          stagger: 0.15,
          ease: "back.out(1.5)"
        },
        "-=0.3"
      );

      // 3. Stars burst around each character
      tl.fromTo(".character-star",
        {
          opacity: 0,
          scale: 0,
          x: 0,
          y: 0
        },
        {
          opacity: 1,
          scale: 1,
          x: (i) => [30, -30, 25, -25][i % 4],
          y: (i) => [-30, -30, 30, 30][i % 4],
          duration: 0.5,
          stagger: 0.05,
          ease: "back.out(2)"
        },
        "-=0.3"
      );

      // Stars float
      gsap.to(".character-star", {
        y: "+=8",
        x: "+=4",
        rotation: "random(-15, 15)",
        duration: "random(2, 3)",
        repeat: -1,
        yoyo: true,
        ease: "sine.inOut",
        delay: 1
      });

      // 4. Button fades up
      tl.fromTo(".continue-button",
        { opacity: 0, y: 20 },
        {
          opacity: 1,
          y: 0,
          duration: 0.5,
          ease: "back.out(1.5)"
        },
        "-=0.2"
      );

      // Subtle glow pulse on cards
      gsap.to(".character-glow", {
        opacity: 0.4,
        scale: 1.05,
        duration: 2,
        repeat: -1,
        yoyo: true,
        ease: "sine.inOut"
      });

    }, containerRef);

    return () => ctx.revert();
  }, []);

  return (
    <div ref={containerRef} className="approval-page relative min-h-screen bg-[#F5F1E8] flex flex-col items-center justify-center px-6 py-20">
      <ProgressIndicator step={3} />

      {/* Title */}
      <motion.div className="approval-title text-center mb-12">
        <h2 className="text-4xl font-bold text-[#8B7355] mb-2" style={{ fontFamily: 'Comic Sans MS, cursive' }}>
          Meet Your Characters!
        </h2>
        <p className="text-lg text-[#8B7355]/70">
          {characters.length} {characters.length === 1 ? 'character' : 'characters'} ready for your story
        </p>
      </motion.div>

      {/* Character Grid */}
      <div className="characters-grid grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl w-full mb-12">
        {characters.map((character, index) => (
          <div key={index} className="character-card-wrapper relative">
            {/* Glow effect */}
            <div className="character-glow absolute inset-0 bg-[#D4A03D] rounded-full blur-3xl opacity-20 -z-10" />

            {/* Card */}
            <div className="character-card relative bg-white rounded-3xl shadow-2xl p-6 border-4 border-[#8B7355]">
              {/* Character Image */}
              {character.image_url && (
                <Image
                  src={character.image_url}
                  alt={character.name}
                  width={300}
                  height={300}
                  className="w-full h-auto rounded-2xl mb-4"
                />
              )}

              {/* Character Name */}
              <h3 className="text-2xl font-bold text-[#8B7355] text-center mb-2" style={{ fontFamily: 'Comic Sans MS, cursive' }}>
                {character.name}
              </h3>

              {/* Character Description */}
              <p className="text-sm text-[#8B7355]/70 text-center line-clamp-3">
                {character.description}
              </p>

              {/* Decorative stars */}
              {[...Array(4)].map((_, i) => (
                <Image
                  key={i}
                  src="/icons/stars.png"
                  alt=""
                  width={30}
                  height={30}
                  className={`character-star star-${i} absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2`}
                />
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Continue Button */}
      <div className="continue-button">
        <WobblyButton
          onClick={onContinue}
          variant="primary"
        >
          <Image src="/icons/magic_wand.png" alt="" width={24} height={24} />
          Continue to Story
          <Image src="/icons/right_arrow.png" alt="" width={20} height={20} className="ml-2" />
        </WobblyButton>
      </div>
    </div>
  );
}
