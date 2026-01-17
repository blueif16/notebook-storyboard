'use client';

import { useEffect, useRef } from 'react';
import { gsap } from 'gsap';
import { motion } from 'framer-motion';
import Image from 'next/image';
import { ProgressIndicator } from './ProgressIndicator';
import { WobblyButton } from './WobblyButton';

interface CharacterApprovalProps {
  character: {
    imageUrl: string;
    name: string;
  };
  onApprove: () => void;
  onRegenerate: () => void;
}

export function CharacterApproval({ character, onApprove, onRegenerate }: CharacterApprovalProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      const tl = gsap.timeline();

      // 1. Frame draws itself
      tl.fromTo(".character-frame",
        { opacity: 0, scale: 0.9 },
        {
          opacity: 1,
          scale: 1,
          duration: 0.8,
          ease: "power2.inOut"
        }
      );

      // 2. Character materializes - magical entrance!
      tl.fromTo(".character-image",
        {
          opacity: 0,
          scale: 0.7,
          filter: "blur(20px) brightness(1.5)"
        },
        {
          opacity: 1,
          scale: 1,
          filter: "blur(0px) brightness(1)",
          duration: 0.8,
          ease: "power2.out"
        },
        "-=0.3"
      );

      // 3. Stars burst outward
      tl.fromTo(".reveal-star",
        {
          opacity: 0,
          scale: 0,
          x: 0,
          y: 0
        },
        {
          opacity: 1,
          scale: 1,
          x: (i) => [50, -40, 60, -50, 30][i],
          y: (i) => [-40, -50, 20, 40, -60][i],
          duration: 0.6,
          stagger: 0.08,
          ease: "back.out(2)"
        },
        "-=0.4"
      );

      // Stars then float
      gsap.to(".reveal-star", {
        y: "+=10",
        x: "+=5",
        rotation: "random(-20, 20)",
        duration: "random(2, 3)",
        repeat: -1,
        yoyo: true,
        ease: "sine.inOut",
        delay: 1.5
      });

      // 4. Buttons fade up
      tl.fromTo(".action-buttons button",
        { opacity: 0, y: 20 },
        {
          opacity: 1,
          y: 0,
          duration: 0.4,
          stagger: 0.1,
          ease: "back.out(1.5)"
        },
        "-=0.2"
      );

      // 5. Flower accent
      tl.fromTo(".flower-accent",
        { opacity: 0, scale: 0, rotation: -45 },
        {
          opacity: 1,
          scale: 1,
          rotation: 0,
          duration: 0.5,
          ease: "back.out(2)"
        },
        "-=0.2"
      );

      // ∞ Subtle glow pulse
      gsap.to(".character-glow", {
        opacity: 0.6,
        scale: 1.05,
        duration: 2,
        repeat: -1,
        yoyo: true,
        ease: "sine.inOut"
      });

    }, containerRef);

    return () => ctx.revert();
  }, []);

  const handleRegenerate = () => {
    gsap.to(".character-image", {
      opacity: 0,
      scale: 0.9,
      filter: "blur(10px)",
      duration: 0.4,
      onComplete: onRegenerate
    });
  };

  return (
    <div ref={containerRef} className="approval-page relative min-h-screen bg-[#F5F1E8] flex flex-col items-center justify-center px-6">
      <ProgressIndicator step={3} />

      {/* Character presentation */}
      <div className="character-stage relative">
        {/* Glow effect behind */}
        <div className="character-glow absolute inset-0 bg-[#D4A03D] rounded-full blur-3xl opacity-30 -z-10" />

        {/* Hand-drawn frame */}
        <div className="character-frame relative bg-white rounded-3xl shadow-2xl p-8 border-4 border-[#8B7355]">
          {/* The character */}
          <Image
            src={character.imageUrl}
            alt={character.name}
            width={400}
            height={400}
            className="character-image rounded-2xl"
          />
        </div>

        {/* Burst stars */}
        {[...Array(5)].map((_, i) => (
          <Image
            key={i}
            src="/icons/stars.png"
            alt=""
            width={50}
            height={50}
            className={`reveal-star star-${i} absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2`}
          />
        ))}

        {/* Flower accent */}
        <Image
          src="/icons/flower.png"
          alt=""
          width={80}
          height={80}
          className="flower-accent absolute -bottom-4 -right-4"
        />
      </div>

      {/* Action buttons */}
      <div className="action-buttons flex gap-4 mt-12">
        <motion.button
          className="try-again-btn flex items-center gap-2 px-6 py-3 rounded-full bg-white border-2 border-[#8B7355] text-[#8B7355]"
          onClick={handleRegenerate}
          whileHover={{ scale: 1.03, x: -3 }}
          whileTap={{ scale: 0.97 }}
        >
          <Image src="/icons/refresh_arrows.png" alt="" width={24} height={24} />
          Try again
        </motion.button>

        <WobblyButton
          onClick={onApprove}
          variant="primary"
        >
          <Image src="/icons/checkmark.png" alt="" width={24} height={24} />
          Perfect!
          <Image src="/icons/heart.png" alt="" width={20} height={20} className="ml-1" />
        </WobblyButton>
      </div>
    </div>
  );
}
