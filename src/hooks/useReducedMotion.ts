import { useState, useEffect } from 'react'

/**
 * Hook to detect and respond to prefers-reduced-motion media query
 *
 * Returns true if the user has enabled reduce-motion preferences in their OS.
 * Listens for changes to the media query and updates in real-time.
 *
 * @returns boolean - true if reduced motion is preferred, false otherwise
 */
export function useReducedMotion(): boolean {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState<boolean>(() => {
    // Initialize with current preference (SSR-safe check)
    if (typeof window === 'undefined') return false
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches
  })

  useEffect(() => {
    // Get the media query list
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)')

    // Create a listener function to handle changes
    const handleChange = (event: MediaQueryListEvent) => {
      setPrefersReducedMotion(event.matches)
    }

    // Add listener for media query changes
    // Support both modern addEventListener and legacy addListener
    if (mediaQuery.addEventListener) {
      mediaQuery.addEventListener('change', handleChange)
    } else {
      // Fallback for older browsers
      mediaQuery.addListener(handleChange)
    }

    // Cleanup: remove listener on unmount
    return () => {
      if (mediaQuery.removeEventListener) {
        mediaQuery.removeEventListener('change', handleChange)
      } else {
        // Fallback for older browsers
        mediaQuery.removeListener(handleChange)
      }
    }
  }, [])

  return prefersReducedMotion
}
