import type { DemoDataset, ExecutionStep, ComparisonResult, Metrics } from '../types'

/**
 * Demo dataset for demonstration purposes
 */
export const DEMO_DATASET: DemoDataset = {
  id: 'demo-001',
  name: 'Semantic Search Benchmark',
  description:
    'A comprehensive benchmark dataset for evaluating semantic search and ranking optimization techniques',
  size: 10000,
  query: 'Find the most relevant documents for semantic queries',
}

/**
 * Execution steps for the demo
 */
export const EXECUTION_STEPS: ExecutionStep[] = [
  {
    id: 'step-1',
    name: 'Data Loading',
    description: 'Loading benchmark dataset and preparing documents',
    duration: 2.3,
    status: 'completed',
  },
  {
    id: 'step-2',
    name: 'Baseline Evaluation',
    description: 'Evaluating baseline semantic search model',
    duration: 5.8,
    status: 'completed',
  },
  {
    id: 'step-3',
    name: 'Model Optimization',
    description: 'Applying optimizations to the ranking model',
    duration: 8.2,
    status: 'completed',
  },
  {
    id: 'step-4',
    name: 'Candidate Evaluation',
    description: 'Evaluating optimized candidate model',
    duration: 6.1,
    status: 'completed',
  },
  {
    id: 'step-5',
    name: 'Comparison Analysis',
    description: 'Analyzing performance differences between models',
    duration: 3.5,
    status: 'completed',
  },
]

/**
 * Baseline metrics (original model)
 */
export const BASELINE_METRICS: Metrics = {
  recall: 0.405,
  precision: 0.02,
  hit: 0.41,
}

/**
 * Candidate metrics (optimized model)
 */
export const CANDIDATE_METRICS: Metrics = {
  recall: 0.249,
  precision: 0.017,
  hit: 0.26,
}

/**
 * Comparison results between baseline and candidate
 */
export const COMPARISON_RESULT: ComparisonResult = {
  baseline: BASELINE_METRICS,
  candidate: CANDIDATE_METRICS,
  improved: 6,
  unchanged: 75,
  regressed: 19,
}

/**
 * Verification of metrics
 */
export const verifyMetrics = (): boolean => {
  const result = COMPARISON_RESULT

  // Verify baseline metrics
  if (
    Math.abs(result.baseline.recall - 0.405) > 0.001 ||
    Math.abs(result.baseline.precision - 0.02) > 0.001 ||
    Math.abs(result.baseline.hit - 0.41) > 0.001
  ) {
    console.error('Baseline metrics verification failed')
    return false
  }

  // Verify candidate metrics
  if (
    Math.abs(result.candidate.recall - 0.249) > 0.001 ||
    Math.abs(result.candidate.precision - 0.017) > 0.001 ||
    Math.abs(result.candidate.hit - 0.26) > 0.001
  ) {
    console.error('Candidate metrics verification failed')
    return false
  }

  // Verify outcomes
  if (result.improved !== 6 || result.unchanged !== 75 || result.regressed !== 19) {
    console.error('Outcome verification failed')
    return false
  }

  console.log('✓ Metrics verification passed')
  return true
}

/**
 * Sample regression query results for table display
 * Includes improved, unchanged, and regressed queries
 */
export const REGRESSION_QUERY_RESULTS = [
  // Improved queries
  { queryId: 'Q001', baseline: 0.60, candidate: 0.80, delta: 0.20, status: 'improved' as const },
  { queryId: 'Q002', baseline: 0.55, candidate: 0.75, delta: 0.20, status: 'improved' as const },
  { queryId: 'Q003', baseline: 0.50, candidate: 0.70, delta: 0.20, status: 'improved' as const },
  { queryId: 'Q004', baseline: 0.65, candidate: 0.82, delta: 0.17, status: 'improved' as const },
  { queryId: 'Q005', baseline: 0.45, candidate: 0.60, delta: 0.15, status: 'improved' as const },
  { queryId: 'Q006', baseline: 0.70, candidate: 0.85, delta: 0.15, status: 'improved' as const },
  
  // Unchanged queries
  { queryId: 'Q007', baseline: 0.80, candidate: 0.80, delta: 0.00, status: 'unchanged' as const },
  { queryId: 'Q008', baseline: 0.75, candidate: 0.75, delta: 0.00, status: 'unchanged' as const },
  { queryId: 'Q009', baseline: 0.90, candidate: 0.90, delta: 0.00, status: 'unchanged' as const },
  { queryId: 'Q010', baseline: 0.65, candidate: 0.65, delta: 0.00, status: 'unchanged' as const },
  { queryId: 'Q011', baseline: 0.55, candidate: 0.55, delta: 0.00, status: 'unchanged' as const },
  { queryId: 'Q012', baseline: 0.70, candidate: 0.70, delta: 0.00, status: 'unchanged' as const },
  { queryId: 'Q013', baseline: 0.60, candidate: 0.60, delta: 0.00, status: 'unchanged' as const },
  { queryId: 'Q014', baseline: 0.85, candidate: 0.85, delta: 0.00, status: 'unchanged' as const },
  { queryId: 'Q015', baseline: 0.50, candidate: 0.50, delta: 0.00, status: 'unchanged' as const },
  
  // Regressed queries
  { queryId: 'Q016', baseline: 0.80, candidate: 0.40, delta: -0.40, status: 'regressed' as const },
  { queryId: 'Q017', baseline: 0.75, candidate: 0.50, delta: -0.25, status: 'regressed' as const },
  { queryId: 'Q018', baseline: 0.70, candidate: 0.45, delta: -0.25, status: 'regressed' as const },
  { queryId: 'Q019', baseline: 0.90, candidate: 0.70, delta: -0.20, status: 'regressed' as const },
  { queryId: 'Q020', baseline: 0.65, candidate: 0.50, delta: -0.15, status: 'regressed' as const },
]
