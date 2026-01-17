# Storybook WebUI — Animation Enhancement Guide

Based on your design philosophy of **"Guided Wonder"** and the storybook aesthetic, here's a comprehensive animation strategy that feels hand-drawn, magical, and immersive.

---

## Animation Philosophy

| Principle | Implementation |
|-----------|----------------|
| **Slow & Intentional** | Durations 0.4s–0.8s, soft easing |
| **Sequential Reveals** | Staggered timelines, never all-at-once |
| **Organic Motion** | Wobbly easing, slight overshoot, breathing rhythms |
| **Magic Moments** | Celebratory bursts at key milestones |
| **Invisible Chrome** | UI fades as content takes focus |

### Custom Easing (The "Storybook" Feel)
```javascript
// GSAP custom ease - slightly wobbly, like hand-drawn
const storybookEase = "power2.out";
const magicEase = "back.out(1.4)"; // Gentle overshoot
const floatEase = "sine.inOut"; // For breathing/floating

// Motion spring config - soft and playful
const softSpring = { type: "spring", stiffness: 120, damping: 14 };
const gentleBounce = { type: "spring", stiffness: 200, damping: 20 };
```

---

## Page 0: Landing — "Wonder, Invitation"

### Animation Sequence (Timeline)

```
0.0s ─────────────────────────────────────────────────────── 3.0s
     │                                                      │
     ├─ [0.0s] Cloud drifts in from left (opacity + x)
     ├─ [0.2s] Hero character fades up with scale
     ├─ [0.6s] Stars cluster twinkle in (staggered)
     ├─ [1.0s] Headline text reveals (per-character)
     ├─ [1.6s] Subtext fades in
     ├─ [2.0s] CTA button pops in with magic wand sparkle
     └─ [∞] Floating loop begins (stars, cloud drift)
```

### Implementation

```tsx
// components/LandingPage.tsx
import { useEffect, useRef } from 'react';
import { gsap } from 'gsap';
import { SplitText } from 'gsap/SplitText';
import { motion } from 'motion/react';

gsap.registerPlugin(SplitText);

export function LandingPage() {
  const containerRef = useRef<HTMLDivElement>(null);
  const headlineRef = useRef<HTMLHeadingElement>(null);
  
  useEffect(() => {
    const ctx = gsap.context(() => {
      // Master timeline for sequenced entrance
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
      
      // 4. Headline text reveal (SplitText)
      if (headlineRef.current) {
        const split = SplitText.create(headlineRef.current, {
          type: "chars",
          charsClass: "char"
        });
        
        tl.fromTo(split.chars,
          { opacity: 0, y: 30, rotationX: -40 },
          {
            opacity: 1,
            y: 0,
            rotationX: 0,
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
    <div ref={containerRef} className="landing-page">
      {/* Decorative elements */}
      <img src="/cloud.svg" className="cloud" alt="" />
      <img src="/star-1.svg" className="star star-1" alt="" />
      <img src="/star-2.svg" className="star star-2" alt="" />
      <img src="/star-3.svg" className="star star-3" alt="" />
      
      {/* Hero */}
      <img 
        src="/hero-character.svg" 
        className="hero-character" 
        alt="Character sitting on magical books"
      />
      
      {/* Text */}
      <h1 ref={headlineRef} className="headline">
        Let's make a story together
      </h1>
      <p className="subtext">Create magical bedtime stories in minutes</p>
      
      {/* CTA */}
      <div className="swirl" />
      <motion.button 
        className="cta-button"
        whileHover={{ scale: 1.05, y: -2 }}
        whileTap={{ scale: 0.98 }}
        transition={softSpring}
      >
        <MagicWandIcon />
        Begin
      </motion.button>
    </div>
  );
}
```

### Floating Decorations Component

