// Animation constants and easing functions

export const storybookEase = "power2.out";
export const magicEase = "back.out(1.4)";
export const floatEase = "sine.inOut";

export const softSpring = {
  type: "spring" as const,
  stiffness: 120,
  damping: 14
};

export const gentleBounce = {
  type: "spring" as const,
  stiffness: 200,
  damping: 20
};

export const pageVariants = {
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
      ease: [0.25, 0.1, 0.25, 1] as any,
      when: "beforeChildren" as const,
      staggerChildren: 0.1
    }
  },
  exit: {
    opacity: 0,
    x: -40,
    filter: "blur(4px)",
    transition: {
      duration: 0.3,
      ease: [0.25, 0.1, 0.25, 1] as any,
    }
  }
};
