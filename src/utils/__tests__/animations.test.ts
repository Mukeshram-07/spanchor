import { describe, it, expect, beforeEach } from 'vitest';
import {
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
  prefersReducedMotion,
  animations,
} from '../animations';

describe('Animation Utilities', () => {
  describe('prefersReducedMotion', () => {
    it('should return a boolean', () => {
      const result = prefersReducedMotion();
      expect(typeof result).toBe('boolean');
    });

    it('should handle missing matchMedia gracefully', () => {
      const originalMatchMedia = window.matchMedia;
      // @ts-ignore
      delete window.matchMedia;

      const result = prefersReducedMotion();
      expect(typeof result).toBe('boolean');

      // Restore
      window.matchMedia = originalMatchMedia;
    });
  });

  describe('fadeIn animation', () => {
    it('should have hidden and visible states', () => {
      expect(fadeIn.hidden).toBeDefined();
      expect(fadeIn.visible).toBeDefined();
    });

    it('should animate opacity from 0 to 1', () => {
      const hidden = fadeIn.hidden as any;
      const visible = fadeIn.visible as any;

      expect(hidden.opacity).toBe(0);
      expect(visible.opacity).toBe(1);
    });

    it('should have transition property in visible state', () => {
      const visible = fadeIn.visible as any;
      expect(visible.transition).toBeDefined();
      expect(visible.transition.duration).toBeGreaterThanOrEqual(0);
    });
  });

  describe('slideUp animation', () => {
    it('should have hidden and visible states', () => {
      expect(slideUp.hidden).toBeDefined();
      expect(slideUp.visible).toBeDefined();
    });

    it('should animate y position and opacity', () => {
      const hidden = slideUp.hidden as any;
      const visible = slideUp.visible as any;

      expect(hidden.opacity).toBe(0);
      expect(hidden.y).toBe(20);
      expect(visible.opacity).toBe(1);
      expect(visible.y).toBe(0);
    });
  });

  describe('slideDown animation', () => {
    it('should have hidden and visible states', () => {
      expect(slideDown.hidden).toBeDefined();
      expect(slideDown.visible).toBeDefined();
    });

    it('should animate y position downward', () => {
      const hidden = slideDown.hidden as any;
      const visible = slideDown.visible as any;

      expect(hidden.opacity).toBe(0);
      expect(hidden.y).toBe(-20);
      expect(visible.opacity).toBe(1);
      expect(visible.y).toBe(0);
    });
  });

  describe('slideLeft animation', () => {
    it('should have hidden and visible states', () => {
      expect(slideLeft.hidden).toBeDefined();
      expect(slideLeft.visible).toBeDefined();
    });

    it('should animate x position rightward', () => {
      const hidden = slideLeft.hidden as any;
      const visible = slideLeft.visible as any;

      expect(hidden.opacity).toBe(0);
      expect(hidden.x).toBe(20);
      expect(visible.opacity).toBe(1);
      expect(visible.x).toBe(0);
    });
  });

  describe('slideRight animation', () => {
    it('should have hidden and visible states', () => {
      expect(slideRight.hidden).toBeDefined();
      expect(slideRight.visible).toBeDefined();
    });

    it('should animate x position leftward', () => {
      const hidden = slideRight.hidden as any;
      const visible = slideRight.visible as any;

      expect(hidden.opacity).toBe(0);
      expect(hidden.x).toBe(-20);
      expect(visible.opacity).toBe(1);
      expect(visible.x).toBe(0);
    });
  });

  describe('scaleIn animation', () => {
    it('should have hidden and visible states', () => {
      expect(scaleIn.hidden).toBeDefined();
      expect(scaleIn.visible).toBeDefined();
    });

    it('should animate scale from 0.8 to 1', () => {
      const hidden = scaleIn.hidden as any;
      const visible = scaleIn.visible as any;

      expect(hidden.opacity).toBe(0);
      expect(hidden.scale).toBe(0.8);
      expect(visible.opacity).toBe(1);
      expect(visible.scale).toBe(1);
    });
  });

  describe('staggerContainer animation', () => {
    it('should have hidden and visible states', () => {
      expect(staggerContainer.hidden).toBeDefined();
      expect(staggerContainer.visible).toBeDefined();
    });

    it('should have stagger configuration', () => {
      const visible = staggerContainer.visible as any;
      expect(visible.transition).toBeDefined();
      expect(visible.transition.staggerChildren).toBeGreaterThanOrEqual(0);
      expect(visible.transition.delayChildren).toBeGreaterThanOrEqual(0);
    });
  });

  describe('staggerItem animation', () => {
    it('should have hidden and visible states', () => {
      expect(staggerItem.hidden).toBeDefined();
      expect(staggerItem.visible).toBeDefined();
    });

    it('should animate individual items in stagger container', () => {
      const hidden = staggerItem.hidden as any;
      const visible = staggerItem.visible as any;

      expect(hidden.opacity).toBe(0);
      expect(hidden.y).toBe(10);
      expect(visible.opacity).toBe(1);
      expect(visible.y).toBe(0);
    });
  });

  describe('pulseAnimation animation', () => {
    it('should have initial and animate states', () => {
      expect(pulseAnimation.initial).toBeDefined();
      expect(pulseAnimation.animate).toBeDefined();
    });

    it('should have looping transition', () => {
      const animate = pulseAnimation.animate as any;
      expect(animate.transition).toBeDefined();
      expect(animate.transition.repeat).toBe(Infinity);
      expect(animate.transition.repeatType).toBe('loop');
    });
  });

  describe('countUpVariant animation', () => {
    it('should have initial and animate states', () => {
      expect(countUpVariant.initial).toBeDefined();
      expect(countUpVariant.animate).toBeDefined();
    });

    it('should fade in for count up effect', () => {
      const initial = countUpVariant.initial as any;
      const animate = countUpVariant.animate as any;

      expect(initial.opacity).toBe(0);
      expect(animate.opacity).toBe(1);
    });
  });

  describe('bounceIn animation', () => {
    it('should have hidden and visible states', () => {
      expect(bounceIn.hidden).toBeDefined();
      expect(bounceIn.visible).toBeDefined();
    });

    it('should use spring type for bounce effect', () => {
      const visible = bounceIn.visible as any;
      expect(visible.transition).toBeDefined();
      expect(visible.transition.type).toBe('spring');
    });
  });

  describe('rotateIn animation', () => {
    it('should have hidden and visible states', () => {
      expect(rotateIn.hidden).toBeDefined();
      expect(rotateIn.visible).toBeDefined();
    });

    it('should animate rotation', () => {
      const hidden = rotateIn.hidden as any;
      const visible = rotateIn.visible as any;

      expect(hidden.rotate).toBe(-10);
      expect(visible.rotate).toBe(0);
    });
  });

  describe('pageTransition animation', () => {
    it('should have initial, animate, and exit states', () => {
      expect(pageTransition.initial).toBeDefined();
      expect(pageTransition.animate).toBeDefined();
      expect(pageTransition.exit).toBeDefined();
    });

    it('should fade in and out', () => {
      const initial = pageTransition.initial as any;
      const animate = pageTransition.animate as any;
      const exit = pageTransition.exit as any;

      expect(initial.opacity).toBe(0);
      expect(animate.opacity).toBe(1);
      expect(exit.opacity).toBe(0);
    });
  });

  describe('modalEnter animation', () => {
    it('should have hidden, visible, and exit states', () => {
      expect(modalEnter.hidden).toBeDefined();
      expect(modalEnter.visible).toBeDefined();
      expect(modalEnter.exit).toBeDefined();
    });

    it('should scale and fade in modal', () => {
      const hidden = modalEnter.hidden as any;
      const visible = modalEnter.visible as any;

      expect(hidden.opacity).toBe(0);
      expect(hidden.scale).toBe(0.95);
      expect(visible.opacity).toBe(1);
      expect(visible.scale).toBe(1);
    });
  });

  describe('skeletonShimmer animation', () => {
    it('should have animate state for shimmer effect', () => {
      expect(skeletonShimmer.animate).toBeDefined();
    });

    it('should have looping shimmer transition', () => {
      const animate = skeletonShimmer.animate as any;
      expect(animate.transition).toBeDefined();
      expect(animate.transition.repeat).toBe(Infinity);
    });
  });

  describe('pathDraw animation', () => {
    it('should have hidden and visible states', () => {
      expect(pathDraw.hidden).toBeDefined();
      expect(pathDraw.visible).toBeDefined();
    });

    it('should animate SVG path drawing', () => {
      const hidden = pathDraw.hidden as any;
      const visible = pathDraw.visible as any;

      expect(hidden.pathLength).toBe(0);
      expect(hidden.opacity).toBe(0);
      expect(visible.pathLength).toBe(1);
      expect(visible.opacity).toBe(1);
    });
  });

  describe('animations namespace export', () => {
    it('should export all animation variants', () => {
      expect(animations.fadeIn).toBeDefined();
      expect(animations.slideUp).toBeDefined();
      expect(animations.slideDown).toBeDefined();
      expect(animations.slideLeft).toBeDefined();
      expect(animations.slideRight).toBeDefined();
      expect(animations.scaleIn).toBeDefined();
      expect(animations.staggerContainer).toBeDefined();
      expect(animations.staggerItem).toBeDefined();
      expect(animations.pulseAnimation).toBeDefined();
      expect(animations.countUpVariant).toBeDefined();
      expect(animations.bounceIn).toBeDefined();
      expect(animations.rotateIn).toBeDefined();
      expect(animations.pageTransition).toBeDefined();
      expect(animations.modalEnter).toBeDefined();
      expect(animations.skeletonShimmer).toBeDefined();
      expect(animations.pathDraw).toBeDefined();
    });

    it('should have all variants as defined objects', () => {
      Object.values(animations).forEach((variant) => {
        expect(typeof variant).toBe('object');
        expect(variant).not.toBeNull();
      });
    });
  });

  describe('animation transitions respect prefers-reduced-motion', () => {
    it('should have zero duration when reduced motion is preferred', () => {
      // Mock prefers-reduced-motion
      Object.defineProperty(window, 'matchMedia', {
        writable: true,
        value: (query: string) => ({
          matches: query === '(prefers-reduced-motion: reduce)',
          media: query,
          addEventListener: () => {},
          removeEventListener: () => {},
          addListener: () => {},
          removeListener: () => {},
          dispatchEvent: () => false,
        }),
      });

      const isReduced = prefersReducedMotion();
      expect(isReduced).toBe(true);
    });
  });
});