```tsx
// components/FloatingDecorations.tsx
import { useEffect, useRef } from 'react';
import { gsap } from 'gsap';

interface FloatingDecorationsProps {
  elements: Array<{
    src: string;
    className: string;
    style?: React.CSSProperties;
  }>;
}

export function FloatingDecorations({ elements }: FloatingDecorationsProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    const ctx = gsap.context(() => {
      // Each element gets its own floating rhythm
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
    <div ref={containerRef} className="floating-decorations">
      {elements.map((el, i) => (
        <img 
          key={i}
          src={el.src}
          className={`${el.className} floating-${i}`}
          style={el.style}
          alt=""
        />
      ))}
    </div>
  );
}
```

---

## Page Transitions — "Turning Pages"

### Shared Layout Wrapper

```tsx
// components/PageTransition.tsx
import { motion, AnimatePresence } from 'motion/react';
import { useRouter } from 'next/router';

const pageVariants = {
  initial: { 
    opacity: 0, 
    x: 60,
    filter: "blur(4px)"
  },
  enter: { 
    opacity: 1, 
    x: 0,
    filter: "blur(0px)",
    transition: {
      duration: 0.4,
      ease: [0.25, 0.1, 0.25, 1], // Soft ease
      when: "beforeChildren",
      staggerChildren: 0.1
    }
  },
  exit: { 
    opacity: 0, 
    x: -40,
    filter: "blur(4px)",
    transition: {
      duration: 0.3,
      ease: [0.25, 0.1, 0.25, 1]
    }
  }
};

export function PageTransition({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  
  return (
    <AnimatePresence mode="wait">
      <motion.main
        key={router.asPath}
        variants={pageVariants}
        initial="initial"
        animate="enter"
        exit="exit"
        className="page-container"
      >
        {children}
      </motion.main>
    </AnimatePresence>
  );
}
```

### GSAP Page Transition (More Control)

```tsx
// hooks/usePageTransition.ts
import { gsap } from 'gsap';
import { useRouter } from 'next/router';

export function usePageTransition() {
  const router = useRouter();
  
  const animateOut = (href: string) => {
    const tl = gsap.timeline({
      onComplete: () => router.push(href)
    });
    
    // Page content slides out like turning a page
    tl.to(".page-content", {
      opacity: 0,
      x: -50,
      duration: 0.3,
      ease: "power2.in"
    });
    
    // Optional: overlay slides in
    tl.fromTo(".page-overlay",
      { scaleX: 0, transformOrigin: "right" },
      { scaleX: 1, duration: 0.3, ease: "power2.inOut" },
      "-=0.1"
    );
    
    return tl;
  };
  
  const animateIn = () => {
    const tl = gsap.timeline();
    
    // Overlay slides out
    tl.to(".page-overlay", {
      scaleX: 0,
      transformOrigin: "left",
      duration: 0.3,
      ease: "power2.inOut"
    });
    
    // Content slides in
    tl.fromTo(".page-content",
      { opacity: 0, x: 50 },
      { opacity: 1, x: 0, duration: 0.4, ease: "power2.out" },
      "-=0.1"
    );
    
    return tl;
  };
  
  return { animateOut, animateIn };
}
```

---

## Page 1: Record Style — "Playful Exploration"

### Animation Sequence

```
0.0s ─────────────────────────────────────────────────────── 1.5s
     │
     ├─ [0.0s] Progress dots appear (staggered)
     ├─ [0.2s] Card "placed down" animation (scale + shadow)
     ├─ [0.5s] Paintbrush icon draws itself
     ├─ [0.7s] Content fades up inside card
     ├─ [1.0s] Decorative dots cluster breathes
     └─ [∞] Microphone pulse when recording
```

### Implementation

