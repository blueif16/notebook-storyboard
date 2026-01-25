'use client';

import { useEffect, useRef, useState } from 'react';
import { gsap } from 'gsap';
import Image from 'next/image';

interface GenerationLoadingEnhancedProps {
  phase: 'characters' | 'story';
  currentStep?: number;
  totalSteps?: number;
}

const CHARACTER_MESSAGES = [
  "Dreaming up your story...",
  "Meeting your characters...",
  "Drawing character portraits...",
];

const STORY_MESSAGES = [
  "Creating your storybook...",
  "Painting magical scenes...",
  "Adding finishing touches...",
  "Almost there...",
];

export function GenerationLoadingEnhanced({ phase, currentStep, totalSteps }: GenerationLoadingEnhancedProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const messageRef = useRef<HTMLParagraphElement>(null);
  const [messageIndex, setMessageIndex] = useState(0);

  const messages = phase === 'characters' ? CHARACTER_MESSAGES : STORY_MESSAGES;

  useEffect(() => {
    const ctx = gsap.context(() => {
      // Moon gentle rocking
      gsap.to(".moon", {
        rotation: 15,
        duration: 2,
        repeat: -1,
        yoyo: true,
        ease: "sine.inOut"
      });

      // Stars twinkling sequence
      gsap.to(".loading-star", {
        opacity: gsap.utils.wrap([1, 0.3, 0.8, 0.5, 1]),
        scale: gsap.utils.wrap([1.2, 0.9, 1.1, 0.95, 1.15]),
        duration: 0.8,
        repeat: -1,
        yoyo: true,
        stagger: {
          each: 0.2,
          from: "random"
        },
        ease: "sine.inOut"
      });

      // Swirl slow rotation
      gsap.to(".swirl", {
        rotation: 360,
        duration: 8,
        repeat: -1,
        ease: "none"
      });

      // Dots cluster pulsing
      gsap.to(".loading-dot", {
        scale: gsap.utils.wrap([1.3, 1.1, 1.4, 1.2]),
        duration: gsap.utils.wrap([1.5, 1.8, 1.3, 1.6]),
        repeat: -1,
        yoyo: true,
        stagger: 0.2,
        ease: "sine.inOut"
      });

    }, containerRef);

    return () => ctx.revert();
  }, []);

  // Cycling text messages
  useEffect(() => {
    if (!messageRef.current) return;

    const animateMessage = () => {
      gsap.to(messageRef.current, {
        opacity: 0,
        y: -10,
        duration: 0.3,
        ease: "power2.in",
        onComplete: () => {
          setMessageIndex(prev => (prev + 1) % messages.length);
        }
      });
    };

    gsap.fromTo(messageRef.current,
      { opacity: 0, y: 10 },
      {
        opacity: 1,
        y: 0,
        duration: 0.4,
        ease: "power2.out"
      }
    );

    const timer = setTimeout(animateMessage, 3000);
    return () => clearTimeout(timer);

  }, [messageIndex, messages.length]);

  return (
    <div ref={containerRef} className="loading-screen relative min-h-screen bg-[#F5F1E8] flex flex-col items-center justify-center overflow-hidden">
      {/* Floating elements */}
      <Image
        src="/icons/moon.png"
        alt=""
        width={120}
        height={120}
        className="moon absolute top-20 left-20 opacity-70"
      />

      <div className="stars-cluster absolute inset-0">
        {[...Array(5)].map((_, i) => (
          <Image
            key={i}
            src="/icons/stars.png"
            alt=""
            width={60}
            height={60}
            className={`loading-star star-${i} absolute`}
            style={{
              top: `${20 + i * 15}%`,
              left: `${10 + i * 20}%`,
            }}
          />
        ))}
      </div>

      <Image
        src="/icons/swirl.png"
        alt=""
        width={150}
        height={150}
        className="swirl mb-8 opacity-60"
      />

      <div className="dots-cluster flex gap-2 mb-8">
        {[...Array(4)].map((_, i) => (
          <span
            key={i}
            className="loading-dot w-4 h-4 rounded-full bg-[#6B8FA3]"
          />
        ))}
      </div>

      {/* Cycling message */}
      <p
        ref={messageRef}
        className="loading-message text-3xl font-bold text-[#8B7355] text-center mb-4"
        style={{ fontFamily: 'Comic Sans MS, cursive' }}
      >
        {messages[messageIndex]}
      </p>

      {/* Progress indicator */}
      {currentStep !== undefined && totalSteps !== undefined && (
        <div className="progress-info text-center">
          <p className="text-lg text-[#8B7355]/70 mb-2">
            Step {currentStep} of {totalSteps}
          </p>
          <div className="progress-bar w-64 h-2 bg-[#D4C4B0] rounded-full overflow-hidden">
            <div
              className="progress-fill h-full bg-[#6B8FA3] transition-all duration-500"
              style={{ width: `${(currentStep / totalSteps) * 100}%` }}
            />
          </div>
        </div>
      )}
    </div>
  );
}
