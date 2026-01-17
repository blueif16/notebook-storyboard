import { useEffect, useRef } from 'react';
import { gsap } from 'gsap';
import Image from 'next/image';

interface FloatingDecorationsProps {
  elements: Array<{
    src: string;
    className: string;
    style?: React.CSSProperties;
    alt?: string;
  }>;
}

export function FloatingDecorations({ elements }: FloatingDecorationsProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      elements.forEach((_, index) => {
        gsap.to(`.floating-${index}`, {
          y: `random(-12, 12)`,
          x: `random(-8, 8)`,
          rotation: `random(-10, 10)`,
          duration: gsap.utils.random(3, 5),
          repeat: -1,
          yoyo: true,
          ease: "sine.inOut",
          delay: index * 0.3
        });
      });
    }, containerRef);

    return () => ctx.revert();
  }, [elements]);

  return (
    <div ref={containerRef} className="floating-decorations absolute inset-0 pointer-events-none">
      {elements.map((el, i) => (
        <Image
          key={i}
          src={el.src}
          alt={el.alt || ""}
          width={100}
          height={100}
          className={`${el.className} floating-${i} absolute`}
          style={el.style}
        />
      ))}
    </div>
  );
}
