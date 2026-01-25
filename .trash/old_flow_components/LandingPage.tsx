'use client';

import { useEffect, useRef } from 'react';
import { gsap } from 'gsap';
import { motion } from 'framer-motion';
import Image from 'next/image';
import { WobblyButton } from './WobblyButton';
import { softSpring } from '@/lib/animations';

interface LandingPageProps {
  onBegin: () => void;
}

export function LandingPage({ onBegin }: LandingPageProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const headlineRef = useRef<HTMLHeadingElement>(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      const tl = gsap.timeline({ defaults: { ease: "power2.out" } });

      // 1. Cloud drifts in
      tl.fromTo(".cloud",
        { opacity: 0, x: -50 },
        { opacity: 1, x: 0, duration: 0.8 }
      );

      // 2. Hero character rises up
      tl.fromTo(".hero-character",
        { opacity: 0, y: 40, scale: 0.95 },
        { opacity: 1, y: 0, scale: 1, duration: 0.8, ease: "back.out(1.2)" },
        "-=0.4"
      );

      // 3. Stars twinkle in (staggered)
      tl.fromTo(".star",
        { opacity: 0, scale: 0, rotation: -180 },
        {
          opacity: 1,
          scale: 1,
          rotation: 0,
          duration: 0.5,
          stagger: { each: 0.1, from: "random" },
          ease: "back.out(2)"
        },
        "-=0.3"
      );

      // 4. Headline text reveal
      if (headlineRef.current) {
        const chars = headlineRef.current.textContent?.split('') || [];
        headlineRef.current.innerHTML = chars.map(char =>
          `<span class="char inline-block">${char === ' ' ? '&nbsp;' : char}</span>`
        ).join('');

        tl.fromTo(".char",
          { opacity: 0, y: 30 },
          {
            opacity: 1,
            y: 0,
            duration: 0.6,
            stagger: 0.03,
            ease: "power2.out"
          },
          "-=0.2"
        );
      }

      // 5. Subtext fades
      tl.fromTo(".subtext",
        { opacity: 0, y: 10 },
        { opacity: 1, y: 0, duration: 0.5 },
        "-=0.3"
      );

      // 6. CTA button pops in
      tl.fromTo(".cta-button",
        { opacity: 0, scale: 0.8, y: 20 },
        { opacity: 1, scale: 1, y: 0, duration: 0.5, ease: "back.out(1.7)" },
        "-=0.2"
      );

      // 7. Swirl draws near button
      tl.fromTo(".swirl",
        { opacity: 0, scale: 0.5, rotation: -90 },
        { opacity: 1, scale: 1, rotation: 0, duration: 0.6 },
        "-=0.3"
      );

      // ∞ Floating loop (runs forever)
      gsap.to(".star", {
        y: "random(-8, 8)",
        x: "random(-5, 5)",
        rotation: "random(-15, 15)",
        duration: "random(2, 4)",
        repeat: -1,
        yoyo: true,
        ease: "sine.inOut",
        stagger: { each: 0.2, from: "random" }
      });

      gsap.to(".cloud", {
        x: "+=30",
        y: "+=10",
        duration: 8,
        repeat: -1,
        yoyo: true,
        ease: "sine.inOut"
      });

    }, containerRef);

    return () => ctx.revert();
  }, []);

  return (
    <div ref={containerRef} className="landing-page relative min-h-screen bg-[#F5F1E8] flex flex-col items-center justify-center px-6 overflow-hidden">
      {/* Decorative elements */}
      <Image
        src="/icons/cloud.png"
        alt=""
        width={150}
        height={100}
        className="cloud absolute top-10 left-10 opacity-60"
      />

      <Image
        src="/icons/stars.png"
        alt=""
        width={80}
        height={80}
        className="star star-1 absolute top-20 right-20"
      />
      <Image
        src="/icons/stars.png"
        alt=""
        width={60}
        height={60}
        className="star star-2 absolute top-40 right-40"
      />
      <Image
        src="/icons/stars.png"
        alt=""
        width={70}
        height={70}
        className="star star-3 absolute top-32 right-60"
      />

      {/* Hero */}
      <div className="hero-character mb-8">
        <Image
          src="/hero1.jpeg"
          alt="Character sitting on magical books"
          width={500}
          height={500}
          className="rounded-3xl shadow-2xl"
          priority
        />
      </div>

      {/* Text */}
      <h1
        ref={headlineRef}
        className="headline text-5xl md:text-6xl font-bold text-[#8B7355] text-center mb-4"
        style={{ fontFamily: 'Comic Sans MS, cursive' }}
      >
        Let&apos;s make a story together
      </h1>
      <p className="subtext text-lg text-[#8B7355]/80 text-center mb-12">
        Create magical bedtime stories in minutes
      </p>

      {/* CTA */}
      <div className="relative">
        <Image
          src="/icons/swirl.png"
          alt=""
          width={60}
          height={60}
          className="swirl absolute -bottom-8 -right-8 opacity-50"
        />
        <div className="cta-button">
          <WobblyButton onClick={onBegin} variant="primary">
            <Image src="/icons/magic_wand.png" alt="" width={24} height={24} />
            Begin
          </WobblyButton>
        </div>
      </div>
    </div>
  );
}
