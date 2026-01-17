import { motion } from 'framer-motion';
import { ReactNode } from 'react';

interface WobblyButtonProps {
  children: ReactNode;
  variant?: 'primary' | 'secondary';
  onClick?: () => void;
  disabled?: boolean;
  className?: string;
}

export function WobblyButton({
  children,
  variant = 'primary',
  onClick,
  disabled,
  className = ''
}: WobblyButtonProps) {
  const baseClasses = "relative px-8 py-3 rounded-full font-medium transition-all overflow-hidden";
  const variantClasses = variant === 'primary'
    ? "bg-[#6B8FA3] text-white border-2 border-[#8B7355]"
    : "bg-transparent text-[#8B7355] border-2 border-[#8B7355]";
  const disabledClasses = disabled ? "opacity-50 cursor-not-allowed" : "";

  return (
    <motion.button
      className={`${baseClasses} ${variantClasses} ${disabledClasses} ${className}`}
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
      <span className="relative z-10 flex items-center gap-2 justify-center">
        {children}
      </span>
    </motion.button>
  );
}
