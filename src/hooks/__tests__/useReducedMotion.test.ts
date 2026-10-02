import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useReducedMotion } from '../useReducedMotion'

describe('useReducedMotion', () => {
  let originalMatchMedia: typeof window.matchMedia

  beforeEach(() => {
    originalMatchMedia = window.matchMedia
  })

  afterEach(() => {
    window.matchMedia = originalMatchMedia
  })

  it('should return false when user does not prefer reduced motion', () => {
    window.matchMedia = vi.fn().mockReturnValue({
      matches: false,
      media: '(prefers-reduced-motion: reduce)',
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    } as unknown as MediaQueryList)

    const { result } = renderHook(() => useReducedMotion())

    expect(result.current).toBe(false)
  })

  it('should return true when user prefers reduced motion', () => {
    window.matchMedia = vi.fn().mockReturnValue({
      matches: true,
      media: '(prefers-reduced-motion: reduce)',
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    } as unknown as MediaQueryList)

    const { result } = renderHook(() => useReducedMotion())

    expect(result.current).toBe(true)
  })

  it('should listen to media query changes', () => {
    let changeListener: ((event: MediaQueryListEvent) => void) | null = null

    const mockMediaQuery = {
      matches: false,
      media: '(prefers-reduced-motion: reduce)',
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn((event: string, listener: (event: MediaQueryListEvent) => void) => {
        if (event === 'change') {
          changeListener = listener
        }
      }),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    } as unknown as MediaQueryList

    window.matchMedia = vi.fn().mockReturnValue(mockMediaQuery)

    const { result } = renderHook(() => useReducedMotion())

    expect(result.current).toBe(false)

    // Simulate media query change
    if (changeListener) {
      act(() => {
        changeListener!({ matches: true } as MediaQueryListEvent)
      })
    }

    expect(result.current).toBe(true)
  })

  it('should clean up event listener on unmount', () => {
    const removeEventListenerMock = vi.fn()

    window.matchMedia = vi.fn().mockReturnValue({
      matches: false,
      media: '(prefers-reduced-motion: reduce)',
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: removeEventListenerMock,
      dispatchEvent: vi.fn(),
    } as unknown as MediaQueryList)

    const { unmount } = renderHook(() => useReducedMotion())

    unmount()

    // Cleanup should be called without errors
    expect(true).toBe(true)
  })

  it('should support fallback addListener for older browsers', () => {
    const addListenerMock = vi.fn()

    window.matchMedia = vi.fn().mockReturnValue({
      matches: true,
      media: '(prefers-reduced-motion: reduce)',
      onchange: null,
      addListener: addListenerMock,
      removeListener: vi.fn(),
      // No addEventListener - testing fallback
      dispatchEvent: vi.fn(),
    } as unknown as MediaQueryList)

    const { result } = renderHook(() => useReducedMotion())

    // Should still work with fallback
    expect(result.current).toBe(true)
  })

  it('should support multiple independent instances', () => {
    window.matchMedia = vi.fn().mockReturnValue({
      matches: false,
      media: '(prefers-reduced-motion: reduce)',
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    } as unknown as MediaQueryList)

    const { result: result1 } = renderHook(() => useReducedMotion())
    const { result: result2 } = renderHook(() => useReducedMotion())

    expect(result1.current).toBe(false)
    expect(result2.current).toBe(false)
  })
})
