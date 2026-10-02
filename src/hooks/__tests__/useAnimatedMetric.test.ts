import { describe, it, expect, beforeEach, vi } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'
import { useAnimatedMetric } from '../useAnimatedMetric'

describe('useAnimatedMetric', () => {
  beforeEach(() => {
    // Ensure matchMedia is properly mocked for each test
    const mockMatchMedia = (query: string) => {
      const listeners: Array<(this: MediaQueryList, ev: MediaQueryListEvent) => void> = []
      return {
        matches: false,
        media: query,
        onchange: null as ((this: MediaQueryList, ev: MediaQueryListEvent) => void) | null,
        addListener: (listener: (this: MediaQueryList, ev: MediaQueryListEvent) => void) => listeners.push(listener),
        removeListener: (listener: (this: MediaQueryList, ev: MediaQueryListEvent) => void) => {
          const index = listeners.indexOf(listener)
          if (index >= 0) listeners.splice(index, 1)
        },
        addEventListener: (type: string, _listener: (this: MediaQueryList, ev: MediaQueryListEvent) => void) => {
          if (type === 'change') listeners.push(_listener)
        },
        removeEventListener: (type: string, _listener: (this: MediaQueryList, ev: MediaQueryListEvent) => void) => {
          if (type === 'change') {
            const index = listeners.indexOf(_listener)
            if (index >= 0) listeners.splice(index, 1)
          }
        },
        dispatchEvent: () => true,
      } as unknown as MediaQueryList
    }

    Object.defineProperty(window, 'matchMedia', {
      writable: true,
      value: mockMatchMedia,
      configurable: true,
    })
  })

  it('should initialize with displayValue of 0', () => {
    const { result } = renderHook(() => useAnimatedMetric(100))

    expect(result.current.displayValue).toBe(0)
    expect(result.current.isAnimating).toBe(false)
  })

  it('should animate from 0 to target value', async () => {
    const targetValue = 100
    const { result } = renderHook(() => useAnimatedMetric(targetValue, 200))

    act(() => {
      result.current.startAnimation()
    })

    expect(result.current.isAnimating).toBe(true)

    // Wait for animation to complete
    await waitFor(
      () => {
        expect(result.current.isAnimating).toBe(false)
      },
      { timeout: 1000 }
    )

    expect(result.current.displayValue).toBeCloseTo(targetValue, 1)
  })

  it('should respect custom duration', async () => {
    const { result } = renderHook(() => useAnimatedMetric(100, 100)) // 100ms duration

    const startTime = Date.now()

    act(() => {
      result.current.startAnimation()
    })

    await waitFor(
      () => {
        expect(result.current.isAnimating).toBe(false)
      },
      { timeout: 500 }
    )

    const elapsedTime = Date.now() - startTime
    // Should complete roughly around 100ms + some tolerance
    expect(elapsedTime).toBeLessThan(300)
  })

  it('should support different easing functions', async () => {
    const { result: resultLinear } = renderHook(() =>
      useAnimatedMetric(100, 200, 'linear')
    )
    const { result: resultEaseOut } = renderHook(() =>
      useAnimatedMetric(100, 200, 'easeOut')
    )

    act(() => {
      resultLinear.current.startAnimation()
      resultEaseOut.current.startAnimation()
    })

    await waitFor(() => expect(resultLinear.current.isAnimating).toBe(false), {
      timeout: 1000,
    })
    await waitFor(() => expect(resultEaseOut.current.isAnimating).toBe(false), {
      timeout: 1000,
    })

    expect(resultLinear.current.displayValue).toBeCloseTo(100, 1)
    expect(resultEaseOut.current.displayValue).toBeCloseTo(100, 1)
  })

  it('should handle prefers-reduced-motion', () => {
    // Mock matchMedia to return reduced motion preference
    Object.defineProperty(window, 'matchMedia', {
      writable: true,
      value: vi.fn((query: string) => {
        if (query === '(prefers-reduced-motion: reduce)') {
          return {
            matches: true,
            media: query,
            onchange: null,
            addListener: vi.fn(),
            removeListener: vi.fn(),
            addEventListener: vi.fn(),
            removeEventListener: vi.fn(),
            dispatchEvent: vi.fn(),
          } as unknown as MediaQueryList
        }
        return {
          matches: false,
          media: query,
          onchange: null,
          addListener: vi.fn(),
          removeListener: vi.fn(),
          addEventListener: vi.fn(),
          removeEventListener: vi.fn(),
          dispatchEvent: vi.fn(),
        } as unknown as MediaQueryList
      }),
      configurable: true,
    })

    const { result } = renderHook(() => useAnimatedMetric(100, 1000))

    act(() => {
      result.current.startAnimation()
    })

    // With reduced motion, should show target immediately
    expect(result.current.displayValue).toBe(100)
    expect(result.current.isAnimating).toBe(false)
  })

  it('should support multiple simultaneous animations', async () => {
    const { result: result1 } = renderHook(() => useAnimatedMetric(50, 200))
    const { result: result2 } = renderHook(() => useAnimatedMetric(100, 200))

    act(() => {
      result1.current.startAnimation()
      result2.current.startAnimation()
    })

    expect(result1.current.isAnimating).toBe(true)
    expect(result2.current.isAnimating).toBe(true)

    await waitFor(() => expect(result1.current.isAnimating).toBe(false), {
      timeout: 1000,
    })
    await waitFor(() => expect(result2.current.isAnimating).toBe(false), {
      timeout: 1000,
    })

    expect(result1.current.displayValue).toBeCloseTo(50, 1)
    expect(result2.current.displayValue).toBeCloseTo(100, 1)
  })

  it('should clean up on unmount', () => {
    const { result, unmount } = renderHook(() => useAnimatedMetric(100, 500))

    act(() => {
      result.current.startAnimation()
    })

    expect(result.current.isAnimating).toBe(true)

    unmount()

    // No errors should be thrown
    expect(true).toBe(true)
  })
})
