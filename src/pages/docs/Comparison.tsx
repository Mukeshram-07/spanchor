import React from 'react';
import DocumentationPage from '../../components/docs/DocumentationPage';

const Comparison: React.FC = () => {
  return (
    <DocumentationPage
      title="Comparison & Regression Testing"
      description="Compare ranking performance between two systems"
      route="/docs/comparison"
    >
      <section>
        <h2 id="overview">Overview</h2>
        <p>
          Comparison allows you to evaluate how a new ranking system performs against a baseline. 
          SPANCHOR identifies improvements, regressions, and unchanged queries.
        </p>
      </section>

      <section>
        <h2 id="baseline-vs-candidate">Baseline vs Candidate</h2>
        <p>
          <strong>Baseline:</strong> Your current production ranking system
        </p>
        <p className="mt-2">
          <strong>Candidate:</strong> New ranking system, updated embeddings, or different configuration
        </p>
      </section>

      <section>
        <h2 id="running-comparison">Running a Comparison</h2>
        <pre className="bg-secondary-bg p-4 rounded-lg overflow-x-auto text-sm border border-border">
          <code>{`from spanchor import SpanchorClient
import json

# Load gold set
with open('gold_set.json') as f:
    gold_set = json.load(f)

client = SpanchorClient()

# Get baseline results
baseline = client.evaluate(
    gold_set=gold_set['queries'],
    adapter_config=baseline_config,
    top_k=10
)

# Get candidate results
candidate = client.evaluate(
    gold_set=gold_set['queries'],
    adapter_config=candidate_config,
    top_k=10
)

# Compare
comparison = client.compare(baseline, candidate)
print(comparison.summary)`}</code>
        </pre>
      </section>

      <section>
        <h2 id="comparison-results">Understanding Results</h2>
        <p>
          Comparison results show:
        </p>
        <ul>
          <li><strong>Improved:</strong> Queries with better ranking in candidate</li>
          <li><strong>Regressed:</strong> Queries with worse ranking in candidate</li>
          <li><strong>Unchanged:</strong> Queries with same ranking</li>
        </ul>
      </section>

      <section>
        <h2 id="metrics-delta">Metrics Delta</h2>
        <p>
          For each metric, SPANCHOR shows:
        </p>
        <ul>
          <li><strong>Baseline value</strong> - Current system performance</li>
          <li><strong>Candidate value</strong> - New system performance</li>
          <li><strong>Delta</strong> - Change (positive is improvement)</li>
          <li><strong>Percentage change</strong> - % improvement/regression</li>
        </ul>
      </section>

      <section>
        <h2 id="example-report">Example Comparison Report</h2>
        <pre className="bg-secondary-bg p-4 rounded-lg overflow-x-auto text-sm border border-border">
          <code>{`Metric          Baseline  Candidate  Delta    Change
Recall@10       0.72      0.78      +0.06    +8.3%
Precision@10    0.68      0.71      +0.03    +4.4%
Hit Rate@10     0.95      0.96      +0.01    +1.1%

Query Analysis:
- Improved:    32 queries
- Regressed:    4 queries
- Unchanged:   64 queries`}</code>
        </pre>
      </section>

      <section>
        <h2 id="decision-making">Decision Making</h2>
        <ul>
          <li><strong>Approve</strong> - Improvements outweigh regressions, no critical issues</li>
          <li><strong>Investigate</strong> - Regressions need to be understood</li>
          <li><strong>Reject</strong> - Too many regressions or important queries regressed</li>
          <li><strong>Iterate</strong> - Merge improvements, fix regressions, re-test</li>
        </ul>
      </section>

      <section>
        <h2 id="regression-analysis">Regression Analysis</h2>
        <p>
          When candidate regresses, analyze:
        </p>
        <ol>
          <li>Which queries regressed?</li>
          <li>What was the baseline result?</li>
          <li>What is the new result?</li>
          <li>Why might the ranking change have happened?</li>
        </ol>
      </section>
    </DocumentationPage>
  );
};

export default Comparison;
