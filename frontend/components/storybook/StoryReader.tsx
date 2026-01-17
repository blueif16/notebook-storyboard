'use client';

import { useState, useEffect, useRef } from 'react';
import { gsap } from 'gsap';
import { motion, AnimatePresence } from 'framer-motion';
import Image from 'next/image';

interface StoryPage {
  imageUrl: string;
  text: string;
}

interface StoryReaderProps {
  pages: StoryPage[];
  onHome: () => void;
}

const pageVariants = {
  enter: (direction: number) => ({
    x: direction > 0 ? 300 : -300,
    opacity: 0,
    rotateY: direction > 0 ? 15 : -15,
  }),
  center: {
    x: 0,
    opacity: 1,
    rotateY: 0,
    transition: {
      duration: 0.5,
      ease: [0.25, 0.1, 0.25, 1] as any,
    }
  },
  exit: (direction: number) => ({
    x: direction > 0 ? -300 : 300,
    opacity: 0,
    rotateY: direction > 0 ? -15 : 15,
    transition: {
      duration: 0.4,
      ease: [0.25, 0.1, 0.25, 1] as any,
    }
  })
};

export function StoryReader({ pages, onHome }: StoryReaderProps) {
  const [currentPage, setCurrentPage] = useState(0);
  const [direction, setDirection] = useState(0);
  const containerRef = useRef<HTMLDivElement>(null);

  const isLastPage = currentPage === pages.length - 1;

  const goToPage = (newPage: number) => {
    if (newPage < 0 || newPage >= pages.length) return;
    setDirection(newPage > currentPage ? 1 : -1);
    setCurrentPage(newPage);
  };

  // Fade header on scroll/interaction
  useEffect(() => {
    let timeout: NodeJS.Timeout;

    const handleActivity = () => {
      gsap.to(".reader-header", {
        opacity: 1,
        duration: 0.3
      });

      clearTimeout(timeout);
      timeout = setTimeout(() => {
        gsap.to(".reader-header", {
          opacity: 0.3,
          duration: 0.3
        });
      }, 2000);
    };

    window.addEventListener('mousemove', handleActivity);
    window.addEventListener('touchstart', handleActivity);

    return () => {
      window.removeEventListener('mousemove', handleActivity);
      window.removeEventListener('touchstart', handleActivity);
      clearTimeout(timeout);
    };
  }, []);

  return (
    <div ref={containerRef} className="story-reader relative min-h-screen bg-[#F5F1E8]">
      {/* Minimal header - fades on scroll */}
      <header className="reader-header fixed top-0 left-0 right-0 flex justify-between items-center p-6 z-50 transition-opacity">
        <motion.button
          className="home-btn p-3 rounded-full bg-white/80 backdrop-blur-sm border-2 border-[#8B7355]"
          onClick={onHome}
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.95 }}
        >
          <Image src="/icons/home.png" alt="Home" width={24} height={24} />
        </motion.button>
        <span className="page-counter text-[#8B7355] font-medium bg-white/80 backdrop-blur-sm px-4 py-2 rounded-full">
          {currentPage + 1}/{pages.length}
        </span>
      </header>

      {/* Story content with page turns */}
      <div className="story-stage flex items-center justify-center min-h-screen px-6 py-20" style={{ perspective: 1200 }}>
        <AnimatePresence mode="wait" custom={direction}>
          <motion.article
            key={currentPage}
            custom={direction}
            variants={pageVariants}
            initial="enter"
            animate="center"
            exit="exit"
            className="story-page max-w-3xl w-full"
          >
            {/* Illustration with subtle frame */}
            <div className="illustration-frame relative bg-white rounded-3xl shadow-xl p-6 mb-8 border-4 border-[#8B7355]">
              <motion.img
                src={pages[currentPage].imageUrl}
                alt=""
                className="w-full h-auto rounded-2xl"
                initial={{ scale: 1.05, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: 0.2, duration: 0.4 }}
              />
            </div>

            {/* Story text */}
            <motion.div
              className="story-text-container bg-white rounded-3xl shadow-xl p-8 border-4 border-[#8B7355]"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3, duration: 0.4 }}
            >
              <p
                className="story-text text-xl leading-relaxed text-[#8B7355]"
                style={{ fontFamily: 'Georgia, serif' }}
              >
                {pages[currentPage].text}
              </p>
            </motion.div>
          </motion.article>
        </AnimatePresence>
      </div>

      {/* Navigation */}
      <nav className="reader-nav fixed bottom-8 left-1/2 -translate-x-1/2 flex items-center gap-6 bg-white/90 backdrop-blur-sm rounded-full px-6 py-4 shadow-xl border-2 border-[#8B7355]">
        <motion.button
          className="nav-arrow prev disabled:opacity-30"
          onClick={() => goToPage(currentPage - 1)}
          disabled={currentPage === 0}
          whileHover={currentPage > 0 ? { x: -5 } : {}}
          whileTap={currentPage > 0 ? { scale: 0.9 } : {}}
        >
          <Image src="/icons/right_arrow.png" alt="Previous" width={24} height={24} className="rotate-180" />
        </motion.button>

        {/* Page dots */}
        <div className="page-dots flex gap-2">
          {pages.map((_, i) => (
            <motion.button
              key={i}
              className={`page-dot w-3 h-3 rounded-full ${
                i === currentPage ? 'bg-[#8B7355]' : 'bg-[#D4C4B0]'
              }`}
              onClick={() => goToPage(i)}
              whileHover={{ scale: 1.3 }}
              animate={{
                scale: i === currentPage ? 1.2 : 1,
              }}
            />
          ))}
        </div>

        <motion.button
          className="nav-arrow next disabled:opacity-30"
          onClick={() => goToPage(currentPage + 1)}
          disabled={isLastPage}
          whileHover={!isLastPage ? { x: 5 } : {}}
          whileTap={!isLastPage ? { scale: 0.9 } : {}}
        >
          <Image src="/icons/right_arrow.png" alt="Next" width={24} height={24} />
        </motion.button>
      </nav>

      {/* "The End" celebration */}
      {isLastPage && <TheEndCelebration onHome={onHome} />}
    </div>
  );
}

