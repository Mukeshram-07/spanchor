import { useState, useEffect, useRef } from 'react'

/**
 * Hook to animate a metric value from 0 to target
 *
 * Uses timing-based animation to count from 0 to the target value.
 * Respects prefers-reduced-motion for accessibility.
 *
 * @param targetValue - The final value to animate to
 * @param duration - Animation duration in milliseconds (default 1500ms)
 * @param easing - Easing function to use (default 'easeOut')
 * @returns Object with displayValue, isAnimating, and startAnimation function
 */
export function useAnimatedMetric(
  targetValue: number,
  duration: number = 1500,
  easing: 'easeOut' | 'easeIn' | 'linear' = 'easeOut'
) {
  const [displayValue, setDisplayValue] = useState(0)
  const [isAnimating, setIsAnimating] = useState(false)
  const animationFrameRef = useRef<number | null>(null)
  const startTimeRef = useRef<number | null>(null)
  const isMountedRef = useRef(true)

  /**
   * Easing functions for smooth animation
   */
  const easingFunctions = {
    linear: (t: number) => t,
    easeOut: (t: number) => 1 - Math.pow(1 - t, 3),
    easeIn: (t: number) => t * t * t,
  }

  /**
   * Check if user prefers reduced motion
   */
  const prefersReducedMotion = (): boolean => {
    if (typeof window === 'undefined') return false
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches
  }

  /**
   * Animate the value using requestAnimationFrame
   */
  const animate = (currentTime: number) => {
    if (!startTimeRef.current) return

    const elapsed = currentTime - startTimeRef.current
    const progress = Math.min(elapsed / duration, 1)
    const easeFn = easingFunctions[easing]
    const easedProgress = easeFn(progress)
    const newValue = targetValue * easedProgress

    if (isMountedRef.current) {
      setDisplayValue(newValue)
    }

    if (progress < 1) {
      animationFrameRef.current = requestAnimationFrame(animate)
    } else {
      // Animation complete
      if (isMountedRef.current) {
        setDisplayValue(targetValue)
        setIsAnimating(false)
      }
      startTimeRef.current = null
    }
  }

  /**
   * Start animating from 0 to target value
   */
  const startAnimation = () => {
    // If user prefers reduced motion, skip animation
    if (prefersReducedMotion()) {
      setDisplayValue(targetValue)
      setIsAnimating(false)
      return
    }

    // Reset state and start animation
    setDisplayValue(0)
    setIsAnimating(true)
    startTimeRef.current = null

    const startAnimation = (currentTime: number) => {
      if (!startTimeRef.current) {
        startTimeRef.current = currentTime
      }
      animate(currentTime)
    }

    animationFrameRef.current = requestAnimationFrame(startAnimation)
  }

  /**
   * Cleanup on unmount
   */
  useEffect(() => {
    return () => {
      isMountedRef.current = false
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current)
      }
    }
  }, [])

  // If prefers-reduced-motion is set, show target value immediately
  useEffect(() => {
    const shouldReduceMotion = prefersReducedMotion()
    if (shouldReduceMotion) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setDisplayValue(targetValue)
      setIsAnimating(false)
    } else if (!shouldReduceMotion && targetValue !== 0) {
      // Re-enable animation if motion is re-enabled
      void targetValue // Use void to indicate intentional logic
    }
  }, [targetValue])

  return {
    displayValue,
    isAnimating,
    startAnimation,
  }
}