```tsx
// components/StyleConfigPage.tsx
import { useEffect, useRef, useState } from 'react';
import { gsap } from 'gsap';
import { motion } from 'motion/react';

export function StyleConfigPage() {
  const cardRef = useRef<HTMLDivElement>(null);
  const [isRecording, setIsRecording] = useState(false);
  
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
      
      tl.to(".progress-dot:first-child", {
        backgroundColor: "#D4A03D", // Mustard
        duration: 0.3
      }, "-=0.2");
      
      // Card "placed down" - feels like setting a page on a table
      tl.fromTo(".config-card",
        { 
          opacity: 0, 
          y: -20, 
          scale: 0.95,
          boxShadow: "0 0 0 rgba(0,0,0,0)"
        },
        { 
          opacity: 1, 
          y: 0, 
          scale: 1,
          boxShadow: "0 8px 32px rgba(139, 115, 85, 0.15)",
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
      gsap.to(".dots-cluster circle", {
        scale: gsap.utils.wrap([1.1, 0.9, 1.15, 0.85]),
        opacity: gsap.utils.wrap([0.8, 1, 0.7, 0.9]),
        duration: gsap.utils.wrap([2, 2.5, 1.8, 2.2]),
        repeat: -1,
        yoyo: true,
        ease: "sine.inOut",
        stagger: 0.3
      });
      
    }, cardRef);
    
    return () => ctx.revert();
  }, []);
  
  // Recording pulse animation
  useEffect(() => {
    if (isRecording) {
      gsap.to(".sound-wave", {
        scale: gsap.utils.wrap([1, 1.3, 1.1, 1.4, 1]),
        opacity: gsap.utils.wrap([1, 0.7, 1, 0.6, 1]),
        duration: 0.4,
        repeat: -1,
        stagger: 0.1,
        ease: "sine.inOut"
      });
    } else {
      gsap.to(".sound-wave", {
        scale: 1,
        opacity: 0.5,
        duration: 0.3
      });
    }
  }, [isRecording]);
  
  return (
    <div ref={cardRef} className="style-page">
      {/* Progress Indicator */}
      <div className="progress-indicator">
        <div className="progress-dot" />
        <div className="progress-dot" />
        <div className="progress-dot" />
      </div>
      
      {/* Main Card */}
      <div className="config-card wobbly-border">
        <div className="card-content">
          <div className="section-header">
            <PaintbrushIcon />
            <h2>Choose your style</h2>
          </div>
          
          {/* Style options */}
          <div className="style-options">
            {/* Style cards with hover animation */}
            {styles.map((style, i) => (
              <motion.button
                key={style.id}
                className="style-option"
                whileHover={{ 
                  scale: 1.03, 
                  y: -4,
                  boxShadow: "0 12px 24px rgba(139, 115, 85, 0.2)"
                }}
                whileTap={{ scale: 0.98 }}
                transition={{ type: "spring", stiffness: 300, damping: 20 }}
              >
                {style.label}
              </motion.button>
            ))}
          </div>
          
          {/* Voice Recording */}
          <div className="voice-section">
            <motion.button
              className="mic-button"
              onClick={() => setIsRecording(!isRecording)}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <MicrophoneIcon />
              {/* Sound wave dots */}
              <div className="sound-waves">
                {[...Array(5)].map((_, i) => (
                  <span key={i} className="sound-wave" />
                ))}
              </div>
            </motion.button>
            <MusicalNotesDecoration />
          </div>
        </div>
        
        {/* Decorative cluster */}
        <DotsCluster className="dots-cluster" />
      </div>
      
      {/* Navigation */}
      <nav className="page-nav">
        <motion.button 
          className="nav-back"
          whileHover={{ x: -3 }}
          whileTap={{ scale: 0.95 }}
        >
          <HomeIcon />
        </motion.button>
        <motion.button 
          className="nav-next"
          whileHover={{ x: 3, scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <ArrowRightIcon />
        </motion.button>
      </nav>
    </div>
  );
}
```

---

## Page 2: Write Brief — "Focused Creativity"

### Animation Sequence

```
0.0s ─────────────────────────────────────────────────────── 1.2s
     │
     ├─ [0.0s] Progress dot 2 fills (sage green)
     ├─ [0.2s] Card rises gently
     ├─ [0.4s] Pencil icon "draws" into place
     ├─ [0.5s] Text area fades in
     ├─ [0.7s] Placeholder text types itself (optional)
     └─ [∞] Stars near submit twinkle when input valid
```

