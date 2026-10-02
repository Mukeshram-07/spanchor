import React from 'react';
import DocumentationPage from '../../components/docs/DocumentationPage';

const Anchors: React.FC = () => {
  return (
    <DocumentationPage
      title="Anchors"
      description="Use semantic markers to improve retrieval accuracy"
      route="/docs/anchors"
    >
      <section>
        <h2 id="what-are-anchors">What are Anchors?</h2>
        <p>
          Anchors are semantic markers within documents that help identify relevant content. 
          They act as semantic "hotspots" that improve retrieval accuracy for specific topics.
        </p>
      </section>

      <section>
        <h2 id="why-anchors">Why Use Anchors?</h2>
        <p>
          Anchors solve several problems:
        </p>
        <ul>
          <li><strong>Topic specificity</strong> - Mark sections relevant to specific topics</li>
          <li><strong>Semantic precision</strong> - Improve retrieval for narrow queries</li>
          <li><strong>Structured data</strong> - Connect unstructured text to structured metadata</li>
          <li><strong>Multi-level relevance</strong> - Different relevance scores for different sections</li>
        </ul>
      </section>

      <section>
        <h2 id="anchor-structure">Anchor Structure</h2>
        <p>
          An anchor consists of:
        </p>
        <ul>
          <li><strong>Content</strong> - The text or passage being marked</li>
          <li><strong>Topic</strong> - The semantic category</li>
          <li><strong>Weight</strong> - Importance score (0-1)</li>
          <li><strong>Metadata</strong> - Additional context</li>
        </ul>
      </section>

      <section>
        <h2 id="defining-anchors">Defining Anchors</h2>
        <p>
          Define anchors in your documents:
        </p>
        <pre className="bg-secondary-bg p-4 rounded-lg overflow-x-auto text-sm border border-border">
          <code>{`{
  "document_id": "doc_001",
  "title": "Deep Learning Fundamentals",
  "anchors": [
    {
      "content": "Neural networks with multiple layers",
      "topic": "neural_networks",
      "weight": 0.9,
      "metadata": {"section": "architecture"}
    },
    {
      "content": "Backpropagation algorithm for training",
      "topic": "training",
      "weight": 0.8,
      "metadata": {"section": "methods"}
    }
  ]
}`}</code>
        </pre>
      </section>

      <section>
        <h2 id="using-anchors">Using Anchors in Queries</h2>
        <p>
          When searching, anchors automatically improve relevance:
        </p>
        <pre className="bg-secondary-bg p-4 rounded-lg overflow-x-auto text-sm border border-border">
          <code>{`# Query about neural networks
# SPANCHOR automatically weights docs with "neural_networks" anchors higher
results = client.search(
    query="How do neural networks work?",
    use_anchors=True
)`}</code>
        </pre>
      </section>

      <section>
        <h2 id="best-practices">Best Practices</h2>
        <ul>
          <li>Use consistent topic names across your corpus</li>
          <li>Set weights based on section importance</li>
          <li>Include metadata for filtering</li>
          <li>Review anchor effectiveness with gold sets</li>
          <li>Update anchors when content changes</li>
        </ul>
      </section>
    </DocumentationPage>
  );
};

export default Anchors;
