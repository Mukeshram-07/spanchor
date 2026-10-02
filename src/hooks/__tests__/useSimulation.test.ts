import { describe, it, expect } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'
import { useSimulation } from '../useSimulation'
import type { ExecutionStep } from '../../types'

describe('useSimulation', () => {
  const mockSteps: ExecutionStep[] = [
    {
      id: 'step-1',
      name: 'Load Data',
      description: 'Loading dataset',
      duration: 0.1,
      status: 'pending',
    },
    {
      id: 'step-2',
      name: 'Process',
      description: 'Processing data',
      duration: 0.1,
      status: 'pending',
    },
    {
      id: 'step-3',
      name: 'Complete',
      description: 'Completing evaluation',
      duration: 0.1,
      status: 'pending',
    },
  ]

  it('should initialize with default state', () => {
    const { result } = renderHook(() => useSimulation(mockSteps))

    expect(result.current.isRunning).toBe(false)
    expect(result.current.currentStep).toBe(0)
    expect(result.current.results.completedSteps).toHaveLength(0)
    expect(result.current.progress).toBe(0)
  })

  it('should start simulation and progress through steps', async () => {
    const { result } = renderHook(() => useSimulation(mockSteps))

    act(() => {
      result.current.startSimulation()
    })

    expect(result.current.isRunning).toBe(true)

    // Wait for all steps to complete
    await waitFor(
      () => {
        expect(result.current.isRunning).toBe(false)
      },
      { timeout: 2000 }
    )

    expect(result.current.currentStep).toBeGreaterThan(0)
    expect(result.current.results.completedSteps.length).toBeGreaterThan(0)
  })

  it('should stop simulation', async () => {
    const { result } = renderHook(() => useSimulation(mockSteps))

    act(() => {
      result.current.startSimulation()
    })

    expect(result.current.isRunning).toBe(true)

    act(() => {
      result.current.stopSimulation()
    })

    expect(result.current.isRunning).toBe(false)
  })

  it('should reset simulation', async () => {
    const { result } = renderHook(() => useSimulation(mockSteps))

    act(() => {
      result.current.startSimulation()
    })

    await waitFor(() => expect(result.current.isRunning).toBe(false), { timeout: 2000 })

    act(() => {
      result.current.resetSimulation()
    })

    expect(result.current.isRunning).toBe(false)
    expect(result.current.currentStep).toBe(0)
    expect(result.current.results.completedSteps).toHaveLength(0)
    expect(result.current.progress).toBe(0)
  })

  it('should support multiple simultaneous simulations independently', () => {
    const { result: result1 } = renderHook(() => useSimulation(mockSteps))
    const { result: result2 } = renderHook(() => useSimulation(mockSteps))

    act(() => {
      result1.current.startSimulation()
    })

    // result2 should not be affected
    expect(result2.current.isRunning).toBe(false)
  })

  it('should calculate progress percentage', async () => {
    const { result } = renderHook(() => useSimulation(mockSteps))

    act(() => {
      result.current.startSimulation()
    })

    await waitFor(() => expect(result.current.progress).toBeGreaterThan(0), { timeout: 500 })
    expect(result.current.progress).toBeLessThanOrEqual(100)
  })
})
