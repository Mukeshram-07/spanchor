/**
 * Core types for the Spanchor website application
 */

export interface Example {
  id: string
  title: string
  description: string
  query: string
  results: string[]
}

export interface DemoDataset {
  id: string
  name: string
  description: string
  size: number
  query: string
}

export interface ExecutionStep {
  id: string
  name: string
  description: string
  duration: number
  status: 'pending' | 'running' | 'completed' | 'failed'
}

export interface Metrics {
  recall: number
  precision: number
  hit: number
}

export interface ComparisonResult {
  baseline: Metrics
  candidate: Metrics
  improved: number
  unchanged: number
  regressed: number
}

export interface QueryResult {
  queryId: string
  baseline: number
  candidate: number
  delta: number
  status: 'improved' | 'unchanged' | 'regressed'
}

export interface DocsPage {
  id: string
  title: string
  content: string
  sections: DocSection[]
}

export interface DocSection {
  id: string
  title: string
  content: string
  examples?: Example[]
}
