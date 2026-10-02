import { useState, useEffect, useRef, useCallback } from 'react'

/**
 * Represents a terminal line with metadata
 */
export interface TerminalLine {
  id: string
  text: string
  timestamp?: number
}

/**
 * Hook to animate terminal lines appearing sequentially
 *
 * Accepts an array of terminal lines and animates them appearing one by one
 * with a configurable delay between each line. Respects prefers-reduced-motion.
 *
 * @param lines - Array of terminal lines to animate
 * @param delayMs - Delay between each line in milliseconds (default 150ms)
 * @returns Object with visible lines, current line index, and control functions
 */
export function useExecutionTrace(
  lines: TerminalLine[],
  delayMs: number = 150
) {
  const [currentLineIndex, setCurrentLineIndex] = useState(0)
  const [visibleLines, setVisibleLines] = useState<TerminalLine[]>([])
  const [isRunning, setIsRunning] = useState(false)
  const timeoutRefs = useRef<ReturnType<typeof setTimeout>[]>([])
  const isMountedRef = useRef(true)

  /**
   * Check if user prefers reduced motion
   */
  const prefersReducedMotion = (): boolean => {
    if (typeof window === 'undefined') return false
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches
  }

  /**
   * Clear all scheduled timeouts
   */
  const clearTimeouts = useCallback(() => {
    timeoutRefs.current.forEach((timeout) => clearTimeout(timeout))
    timeoutRefs.current = []
  }, [])

  /**
   * Start the trace animation
   */
  const startTrace = useCallback(() => {
    clearTimeouts()
    setCurrentLineIndex(0)
    setVisibleLines([])
    setIsRunning(true)

    // If reduced motion is preferred, show all lines at once
    if (prefersReducedMotion()) {
      if (isMountedRef.current) {
        setVisibleLines(lines)
        setCurrentLineIndex(lines.length)
        setIsRunning(false)
      }
      return
    }

    // Schedule each line to appear
    lines.forEach((line, index) => {
      const timeout = setTimeout(() => {
        if (!isMountedRef.current) return

        setCurrentLineIndex(index + 1)
        setVisibleLines((prev) => [...prev, line])

        // Mark as complete when all lines are shown
        if (index === lines.length - 1) {
          if (isMountedRef.current) {
            setIsRunning(false)
          }
        }
      }, index * delayMs)

      timeoutRefs.current.push(timeout)
    })
  }, [lines, delayMs, clearTimeouts])

  /**
   * Stop the trace animation at current position
   */
  const stopTrace = useCallback(() => {
    clearTimeouts()
    setIsRunning(false)
  }, [clearTimeouts])

  /**
   * Reset the trace to initial state
   */
  const resetTrace = useCallback(() => {
    clearTimeouts()
    setCurrentLineIndex(0)
    setVisibleLines([])
    setIsRunning(false)
  }, [clearTimeouts])

  /**
   * Cleanup on unmount
   */
  useEffect(() => {
    return () => {
      isMountedRef.current = false
      clearTimeouts()
    }
  }, [clearTimeouts])

  return {
    currentLineIndex,
    visibleLines,
    isRunning,
    startTrace,
    stopTrace,
    resetTrace,
  }
}