### Typing Placeholder Effect

```tsx
// components/TypingPlaceholder.tsx
import { useEffect, useRef, useState } from 'react';
import { gsap } from 'gsap';

export function BriefInputPage() {
  const textAreaRef = useRef<HTMLTextAreaElement>(null);
  const [inputValue, setInputValue] = useState('');
  const [isValid, setIsValid] = useState(false);
  
  // Placeholder typing animation
  useEffect(() => {
    const placeholders = [
      "Once upon a time...",
      "In a land far away...",
      "There once lived a...",
    ];
    
    let currentIndex = 0;
    
    const typePlaceholder = () => {
      if (!textAreaRef.current || inputValue) return;
      
      const text = placeholders[currentIndex];
      let charIndex = 0;
      
      const typeChar = () => {
        if (charIndex <= text.length && !inputValue) {
          textAreaRef.current!.placeholder = text.slice(0, charIndex);
          charIndex++;
          gsap.delayedCall(0.08, typeChar);
        } else {
          // Pause, then clear and type next
          gsap.delayedCall(2, () => {
            currentIndex = (currentIndex + 1) % placeholders.length;
            typePlaceholder();
          });
        }
      };
      
      typeChar();
    };
    
    typePlaceholder();
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
    <div className="brief-page">
      {/* Progress - second dot green */}
      <ProgressIndicator step={2} />
      
      <motion.div 
        className="brief-card wobbly-border"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: [0.25, 0.1, 0.25, 1] }}
      >
        <motion.div 
          className="pencil-icon"
          initial={{ opacity: 0, x: -10, rotate: -20 }}
          animate={{ opacity: 1, x: 0, rotate: 0 }}
          transition={{ delay: 0.3, duration: 0.4 }}
        >
          <PencilIcon />
        </motion.div>
        
        <motion.textarea
          ref={textAreaRef}
          className="story-input"
          value={inputValue}
          onChange={(e) => {
            setInputValue(e.target.value);
            setIsValid(e.target.value.length > 20);
          }}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4, duration: 0.4 }}
        />
        
        {/* Decorative swirl */}
        <motion.div 
          className="swirl-decoration"
          initial={{ opacity: 0, scale: 0.5 }}
          animate={{ opacity: 0.6, scale: 1 }}
          transition={{ delay: 0.6, duration: 0.5 }}
        />
      </motion.div>
      
      {/* Submit with stars */}
      <div className="submit-area">
        <Star className="submit-star star-1" />
        <Star className="submit-star star-2" />
        <Star className="submit-star star-3" />
        
        <motion.button
          className="create-button"
          disabled={!isValid}
          whileHover={isValid ? { scale: 1.05 } : {}}
          whileTap={isValid ? { scale: 0.98 } : {}}
        >
          <MagicWandIcon />
          Create
        </motion.button>
      </div>
    </div>
  );
}
```

---

## Loading / Generation State — "Magic Happening"

### The Magical Loading Screen

