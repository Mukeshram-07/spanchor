# React Hooks for SPANCHOR Simulation

This directory contains reusable React hooks for managing animations and deterministic simulations in the SPANCHOR website.

## Hooks Overview

### 1. `useSimulation`

Manages the execution of deterministic simulation steps.

**Usage:**
```typescript
import { useSimulation } from '@/hooks'
import { EXECUTION_STEPS } from '@/data/demoData'

function ExecutionComponent() {
  const {
    isRunning,
    currentStep,
    results,
    progress,
    startSimulation,
    stopSimulation,
    resetSimulation,
  } = useSimulation(EXECUTION_STEPS)

  return (
    <div>
      <p>Progress: {progress}%</p>
      <button onClick={startSimulation}>Start</button>
      <button onClick={stopSimulation}>Stop</button>
      <button onClick={resetSimulation}>Reset</button>
    </div>
  )
}
```

**Features:**
- ✓ Timer-based step progression
- ✓ Multiple simultaneous simulations support
- ✓ Memory leak prevention (cleanup on unmount)
- ✓ Progress tracking (0-100%)
- ✓ Deterministic execution with EXECUTION_STEPS

---

### 2. `useAnimatedMetric`

Animates a numeric metric value from 0 to target, with customizable duration and easing.

**Usage:**
```typescript
import { useAnimatedMetric } from '@/hooks'

function MetricsDisplay() {
  const { displayValue, isAnimating, startAnimation } = useAnimatedMetric(
    0.405, // target value
    1500,  // duration in ms
    'easeOut' // easing function
  )

  return (
    <div>
      <p>Recall@5: {displayValue.toFixed(3)}</p>
      <button onClick={startAnimation}>Animate</button>
    </div>
  )
}
```

**Features:**
- ✓ Smooth animation from 0 to target
- ✓ Custom duration and easing (linear, easeOut, easeIn)
- ✓ Respects prefers-reduced-motion (instant transition)
- ✓ Multiple simultaneous animations
- ✓ GPU-accelerated with requestAnimationFrame

---

### 3. `useExecutionTrace`

Animates terminal lines appearing sequentially with configurable delays.

**Usage:**
```typescript
import { useExecutionTrace, type TerminalLine } from '@/hooks'

const terminalLines: TerminalLine[] = [
  { id: '1', text: '$ spanchor evaluate' },
  { id: '2', text: 'Loading gold set...' },
  { id: '3', text: '✓ 100 queries loaded' },
]

function Terminal() {
  const {
    visibleLines,
    currentLineIndex,
    isRunning,
    startTrace,
    stopTrace,
    resetTrace,
  } = useExecutionTrace(terminalLines, 150)

  return (
    <div>
      {visibleLines.map((line) => (
        <div key={line.id}>{line.text}</div>
      ))}
      <button onClick={startTrace}>Start</button>
      <button onClick={stopTrace}>Stop</button>
      <button onClick={resetTrace}>Reset</button>
    </div>
  )
}
```

**Features:**
- ✓ Sequential line animation
- ✓ Configurable delay between lines
- ✓ Start/stop/reset controls
- ✓ Respects prefers-reduced-motion (all lines appear instantly)
- ✓ Multiple independent traces

---

### 4. `useReducedMotion`

Detects and responds to the `prefers-reduced-motion` media query.

**Usage:**
```typescript
import { useReducedMotion } from '@/hooks'

function AnimatedComponent() {
  const prefersReducedMotion = useReducedMotion()

  const animationDuration = prefersReducedMotion ? 0 : 500

  return (
    <motion.div
      animate={{ opacity: 1 }}
      transition={{ duration: animationDuration }}
    >
      Content
    </motion.div>
  )
}
```

**Features:**
- ✓ Real-time media query detection
- ✓ Listens for OS preference changes
- ✓ Returns boolean (true = reduce motion)
- ✓ Proper cleanup on unmount
- ✓ SSR-safe implementation

---

## Integration Guidelines

### With Simulation Hooks

Combine `useSimulation`, `useAnimatedMetric`, and `useExecutionTrace` for full execution visualization:

