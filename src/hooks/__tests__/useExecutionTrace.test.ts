import { describe, it, expect, beforeEach, vi } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'
import { useExecutionTrace, type TerminalLine } from '../useExecutionTrace'

describe('useExecutionTrace', () => {
  const mockLines: TerminalLine[] = [
    { id: '1', text: '$ spanchor evaluate' },
    { id: '2', text: 'Loading gold set...' },
    { id: '3', text: '✓ 100 queries loaded' },
    { id: '4', text: 'Evaluating...' },
    { id: '5', text: '$ done' },
  ]

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

  it('should initialize with empty visible lines', () => {
    const { result } = renderHook(() => useExecutionTrace(mockLines))

    expect(result.current.visibleLines).toHaveLength(0)
    expect(result.current.currentLineIndex).toBe(0)
    expect(result.current.isRunning).toBe(false)
  })

  it('should animate lines appearing sequentially', async () => {
    const { result } = renderHook(() => useExecutionTrace(mockLines, 50))

    act(() => {
      result.current.startTrace()
    })

    expect(result.current.isRunning).toBe(true)

    // Wait for all lines to appear
    await waitFor(
      () => {
        expect(result.current.visibleLines).toHaveLength(mockLines.length)
      },
      { timeout: 2000 }
    )

    expect(result.current.currentLineIndex).toBe(mockLines.length)
    expect(result.current.isRunning).toBe(false)
  })

  it('should respect custom delay between lines', async () => {
    const { result } = renderHook(() => useExecutionTrace(mockLines, 30))

    const startTime = Date.now()

    act(() => {
      result.current.startTrace()
    })

    await waitFor(
      () => {
        expect(result.current.visibleLines).toHaveLength(mockLines.length)
      },
      { timeout: 2000 }
    )

    const elapsedTime = Date.now() - startTime
    // Should take roughly (lines.length - 1) * delay ms
    const expectedMinTime = (mockLines.length - 1) * 30 - 50
    expect(elapsedTime).toBeGreaterThan(expectedMinTime)
  })

  it('should stop trace at current position', async () => {
    const { result } = renderHook(() => useExecutionTrace(mockLines, 100))

    act(() => {
      result.current.startTrace()
    })

    // Wait for a few lines
    await waitFor(() => expect(result.current.currentLineIndex).toBeGreaterThan(1), {
      timeout: 500,
    })

    const stoppedAtIndex = result.current.currentLineIndex

    act(() => {
      result.current.stopTrace()
    })

    expect(result.current.isRunning).toBe(false)

    // Wait a bit to make sure no more lines appear
    await new Promise((resolve) => setTimeout(resolve, 200))
    expect(result.current.currentLineIndex).toBe(stoppedAtIndex)
  })

  it('should reset trace to initial state', async () => {
    const { result } = renderHook(() => useExecutionTrace(mockLines, 50))

    act(() => {
      result.current.startTrace()
    })

    await waitFor(
      () => {
        expect(result.current.visibleLines).toHaveLength(mockLines.length)
      },
      { timeout: 2000 }
    )

    act(() => {
      result.current.resetTrace()
    })

    expect(result.current.visibleLines).toHaveLength(0)
    expect(result.current.currentLineIndex).toBe(0)
    expect(result.current.isRunning).toBe(false)
  })

  it('should show all lines at once with prefers-reduced-motion', () => {
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

    const { result } = renderHook(() => useExecutionTrace(mockLines, 100))

    act(() => {
      result.current.startTrace()
    })

    // All lines should appear immediately
    expect(result.current.visibleLines).toHaveLength(mockLines.length)
    expect(result.current.currentLineIndex).toBe(mockLines.length)
    expect(result.current.isRunning).toBe(false)
  })

  it('should support multiple independent traces', async () => {
    const lines1: TerminalLine[] = [
      { id: '1', text: 'Trace 1 Line 1' },
      { id: '2', text: 'Trace 1 Line 2' },
    ]
    const lines2: TerminalLine[] = [
      { id: '1', text: 'Trace 2 Line 1' },
      { id: '2', text: 'Trace 2 Line 2' },
      { id: '3', text: 'Trace 2 Line 3' },
    ]

    const { result: result1 } = renderHook(() => useExecutionTrace(lines1, 50))
    const { result: result2 } = renderHook(() => useExecutionTrace(lines2, 50))

    act(() => {
      result1.current.startTrace()
      result2.current.startTrace()
    })

    await waitFor(
      () => {
        expect(result1.current.visibleLines).toHaveLength(lines1.length)
      },
      { timeout: 1000 }
    )
    await waitFor(
      () => {
        expect(result2.current.visibleLines).toHaveLength(lines2.length)
      },
      { timeout: 1000 }
    )

    expect(result1.current.visibleLines).toHaveLength(2)
    expect(result2.current.visibleLines).toHaveLength(3)
  })

  it('should clean up on unmount', () => {
    const { result, unmount } = renderHook(() => useExecutionTrace(mockLines, 50))

    act(() => {
      result.current.startTrace()
    })

    unmount()

    // No errors should be thrown
    expect(true).toBe(true)
  })
})