```tsx
// components/GenerationLoading.tsx
import { useEffect, useRef, useState } from 'react';
import { gsap } from 'gsap';
import { SplitText } from 'gsap/SplitText';

gsap.registerPlugin(SplitText);

const loadingMessages = [
  "Dreaming up your story...",
  "Drawing your characters...",
  "Sprinkling in some magic...",
  "Almost there...",
];

export function GenerationLoading() {
  const containerRef = useRef<HTMLDivElement>(null);
  const messageRef = useRef<HTMLParagraphElement>(null);
  const [messageIndex, setMessageIndex] = useState(0);
  
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
      // Fade out current
      const split = SplitText.create(messageRef.current!, { type: "chars" });
      
      gsap.to(split.chars, {
        opacity: 0,
        y: -10,
        duration: 0.3,
        stagger: 0.02,
        ease: "power2.in",
        onComplete: () => {
          split.revert();
          setMessageIndex(prev => (prev + 1) % loadingMessages.length);
        }
      });
    };
    
    // Fade in new message
    const split = SplitText.create(messageRef.current, { type: "chars" });
    gsap.fromTo(split.chars,
      { opacity: 0, y: 10 },
      { 
        opacity: 1, 
        y: 0, 
        duration: 0.4, 
        stagger: 0.03,
        ease: "power2.out",
        onComplete: () => split.revert()
      }
    );
    
    const timer = setTimeout(animateMessage, 2500);
    return () => clearTimeout(timer);
    
  }, [messageIndex]);
  
  return (
    <div ref={containerRef} className="loading-screen">
      {/* Floating elements */}
      <img src="/moon.svg" className="moon" alt="" />
      
      <div className="stars-cluster">
        {[...Array(5)].map((_, i) => (
          <img 
            key={i}
            src="/star.svg" 
            className={`loading-star star-${i}`}
            alt="" 
          />
        ))}
      </div>
      
      <img src="/swirl.svg" className="swirl" alt="" />
      
      <div className="dots-cluster">
        {[...Array(4)].map((_, i) => (
          <span key={i} className="loading-dot" />
        ))}
      </div>
      
      {/* Cycling message */}
      <p ref={messageRef} className="loading-message handwritten">
        {loadingMessages[messageIndex]}
      </p>
    </div>
  );
}
```

---

## Page 3: Character Approval — "The Big Reveal"

### Animation Sequence

```
0.0s ─────────────────────────────────────────────────────── 2.0s
     │
     ├─ [0.0s] Frame "draws itself" (stroke animation)
     ├─ [0.3s] Character materializes (scale + blur + glow)
     ├─ [0.6s] Stars burst outward from character
     ├─ [1.0s] Action buttons fade up
     ├─ [1.3s] Flower accent pops in
     └─ [∞] Subtle glow pulse on character
```

### Implementation

```tsx
// components/CharacterApproval.tsx
import { useEffect, useRef } from 'react';
import { gsap } from 'gsap';
import { DrawSVGPlugin } from 'gsap/DrawSVGPlugin';
import { motion } from 'motion/react';

gsap.registerPlugin(DrawSVGPlugin);

export function CharacterApproval({ character }) {
  const containerRef = useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    const ctx = gsap.context(() => {
      const tl = gsap.timeline();
      
      // 1. Frame draws itself (wobbly border)
      tl.fromTo(".character-frame path",
        { drawSVG: "0%" },
        { 
          drawSVG: "100%", 
          duration: 0.8, 
          ease: "power2.inOut",
          stagger: 0.1
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
    // Exit animation before regenerating
    gsap.to(".character-image", {
      opacity: 0,
      scale: 0.9,
      filter: "blur(10px)",
      duration: 0.4,
      onComplete: () => {
        // Trigger regeneration
      }
    });
  };
  
  return (
    <div ref={containerRef} className="approval-page">
      <ProgressIndicator step={3} />
      
      {/* Character presentation */}
      <div className="character-stage">
        {/* Glow effect behind */}
        <div className="character-glow" />
        
        {/* Hand-drawn frame */}
        <svg className="character-frame">
          <path d="..." /> {/* Wobbly rectangle path */}
        </svg>
        
        {/* The character */}
        <img 
          src={character.imageUrl} 
          className="character-image"
          alt={character.name}
        />
        
        {/* Burst stars */}
        {[...Array(5)].map((_, i) => (
          <img 
            key={i}
            src="/star.svg"
            className={`reveal-star star-${i}`}
            alt=""
          />
        ))}
        
        {/* Flower accent */}
        <img src="/flower.svg" className="flower-accent" alt="" />
      </div>
      
      {/* Action buttons */}
      <div className="action-buttons">
        <motion.button
          className="try-again-btn"
          onClick={handleRegenerate}
          whileHover={{ scale: 1.03, x: -3 }}
          whileTap={{ scale: 0.97 }}
        >
          <RefreshIcon />
          Try again
        </motion.button>
        
        <motion.button
          className="approve-btn primary"
          whileHover={{ 
            scale: 1.05, 
            boxShadow: "0 8px 24px rgba(139, 115, 85, 0.3)"
          }}
          whileTap={{ scale: 0.98 }}
        >
          <CheckmarkIcon />
          Perfect!
          <HeartIcon className="heart-icon" />
        </motion.button>
      </div>
    </div>
  );
}
```