```typescript
function ExecutionPanel() {
  const simulation = useSimulation(EXECUTION_STEPS)
  const recallAnimation = useAnimatedMetric(0.405, 1500)
  const traceAnimation = useExecutionTrace(terminalLines, 150)

  // Start all animations when simulation starts
  useEffect(() => {
    if (simulation.isRunning) {
      recallAnimation.startAnimation()
      traceAnimation.startTrace()
    }
  }, [simulation.isRunning])

  return (
    <div>
      <Terminal lines={traceAnimation.visibleLines} />
      <Metrics value={recallAnimation.displayValue} />
      <ProgressBar progress={simulation.progress} />
    </div>
  )
}
```

### With Reduced Motion

All animation hooks respect `useReducedMotion` automatically:

```typescript
function Component() {
  const prefersReducedMotion = useReducedMotion()
  
  // If user prefers reduced motion:
  // - useAnimatedMetric: shows target immediately
  // - useExecutionTrace: shows all lines at once
  // - useSimulation: still progresses through steps (UI updates only, no animations)
}
```

---

## API Reference

### `useSimulation(steps)`

**Parameters:**
- `steps`: `ExecutionStep[]` - Array of execution steps

**Returns:**
- `isRunning`: boolean
- `currentStep`: number
- `results`: SimulationResults
- `progress`: number (0-100)
- `startSimulation`: () => void
- `stopSimulation`: () => void
- `resetSimulation`: () => void

---

### `useAnimatedMetric(targetValue, duration?, easing?)`

**Parameters:**
- `targetValue`: number - Final value to animate to
- `duration?`: number - Duration in milliseconds (default: 1500)
- `easing?`: 'linear' | 'easeOut' | 'easeIn' - Easing function (default: 'easeOut')

**Returns:**
- `displayValue`: number
- `isAnimating`: boolean
- `startAnimation`: () => void

---

### `useExecutionTrace(lines, delayMs?)`

**Parameters:**
- `lines`: `TerminalLine[]` - Array of terminal lines
- `delayMs?`: number - Delay between lines in ms (default: 150)

**Returns:**
- `visibleLines`: `TerminalLine[]`
- `currentLineIndex`: number
- `isRunning`: boolean
- `startTrace`: () => void
- `stopTrace`: () => void
- `resetTrace`: () => void

---

### `useReducedMotion()`

**Parameters:**
- None

**Returns:**
- boolean - true if reduced motion is preferred

---

## Performance Considerations

1. **useSimulation**: Uses `setTimeout` for step scheduling. No performance issues even with many steps.

2. **useAnimatedMetric**: Uses `requestAnimationFrame` for smooth animation. GPU-accelerated numeric animation.

3. **useExecutionTrace**: Uses `setTimeout` for delays. Minimal DOM operations (just appending lines).

4. **useReducedMotion**: Lightweight media query listener. No performance impact.

---

## Accessibility Features

All hooks respect `prefers-reduced-motion` globally:

- **useAnimatedMetric**: Shows target value instantly
- **useExecutionTrace**: Shows all lines at once
- **useSimulation**: Steps still progress (no animation delay)
- **useReducedMotion**: Direct OS preference detection

---

## Testing

Each hook includes comprehensive test suites in `__tests__/`:

```bash
# Run tests (when test runner is configured)
npm test
```

Test coverage includes:
- Basic functionality
- Edge cases (empty inputs, rapid calls)
- Multiple simultaneous instances
- Cleanup and memory leaks
- Media query changes
- SSR safety

---

## Best Practices

1. **Always reset before starting**: Call `resetSimulation()` before `startSimulation()`
2. **Handle unmount gracefully**: All hooks clean up properly, but avoid calling methods after unmount
3. **Combine with React state**: Use hooks to manage animations, but keep UI state in component state
4. **Respect user preferences**: Check `useReducedMotion()` before custom animations
5. **Test with prefers-reduced-motion**: Always test your animations with the OS setting enabled

---

## Examples

See `/src/components/features/` for real-world usage examples:
- `ExecutionOutput.tsx` - Full execution panel
- `Terminal.tsx` - Terminal visualization
- `MetricsDisplay.tsx` - Animated metrics
- `QueryProgressList.tsx` - Query status animation
