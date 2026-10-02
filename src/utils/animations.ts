import type { Variants } from 'framer-motion';

/**
 * Utility function to check if user prefers reduced motion
 * Respects the prefers-reduced-motion media query
 */
export const prefersReducedMotion = (): boolean => {
  if (typeof window === 'undefined') return false;
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
};

/**
 * Fade In animation variant
 * Animates opacity from 0 to 1
 */
export const fadeIn: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      duration: prefersReducedMotion() ? 0 : 0.6,
    },
  },
};

/**
 * Slide Up animation variant
 * Animates from below with fade in effect
 */
export const slideUp: Variants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: prefersReducedMotion() ? 0 : 0.6,
      ease: 'easeOut',
    },
  },
};

/**
 * Slide Down animation variant
 * Animates from above with fade in effect
 */
export const slideDown: Variants = {
  hidden: { opacity: 0, y: -20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: prefersReducedMotion() ? 0 : 0.6,
      ease: 'easeOut',
    },
  },
};

/**
 * Slide Left animation variant
 * Animates from right with fade in effect
 */
export const slideLeft: Variants = {
  hidden: { opacity: 0, x: 20 },
  visible: {
    opacity: 1,
    x: 0,
    transition: {
      duration: prefersReducedMotion() ? 0 : 0.6,
      ease: 'easeOut',
    },
  },
};

/**
 * Slide Right animation variant
 * Animates from left with fade in effect
 */
export const slideRight: Variants = {
  hidden: { opacity: 0, x: -20 },
  visible: {
    opacity: 1,
    x: 0,
    transition: {
      duration: prefersReducedMotion() ? 0 : 0.6,
      ease: 'easeOut',
    },
  },
};

/**
 * Scale In animation variant
 * Animates scale from 0 to 1 with fade in effect
 */
export const scaleIn: Variants = {
  hidden: { opacity: 0, scale: 0.8 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: {
      duration: prefersReducedMotion() ? 0 : 0.6,
      ease: 'easeOut',
    },
  },
};

/**
 * Stagger Container animation variant
 * Staggered animation for children elements
 */
export const staggerContainer: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: prefersReducedMotion() ? 0 : 0.1,
      delayChildren: prefersReducedMotion() ? 0 : 0.2,
    },
  },
};

/**
 * Stagger Item animation variant
 * Individual item animation for use with staggerContainer
 */
export const staggerItem: Variants = {
  hidden: { opacity: 0, y: 10 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: prefersReducedMotion() ? 0 : 0.4,
    },
  },
};

/**
 * Pulse Animation variant
 * Looping pulse effect for attention-drawing elements
 */
export const pulseAnimation: Variants = {
  initial: { opacity: 1, scale: 1 },
  animate: {
    opacity: [1, 0.5, 1],
    scale: [1, 1.05, 1],
    transition: {
      duration: prefersReducedMotion() ? 0 : 2,
      repeat: Infinity,
      repeatType: 'loop',
    },
  },
};

/**
 * Count Up animation - for numeric animations
 * This is a special case that returns custom animation values
 * Used with Framer Motion's useMotionValue and useTransform
 */
export const countUpVariant: Variants = {
  initial: { opacity: 0 },
  animate: {
    opacity: 1,
    transition: {
      duration: prefersReducedMotion() ? 0 : 1.5,
    },
  },
};

/**
 * Bounce In animation variant
 * Scales in with a bounce effect
 */
export const bounceIn: Variants = {
  hidden: { opacity: 0, scale: 0 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: {
      duration: prefersReducedMotion() ? 0 : 0.6,
      type: 'spring',
      bounce: 0.5,
    },
  },
};

/**
 * Rotate In animation variant
 * Animates rotation with fade in
 */
export const rotateIn: Variants = {
  hidden: { opacity: 0, rotate: -10 },
  visible: {
    opacity: 1,
    rotate: 0,
    transition: {
      duration: prefersReducedMotion() ? 0 : 0.6,
      ease: 'easeOut',
    },
  },
};

/**
 * Page transition animation - for route changes
 * Fade transition between pages
 */
export const pageTransition: Variants = {
  initial: { opacity: 0 },
  animate: {
    opacity: 1,
    transition: {
      duration: prefersReducedMotion() ? 0 : 0.5,
    },
  },
  exit: {
    opacity: 0,
    transition: {
      duration: prefersReducedMotion() ? 0 : 0.3,
    },
  },
};

/**
 * Modal entrance animation
 * Fades and scales up smoothly
 */
export const modalEnter: Variants = {
  hidden: { opacity: 0, scale: 0.95, y: -10 },
  visible: {
    opacity: 1,
    scale: 1,
    y: 0,
    transition: {
      duration: prefersReducedMotion() ? 0 : 0.3,
      ease: 'easeOut',
    },
  },
  exit: {
    opacity: 0,
    scale: 0.95,
    y: -10,
    transition: {
      duration: prefersReducedMotion() ? 0 : 0.2,
    },
  },
};

/**
 * Skeleton loading animation
 * Shimmer effect for loading states
 */
export const skeletonShimmer: Variants = {
  animate: {
    backgroundPosition: ['200% 0', '-200% 0'],
    transition: {
      duration: prefersReducedMotion() ? 0 : 2,
      repeat: Infinity,
      repeatType: 'loop',
    },
  },
};

/**
 * Path drawing animation
 * Used for SVG path animations
 */
export const pathDraw: Variants = {
  hidden: { pathLength: 0, opacity: 0 },
  visible: {
    pathLength: 1,
    opacity: 1,
    transition: {
      duration: prefersReducedMotion() ? 0 : 1.5,
      ease: 'easeInOut',
    },
  },
};

/**
 * Export all animation variants as a namespace
 * This allows for easy import and organized access
 */
export const animations = {
  fadeIn,
  slideUp,
  slideDown,
  slideLeft,
  slideRight,
  scaleIn,
  staggerContainer,
  staggerItem,
  pulseAnimation,
  countUpVariant,
  bounceIn,
  rotateIn,
  pageTransition,
  modalEnter,
  skeletonShimmer,
  pathDraw,
};

export default animations;