---

## Page 4: Story Reading — "Immersion"

### Page Turn Animation

```tsx
// components/StoryReader.tsx
import { useState, useEffect, useRef } from 'react';
import { gsap } from 'gsap';
import { motion, AnimatePresence } from 'motion/react';

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
      ease: [0.25, 0.1, 0.25, 1]
    }
  },
  exit: (direction: number) => ({
    x: direction > 0 ? -300 : 300,
    opacity: 0,
    rotateY: direction > 0 ? -15 : 15,
    transition: {
      duration: 0.4,
      ease: [0.25, 0.1, 0.25, 1]
    }
  })
};

export function StoryReader({ pages }) {
  const [currentPage, setCurrentPage] = useState(0);
  const [direction, setDirection] = useState(0);
  const containerRef = useRef<HTMLDivElement>(null);
  
  const isLastPage = currentPage === pages.length - 1;
  
  const goToPage = (newPage: number) => {
    setDirection(newPage > currentPage ? 1 : -1);
    setCurrentPage(newPage);
  };
  
  // Fade header on scroll/interaction
  useEffect(() => {
    const handleScroll = () => {
      gsap.to(".reader-header", {
        opacity: 0.3,
        duration: 0.3
      });
    };
    
    const handleIdle = () => {
      gsap.to(".reader-header", {
        opacity: 1,
        duration: 0.3
      });
    };
    
    // Implementation of scroll/idle detection...
  }, []);
  
  return (
    <div ref={containerRef} className="story-reader">
      {/* Minimal header - fades on scroll */}
      <header className="reader-header">
        <motion.button 
          className="home-btn"
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.95 }}
        >
          <HomeIcon />
        </motion.button>
        <span className="page-counter">{currentPage + 1}/{pages.length}</span>
      </header>
      
      {/* Story content with page turns */}
      <div className="story-stage" style={{ perspective: 1200 }}>
        <AnimatePresence mode="wait" custom={direction}>
          <motion.article
            key={currentPage}
            custom={direction}
            variants={pageVariants}
            initial="enter"
            animate="center"
            exit="exit"
            className="story-page"
          >
            {/* Illustration with subtle frame */}
            <div className="illustration-frame wobbly-border">
              <motion.img
                src={pages[currentPage].imageUrl}
                alt=""
                initial={{ scale: 1.05, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: 0.2, duration: 0.4 }}
              />
            </div>
            
            {/* Story text */}
            <motion.p
              className="story-text"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3, duration: 0.4 }}
            >
              {pages[currentPage].text}
            </motion.p>
          </motion.article>
        </AnimatePresence>
      </div>
      
      {/* Navigation */}
      <nav className="reader-nav">
        <motion.button
          className="nav-arrow prev"
          onClick={() => goToPage(currentPage - 1)}
          disabled={currentPage === 0}
          whileHover={{ x: -5 }}
          whileTap={{ scale: 0.9 }}
        >
          <ArrowLeftIcon />
        </motion.button>
        
        {/* Page dots */}
        <div className="page-dots">
          {pages.map((_, i) => (
            <motion.button
              key={i}
              className={`page-dot ${i === currentPage ? 'active' : ''}`}
              onClick={() => goToPage(i)}
              whileHover={{ scale: 1.3 }}
              animate={{
                scale: i === currentPage ? 1.2 : 1,
                backgroundColor: i === currentPage ? '#8B7355' : '#D4C4B0'
              }}
            />
          ))}
        </div>
        
        <motion.button
          className="nav-arrow next"
          onClick={() => goToPage(currentPage + 1)}
          disabled={isLastPage}
          whileHover={{ x: 5 }}
          whileTap={{ scale: 0.9 }}
        >
          <ArrowRightIcon />
        </motion.button>
      </nav>
      
      {/* "The End" celebration */}
      {isLastPage && <TheEndCelebration />}
    </div>
  );
}
```

