import React from 'react';
import DocumentationPage from '../../components/docs/DocumentationPage';

const GoldSets: React.FC = () => {
  return (
    <DocumentationPage
      title="Gold Sets"
      description="Create and manage ground truth datasets for search evaluation"
      route="/docs/gold-sets"
    >
      <section>
        <h2 id="what-are-gold-sets">What are Gold Sets?</h2>
        <p>
          Gold sets are curated collections of query-document pairs labeled with their relevance. 
          They represent the ground truth of what "good" search results should look like.
        </p>
      </section>

      <section>
        <h2 id="gold-set-format">Gold Set Format</h2>
        <p>
          Gold sets are typically JSON files with this structure:
        </p>
        <pre className="bg-secondary-bg p-4 rounded-lg overflow-x-auto text-sm border border-border">
          <code>{`{
  "name": "E-commerce Search",
  "version": "1.0",
  "description": "Gold set for product search queries",
  "queries": [
    {
      "query_id": "q1",
      "query_text": "blue running shoes",
      "relevant_documents": ["doc_101", "doc_203", "doc_445"],
      "irrelevant_documents": ["doc_050", "doc_999"]
    },
    {
      "query_id": "q2",
      "query_text": "women's athletic wear",
      "relevant_documents": ["doc_204", "doc_355", "doc_667"]
    }
  ]
}`}</code>
        </pre>
      </section>

      <section>
        <h2 id="creating-gold-sets">Creating Gold Sets</h2>
        <p>
          Steps to create an effective gold set:
        </p>
        <ol>
          <li><strong>Define scope</strong> - What queries and domains?</li>
          <li><strong>Collect queries</strong> - Real or representative queries</li>
          <li><strong>Find relevant docs</strong> - Manual or automated identification</li>
          <li><strong>Verify quality</strong> - Check labels for accuracy</li>
          <li><strong>Document decisions</strong> - Note any edge cases</li>
        </ol>
      </section>

      <section>
        <h2 id="gold-set-sizes">Recommended Gold Set Sizes</h2>
        <ul>
          <li><strong>Small (10-50 queries)</strong> - Quick validation, topic-specific tests</li>
          <li><strong>Medium (50-500 queries)</strong> - General evaluation, regression detection</li>
          <li><strong>Large (500+ queries)</strong> - Production monitoring, training LTR models</li>
        </ul>
      </section>

      <section>
        <h2 id="using-gold-sets">Using Gold Sets in SPANCHOR</h2>
        <p>
          Load and evaluate with your gold set:
        </p>
        <pre className="bg-secondary-bg p-4 rounded-lg overflow-x-auto text-sm border border-border">
          <code>{`import json
from spanchor import SpanchorClient

# Load gold set
with open('gold_set.json') as f:
    gold_set = json.load(f)

# Initialize client
client = SpanchorClient()

# Evaluate
results = client.evaluate(
    gold_set=gold_set['queries'],
    top_k=10
)

print(f"Recall@10: {results.metrics.recall}")
print(f"Precision@10: {results.metrics.precision}")`}</code>
        </pre>
      </section>

      <section>
        <h2 id="best-practices">Best Practices</h2>
        <ul>
          <li>Keep gold sets focused on specific use cases or domains</li>
          <li>Regularly update gold sets with new queries</li>
          <li>Use consistent relevance judgments</li>
          <li>Document any edge cases or ambiguous queries</li>
          <li>Version control your gold sets</li>
          <li>Have multiple annotators review labels for quality</li>
          <li>Split into train/validation/test sets for ML</li>
        </ul>
      </section>

      <section>
        <h2 id="multi-label-relevance">Multi-level Relevance</h2>
        <p>
          For more nuanced evaluation, use relevance grades:
        </p>
        <pre className="bg-secondary-bg p-4 rounded-lg overflow-x-auto text-sm border border-border">
          <code>{`{
  "query_id": "q3",
  "query_text": "machine learning",
  "relevance_judgments": {
    "doc_001": "highly_relevant",
    "doc_042": "relevant",
    "doc_089": "partially_relevant",
    "doc_234": "not_relevant"
  }
}`}</code>
        </pre>
      </section>
    </DocumentationPage>
  );
};

export default GoldSets;
