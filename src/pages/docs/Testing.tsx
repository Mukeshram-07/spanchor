import React from 'react';
import DocumentationPage from '../../components/docs/DocumentationPage';

const Testing: React.FC = () => {
  return (
    <DocumentationPage
      title="Testing Examples"
      description="Real-world examples of using SPANCHOR for semantic search testing"
      route="/docs/testing"
    >
      <section>
        <h2 id="ecommerce-example">Example 1: E-Commerce Product Search</h2>
        <p>
          Testing semantic search for an e-commerce platform:
        </p>
        <pre className="bg-secondary-bg p-4 rounded-lg overflow-x-auto text-sm border border-border">
          <code>{`{
  "name": "E-commerce Product Search",
  "queries": [
    {
      "query": "blue running shoes",
      "relevant": ["adidas-blue-run-123", "nike-blue-run-456"]
    },
    {
      "query": "waterproof jacket",
      "relevant": ["columbia-waterproof-001", "north-face-waterproof-002"]
    }
  ]
}`}</code>
        </pre>
      </section>

      <section>
        <h2 id="qa-example">Example 2: Question Answering System</h2>
        <p>
          Testing retrieval for a Q&A system that needs exact answers:
        </p>
        <pre className="bg-secondary-bg p-4 rounded-lg overflow-x-auto text-sm border border-border">
          <code>{`{
  "name": "FAQ System",
  "queries": [
    {
      "query": "How do I reset my password?",
      "relevant": ["faq_001"],  # Exact answer required
      "top_k": 1
    },
    {
      "query": "What are your business hours?",
      "relevant": ["faq_002"],
      "top_k": 1
    }
  ]
}`}</code>
        </pre>
      </section>

      <section>
        <h2 id="rag-example">Example 3: RAG System</h2>
        <p>
          Testing retrieval for retrieval-augmented generation:
        </p>
        <pre className="bg-secondary-bg p-4 rounded-lg overflow-x-auto text-sm border border-border">
          <code>{`from spanchor import SpanchorClient

# Create RAG gold set - needs diverse contextual information
gold_set = {
  "name": "RAG Context Retrieval",
  "queries": [
    {
      "query": "Explain the impact of climate change",
      "relevant": ["env_001", "env_045", "env_089"],  # Multiple sources
      "top_k": 5
    }
  ]
}

# Test retrieval
client = SpanchorClient(adapter="elasticsearch")
results = client.evaluate(gold_set=gold_set)

print(f"Can find relevant context: {results.metrics.recall}")`}</code>
        </pre>
      </section>

      <section>
        <h2 id="ci-integration">Example 4: CI/CD Integration</h2>
        <p>
          Integrate SPANCHOR into your GitHub Actions workflow:
        </p>
        <pre className="bg-secondary-bg p-4 rounded-lg overflow-x-auto text-sm border border-border">
          <code>{`name: Search Quality Tests

on: [push, pull_request]

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: pip install spanchor
      
      # Test against gold set
      - run: |
          spanchor evaluate \\
            --gold-set gold_set.json \\
            --adapter elasticsearch \\
            --output baseline.json
      
      # Check metrics
      - run: |
          python -c "
          import json
          with open('baseline.json') as f:
            results = json.load(f)
          assert results['metrics']['recall'] > 0.7, 'Recall too low!'
          "`}</code>
        </pre>
      </section>

      <section>
        <h2 id="regression-testing">Example 5: Regression Testing</h2>
        <p>
          Compare new embedding model against current:
        </p>
        <pre className="bg-secondary-bg p-4 rounded-lg overflow-x-auto text-sm border border-border">
          <code>{`from spanchor import SpanchorClient

client = SpanchorClient()

# Test current embeddings
baseline = client.evaluate(
    gold_set=gold_set,
    adapter_config={
        'embedding_model': 'sentence-transformers/all-MiniLM-L6-v2'
    }
)

# Test new embeddings
candidate = client.evaluate(
    gold_set=gold_set,
    adapter_config={
        'embedding_model': 'sentence-transformers/all-mpnet-base-v2'
    }
)

# Compare
comparison = client.compare(baseline, candidate)

# Show detailed analysis
print(comparison.improved_queries)      # Queries that got better
print(comparison.regressed_queries)     # Queries that got worse
print(comparison.metrics_delta)`}</code>
        </pre>
      </section>

      <section>
        <h2 id="best-practices-testing">Best Practices</h2>
        <ul>
          <li>Create focused gold sets for specific domains or use cases</li>
          <li>Keep gold sets version controlled</li>
          <li>Run tests before and after changes</li>
          <li>Document expected metric thresholds</li>
          <li>Use CI/CD to automate regression detection</li>
          <li>Review and update gold sets regularly</li>
          <li>Test with realistic query distributions</li>
        </ul>
      </section>
    </DocumentationPage>
  );
};

export default Testing;