### "The End" Celebration

```tsx
// components/TheEndCelebration.tsx
import { useEffect, useRef } from 'react';
import { gsap } from 'gsap';
import { SplitText } from 'gsap/SplitText';

export function TheEndCelebration() {
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
      const split = SplitText.create(".the-end-text", { type: "chars" });
      
      tl.fromTo(split.chars,
        { opacity: 0, y: 30, rotation: -15 },
        {
          opacity: 1,
          y: 0,
          rotation: 0,
          duration: 0.6,
          stagger: 0.05,
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
    <div ref={containerRef} className="the-end-celebration">
      {/* Confetti */}
      <div className="confetti-container">
        {[...Array(30)].map((_, i) => (
          <div 
            key={i} 
            className="confetti-piece"
            style={{
              backgroundColor: ['#7B9E89', '#D4A03D', '#C17C74', '#6B8FA3'][i % 4],
              width: gsap.utils.random(8, 16),
              height: gsap.utils.random(8, 16),
              borderRadius: i % 2 === 0 ? '50%' : '2px'
            }}
          />
        ))}
      </div>
      
      {/* Stars */}
      <img src="/star.svg" className="end-star star-1" alt="" />
      <img src="/star.svg" className="end-star star-2" alt="" />
      <img src="/star.svg" className="end-star star-3" alt="" />
      
      {/* The End */}
      <h2 className="the-end-text handwritten">The End</h2>
      
      {/* Flower */}
      <img src="/flower.svg" className="end-flower" alt="" />
      
      {/* CTAs */}
      <div className="end-actions">
        <motion.button 
          className="end-cta"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <OpenBookIcon />
          Read again
        </motion.button>
        
        <motion.button 
          className="end-cta primary"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <MagicWandIcon />
          Make another story
        </motion.button>
        
        <motion.button 
          className="end-cta"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <HomeIcon />
          Go home
        </motion.button>
      </div>
    </div>
  );
}
```

---

## Utility Components

### Progress Indicator

```tsx
// components/ProgressIndicator.tsx
import { useEffect, useRef } from 'react';
import { gsap } from 'gsap';

const stepColors = ['#D4A03D', '#7B9E89', '#C17C74']; // Mustard, Sage, Coral

export function ProgressIndicator({ step }: { step: 1 | 2 | 3 }) {
  const dotsRef = useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    const ctx = gsap.context(() => {
      // Animate the current step dot filling
      gsap.to(`.progress-dot:nth-child(${step})`, {
        backgroundColor: stepColors[step - 1],
        scale: 1.1,
        duration: 0.4,
        ease: "back.out(2)"
      });
      
      // Previous dots stay filled
      for (let i = 1; i < step; i++) {
        gsap.set(`.progress-dot:nth-child(${i})`, {
          backgroundColor: stepColors[i - 1]
        });
      }
    }, dotsRef);
    
    return () => ctx.revert();
  }, [step]);
  
  return (
    <div ref={dotsRef} className="progress-indicator">
      <svg className="progress-dot" viewBox="0 0 24 24">
        <circle cx="12" cy="12" r="10" className="wobbly-circle" />
      </svg>
      <svg className="progress-dot" viewBox="0 0 24 24">
        <circle cx="12" cy="12" r="10" className="wobbly-circle" />
      </svg>
      <svg className="progress-dot" viewBox="0 0 24 24">
        <circle cx="12" cy="12" r="10" className="wobbly-circle" />
      </svg>
    </div>
  );
}
```

### Wobbly Button Component

