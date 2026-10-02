import { useState, useEffect, useRef, useCallback } from 'react'
import type { ExecutionStep } from '../types'

/**
 * Step progression results that accumulate during simulation
 */
export interface SimulationResults {
  completedSteps: ExecutionStep[]
  currentStatus: string
  queriesProcessed: number
  metricsComputed: Record<string, number>
}

/**
 * Current state of the simulation
 */
export interface SimulationState {
  isRunning: boolean
  currentStep: number
  results: SimulationResults
  progress: number // 0-100
}

/**
 * Hook to manage deterministic simulation execution
 *
 * Advances through EXECUTION_STEPS based on timestamps, updating state as it progresses.
 * Supports multiple simultaneous simulations independently.
 *
 * @param steps - Array of execution steps to simulate
 * @returns Simulation state and control functions
 */
export function useSimulation(steps: ExecutionStep[]) {
  const [state, setState] = useState<SimulationState>({
    isRunning: false,
    currentStep: 0,
    results: {
      completedSteps: [],
      currentStatus: 'Ready',
      queriesProcessed: 0,
      metricsComputed: {},
    },
    progress: 0,
  })

  const timeoutRefs = useRef<ReturnType<typeof setTimeout>[]>([])
  const startTimeRef = useRef<number | null>(null)
  const isMountedRef = useRef<boolean>(true)

  /**
   * Clean up all active timers
   */
  const clearTimers = useCallback(() => {
    timeoutRefs.current.forEach((timeout) => clearTimeout(timeout))
    timeoutRefs.current = []
  }, [])

  /**
   * Start the simulation from the beginning
   */
  const startSimulation = useCallback(() => {
    // Reset state
    setState({
      isRunning: true,
      currentStep: 0,
      results: {
        completedSteps: [],
        currentStatus: 'Loading...',
        queriesProcessed: 0,
        metricsComputed: {},
      },
      progress: 0,
    })

    startTimeRef.current = Date.now()

    // Schedule each step based on its timestamp
    steps.forEach((step, index) => {
      const timeout = setTimeout(() => {
        if (!isMountedRef.current) return

        // Update state with this step's results
        setState((prev) => {
          const newCompleted = [...prev.results.completedSteps, step]
          const progress = Math.round(((index + 1) / steps.length) * 100)
          const newStatus = step.description || `Running step ${index + 1}...`

          return {
            isRunning: index < steps.length - 1,
            currentStep: index,
            results: {
              completedSteps: newCompleted,
              currentStatus: newStatus,
              queriesProcessed: prev.results.queriesProcessed,
              metricsComputed: prev.results.metricsComputed,
            },
            progress,
          }
        })

        // Mark as complete when all steps finished
        if (index === steps.length - 1) {
          if (isMountedRef.current) {
            setState((prev) => ({
              ...prev,
              isRunning: false,
              results: {
                ...prev.results,
                currentStatus: 'Evaluation complete',
              },
            }))
          }
        }
      }, step.duration * 1000) // Convert seconds to milliseconds

      timeoutRefs.current.push(timeout)
    })
  }, [steps])

  /**
   * Stop the simulation at any point
   */
  const stopSimulation = useCallback(() => {
    clearTimers()
    setState((prev) => ({
      ...prev,
      isRunning: false,
      results: {
        ...prev.results,
        currentStatus: 'Stopped',
      },
    }))
  }, [clearTimers])

  /**
   * Reset the simulation to initial state
   */
  const resetSimulation = useCallback(() => {
    clearTimers()
    startTimeRef.current = null
    setState({
      isRunning: false,
      currentStep: 0,
      results: {
        completedSteps: [],
        currentStatus: 'Ready',
        queriesProcessed: 0,
        metricsComputed: {},
      },
      progress: 0,
    })
  }, [clearTimers])

  /**
   * Cleanup on unmount - prevent memory leaks
   */
  useEffect(() => {
    return () => {
      isMountedRef.current = false
      clearTimers()
    }
  }, [clearTimers])

  return {
    ...state,
    startSimulation,
    stopSimulation,
    resetSimulation,
  }
}