function TheEndCelebration({ onHome }: { onHome: () => void }) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      const tl = gsap.timeline({ delay: 0.5 });

      // Confetti burst
      tl.fromTo(".confetti-piece",
        {
          opacity: 0,
          scale: 0,
          x: 0,
          y: 0,
          rotation: 0
        },
        {
          opacity: 1,
          scale: 1,
          x: () => gsap.utils.random(-150, 150),
          y: () => gsap.utils.random(-100, 50),
          rotation: () => gsap.utils.random(-180, 180),
          duration: 0.8,
          stagger: {
            each: 0.02,
            from: "center"
          },
          ease: "power2.out"
        }
      );

      // Confetti falls
      tl.to(".confetti-piece", {
        y: "+=200",
        opacity: 0,
        rotation: "+=180",
        duration: 2,
        stagger: 0.05,
        ease: "power1.in"
      }, "+=0.5");

      // "The End" text
      tl.fromTo(".the-end-text",
        { opacity: 0, y: 30, scale: 0.8 },
        {
          opacity: 1,
          y: 0,
          scale: 1,
          duration: 0.8,
          ease: "back.out(2)"
        },
        "-=1.5"
      );

      // Stars scatter
      tl.fromTo(".end-star",
        { opacity: 0, scale: 0 },
        {
          opacity: 1,
          scale: 1,
          duration: 0.4,
          stagger: 0.1,
          ease: "back.out(2)"
        },
        "-=0.8"
      );

      // Flower blooms
      tl.fromTo(".end-flower",
        { opacity: 0, scale: 0, rotation: -45 },
        {
          opacity: 1,
          scale: 1,
          rotation: 0,
          duration: 0.5,
          ease: "back.out(2)"
        },
        "-=0.3"
      );

      // CTAs fade up
      tl.fromTo(".end-cta",
        { opacity: 0, y: 20 },
        {
          opacity: 1,
          y: 0,
          duration: 0.4,
          stagger: 0.1
        },
        "-=0.2"
      );

    }, containerRef);

    return () => ctx.revert();
  }, []);

  return (
    <div ref={containerRef} className="the-end-celebration fixed inset-0 flex items-center justify-center bg-[#F5F1E8]/95 backdrop-blur-sm z-40">
      {/* Confetti */}
      <div className="confetti-container absolute inset-0 flex items-center justify-center">
        {[...Array(30)].map((_, i) => (
          <div
            key={i}
            className="confetti-piece absolute w-3 h-3 rounded-full"
            style={{
              backgroundColor: ['#7B9E89', '#D4A03D', '#C17C74', '#6B8FA3'][i % 4],
            }}
          />
        ))}
      </div>

      <div className="relative text-center">
        {/* Stars */}
        <Image src="/icons/stars.png" alt="" width={60} height={60} className="end-star absolute -top-20 left-1/2 -translate-x-1/2" />
        <Image src="/icons/stars.png" alt="" width={50} height={50} className="end-star absolute -top-10 -left-20" />
        <Image src="/icons/stars.png" alt="" width={50} height={50} className="end-star absolute -top-10 -right-20" />

        {/* The End */}
        <h2 className="the-end-text text-7xl font-bold text-[#8B7355] mb-8" style={{ fontFamily: 'Comic Sans MS, cursive' }}>
          The End
        </h2>

        {/* Flower */}
        <Image src="/icons/flower.png" alt="" width={80} height={80} className="end-flower mx-auto mb-8" />

        {/* CTAs */}
        <div className="end-actions flex flex-col gap-4 items-center">
          <motion.button
            className="end-cta flex items-center gap-2 px-8 py-3 rounded-full bg-white border-2 border-[#8B7355] text-[#8B7355]"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Image src="/icons/open_book.png" alt="" width={24} height={24} />
            Read again
          </motion.button>

          <motion.button
            className="end-cta flex items-center gap-2 px-8 py-3 rounded-full bg-[#6B8FA3] text-white border-2 border-[#8B7355]"
            onClick={onHome}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Image src="/icons/magic_wand.png" alt="" width={24} height={24} />
            Make another story
          </motion.button>

          <motion.button
            className="end-cta flex items-center gap-2 px-8 py-3 rounded-full bg-white border-2 border-[#8B7355] text-[#8B7355]"
            onClick={onHome}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Image src="/icons/home.png" alt="" width={24} height={24} />
            Go home
          </motion.button>
        </div>
      </div>
    </div>
  );
}
