import { useEffect, useRef } from 'react';
import { gsap } from 'gsap';

const stepColors = ['#D4A03D', '#7B9E89', '#C17C74']; // Mustard, Sage, Coral

export function ProgressIndicator({ step }: { step: 1 | 2 | 3 }) {
  const dotsRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.to(`.progress-dot:nth-child(${step})`, {
        backgroundColor: stepColors[step - 1],
        scale: 1.1,
        duration: 0.4,
        ease: "back.out(2)"
      });

      for (let i = 1; i < step; i++) {
        gsap.set(`.progress-dot:nth-child(${i})`, {
          backgroundColor: stepColors[i - 1]
        });
      }
    }, dotsRef);

    return () => ctx.revert();
  }, [step]);

  return (
    <div ref={dotsRef} className="progress-indicator flex gap-3 justify-center mb-8">
      <div className="progress-dot w-4 h-4 rounded-full border-2 border-[#8B7355] bg-[#F5F1E8]" />
      <div className="progress-dot w-4 h-4 rounded-full border-2 border-[#8B7355] bg-[#F5F1E8]" />
      <div className="progress-dot w-4 h-4 rounded-full border-2 border-[#8B7355] bg-[#F5F1E8]" />
    </div>
  );
}
