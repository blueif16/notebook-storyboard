'use client';

import { useEffect, useRef, useState } from 'react';
import { gsap } from 'gsap';
import { motion } from 'framer-motion';
import Image from 'next/image';
import { ProgressIndicator } from './ProgressIndicator';
import { WobblyButton } from './WobblyButton';

interface BriefInputPageProps {
  onNext: (brief: string) => void;
  onBack: () => void;
}

const placeholders = [
  "Once upon a time...",
  "In a land far away...",
  "There once lived a...",
];

export function BriefInputPage({ onNext, onBack }: BriefInputPageProps) {
  const textAreaRef = useRef<HTMLTextAreaElement>(null);
  const [inputValue, setInputValue] = useState('');
  const [isValid, setIsValid] = useState(false);
  const [currentPlaceholder, setCurrentPlaceholder] = useState(placeholders[0]);

  // Placeholder typing animation
  useEffect(() => {
    let currentIndex = 0;
    let charIndex = 0;
    let isDeleting = false;

    const typePlaceholder = () => {
      if (inputValue) return;

      const text = placeholders[currentIndex];

      if (!isDeleting) {
        if (charIndex <= text.length) {
          setCurrentPlaceholder(text.slice(0, charIndex));
          charIndex++;
          setTimeout(typePlaceholder, 80);
        } else {
          setTimeout(() => {
            isDeleting = true;
            typePlaceholder();
          }, 2000);
        }
      } else {
        if (charIndex > 0) {
          setCurrentPlaceholder(text.slice(0, charIndex));
          charIndex--;
          setTimeout(typePlaceholder, 50);
        } else {
          isDeleting = false;
          currentIndex = (currentIndex + 1) % placeholders.length;
          setTimeout(typePlaceholder, 500);
        }
      }
    };

    const timer = setTimeout(typePlaceholder, 1000);
    return () => clearTimeout(timer);
  }, [inputValue]);

  // Stars twinkle when valid
  useEffect(() => {
    if (isValid) {
      gsap.to(".submit-star", {
        scale: gsap.utils.wrap([1.2, 1.3, 1.1]),
        opacity: 1,
        duration: 0.6,
        repeat: -1,
        yoyo: true,
        stagger: 0.2,
        ease: "sine.inOut"
      });
    } else {
      gsap.to(".submit-star", {
        scale: 1,
        opacity: 0.4,
        duration: 0.3
      });
    }
  }, [isValid]);

  return (
    <div className="brief-page relative min-h-screen bg-[#F5F1E8] flex flex-col items-center justify-center px-6">
      {/* Progress - second dot green */}
      <ProgressIndicator step={2} />

      <motion.div
        className="brief-card relative bg-white rounded-3xl shadow-xl p-8 max-w-3xl w-full border-4 border-[#8B7355]"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: [0.25, 0.1, 0.25, 1] }}
      >
        <motion.div
          className="pencil-icon flex items-center gap-3 mb-6"
          initial={{ opacity: 0, x: -10, rotate: -20 }}
          animate={{ opacity: 1, x: 0, rotate: 0 }}
          transition={{ delay: 0.3, duration: 0.4 }}
        >
          <Image src="/icons/pencil.png" alt="" width={40} height={40} />
          <h2 className="text-3xl font-bold text-[#8B7355]" style={{ fontFamily: 'Comic Sans MS, cursive' }}>
            Tell me about your story
          </h2>
        </motion.div>

        <motion.textarea
          ref={textAreaRef}
          className="story-input w-full h-64 p-6 rounded-2xl border-2 border-[#D4C4B0] bg-[#F5F1E8] text-[#8B7355] text-lg resize-none focus:outline-none focus:border-[#6B8FA3] transition-colors"
          placeholder={currentPlaceholder}
          value={inputValue}
          onChange={(e) => {
            setInputValue(e.target.value);
            setIsValid(e.target.value.length > 20);
          }}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4, duration: 0.4 }}
          style={{ fontFamily: 'Georgia, serif' }}
        />

        {/* Decorative swirl */}
        <motion.div
          className="swirl-decoration absolute -bottom-6 -left-6"
          initial={{ opacity: 0, scale: 0.5 }}
          animate={{ opacity: 0.6, scale: 1 }}
          transition={{ delay: 0.6, duration: 0.5 }}
        >
          <Image src="/icons/swirl.png" alt="" width={80} height={80} />
        </motion.div>
      </motion.div>

      {/* Submit with stars */}
      <div className="submit-area relative flex items-center justify-center mt-8">
        <Image
          src="/icons/stars.png"
          alt=""
          width={50}
          height={50}
          className="submit-star star-1 absolute -left-16 top-0 opacity-40"
        />
        <Image
          src="/icons/stars.png"
          alt=""
          width={40}
          height={40}
          className="submit-star star-2 absolute -right-16 top-0 opacity-40"
        />
        <Image
          src="/icons/stars.png"
          alt=""
          width={45}
          height={45}
          className="submit-star star-3 absolute left-1/2 -translate-x-1/2 -top-12 opacity-40"
        />

        <WobblyButton
          onClick={() => isValid && onNext(inputValue)}
          disabled={!isValid}
          variant="primary"
        >
          <Image src="/icons/magic_wand.png" alt="" width={24} height={24} />
          Create
        </WobblyButton>
      </div>

      {/* Navigation */}
      <nav className="page-nav flex justify-between w-full max-w-3xl mt-8">
        <motion.button
          className="nav-back p-3 rounded-full bg-white border-2 border-[#8B7355]"
          onClick={onBack}
          whileHover={{ x: -3 }}
          whileTap={{ scale: 0.95 }}
        >
          <Image src="/icons/home.png" alt="Back" width={24} height={24} />
        </motion.button>
      </nav>
    </div>
  );
}