```tsx
// components/WobblyButton.tsx
import { motion } from 'motion/react';

interface WobblyButtonProps {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary';
  onClick?: () => void;
  disabled?: boolean;
}

export function WobblyButton({ 
  children, 
  variant = 'primary',
  onClick,
  disabled 
}: WobblyButtonProps) {
  return (
    <motion.button
      className={`wobbly-button ${variant}`}
      onClick={onClick}
      disabled={disabled}
      whileHover={!disabled ? { 
        scale: 1.03, 
        y: -2,
        boxShadow: "0 8px 20px rgba(139, 115, 85, 0.25)"
      } : {}}
      whileTap={!disabled ? { 
        scale: 0.98,
        y: 0
      } : {}}
      transition={{
        type: "spring",
        stiffness: 400,
        damping: 17
      }}
    >
      {/* Wobbly SVG border */}
      <svg className="button-border" viewBox="0 0 200 60" preserveAspectRatio="none">
        <path 
          d="M10,5 Q5,5 5,15 L5,45 Q5,55 15,55 L185,55 Q195,55 195,45 L195,15 Q195,5 185,5 Z"
          className="wobbly-path"
        />
      </svg>
      <span className="button-content">{children}</span>
    </motion.button>
  );
}
```

---

## CSS Keyframes for Subtle Effects

```css
/* styles/animations.css */

/* Wobbly float - for decorative elements */
@keyframes wobble-float {
  0%, 100% {
    transform: translateY(0) rotate(0deg);
  }
  25% {
    transform: translateY(-8px) rotate(2deg);
  }
  75% {
    transform: translateY(5px) rotate(-2deg);
  }
}

/* Gentle pulse - for glows and highlights */
@keyframes gentle-pulse {
  0%, 100% {
    opacity: 0.4;
    transform: scale(1);
  }
  50% {
    opacity: 0.7;
    transform: scale(1.05);
  }
}

/* Twinkle - for stars */
@keyframes twinkle {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.5;
    transform: scale(0.8);
  }
}

/* Hand-drawn path animation */
@keyframes draw-path {
  to {
    stroke-dashoffset: 0;
  }
}

/* Apply to elements */
.floating-decoration {
  animation: wobble-float 4s ease-in-out infinite;
}

.star-decoration {
  animation: twinkle 2s ease-in-out infinite;
  animation-delay: var(--delay, 0s);
}

.glow-effect {
  animation: gentle-pulse 3s ease-in-out infinite;
}
```

---

## Animation Timing Summary

| Page | Total Duration | Feel |
|------|----------------|------|
| Landing | ~3s entrance, ∞ floats | Magical, unhurried |
| Config 1 | ~1.5s entrance | Playful, inviting |
| Config 2 | ~1.2s entrance | Calm, focused |
| Loading | ∞ loop | Dreamy, anticipatory |
| Approval | ~2s reveal | Celebratory, proud |
| Reading | 0.5s per turn | Immersive, smooth |
| The End | ~2.5s celebration | Joyful, accomplished |

---

## Reduced Motion Support

```tsx
// hooks/useReducedMotion.ts
import { useEffect, useState } from 'react';
import { gsap } from 'gsap';

export function useReducedMotion() {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);
  
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setPrefersReducedMotion(mediaQuery.matches);
    
    if (mediaQuery.matches) {
      // Disable all GSAP animations
      gsap.globalTimeline.timeScale(0);
      // Or make them instant
      gsap.defaults({ duration: 0 });
    }
    
    const handler = (e: MediaQueryListEvent) => {
      setPrefersReducedMotion(e.matches);
    };
    
    mediaQuery.addEventListener('change', handler);
    return () => mediaQuery.removeEventListener('change', handler);
  }, []);
  
  return prefersReducedMotion;
}

// Usage in components
const prefersReducedMotion = useReducedMotion();

<motion.div
  animate={prefersReducedMotion ? {} : { x: 100 }}
/>
```

---

This animation system maintains the **hand-drawn, storybook aesthetic** while creating a **magical, immersive journey** through each configuration step. Every animation serves the emotional arc—from wonder at landing, through playful exploration, to the celebratory reveal of the finished story.