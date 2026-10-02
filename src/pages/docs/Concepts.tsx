import React from 'react';
import DocumentationPage from '../../components/docs/DocumentationPage';

const Concepts: React.FC = () => {
  return (
    <DocumentationPage
      title="Core Concepts"
      description="Understand the fundamental principles behind SPANCHOR"
      route="/docs/concepts"
    >
      <section>
        <h2 id="semantic-search">Semantic Search</h2>
        <p>
          Semantic search goes beyond keyword matching. It understands the meaning and intent 
          behind a query and returns documents with similar semantic content.
        </p>
        <p>
          Traditional search: <code>cat</code> matches "cat" and "feline" separately.
        </p>
        <p>
          Semantic search: Understands "cat", "feline", "kitten", and "pet" are related.
        </p>
      </section>

      <section>
        <h2 id="embeddings">Embeddings</h2>
        <p>
          Embeddings are dense vector representations of text that capture semantic meaning. 
          They allow us to:
        </p>
        <ul>
          <li>Compare similarity between queries and documents</li>
          <li>Find semantically related content</li>
          <li>Train ranking models</li>
          <li>Detect query intent</li>
        </ul>
      </section>

      <section>
        <h2 id="ranking">Ranking Models</h2>
        <p>
          After retrieval, documents are ranked by relevance. SPANCHOR supports:
        </p>
        <ul>
          <li><strong>BM25</strong> - Traditional keyword-based ranking</li>
          <li><strong>Semantic</strong> - Embedding-based similarity</li>
          <li><strong>Learned-to-Rank</strong> - Machine learning models trained on your data</li>
          <li><strong>Hybrid</strong> - Combination of multiple ranking strategies</li>
        </ul>
      </section>

      <section>
        <h2 id="gold-sets">Gold Sets</h2>
        <p>
          A gold set is a collection of query-document pairs labeled as relevant or irrelevant. 
          It's used to:
        </p>
        <ul>
          <li>Define what "good" search quality means for your use case</li>
          <li>Train ranking models</li>
          <li>Evaluate ranking quality</li>
          <li>Detect regressions in search results</li>
        </ul>
      </section>

      <section>
        <h2 id="evaluation-metrics">Evaluation Metrics</h2>
        <p>
          SPANCHOR measures search quality using standard information retrieval metrics:
        </p>
        <ul>
          <li><strong>Recall@K</strong> - What % of relevant docs are in top K results?</li>
          <li><strong>Precision@K</strong> - What % of top K results are relevant?</li>
          <li><strong>Hit Rate@K</strong> - What % of queries have ≥1 relevant result in top K?</li>
          <li><strong>MRR</strong> - Mean reciprocal rank of first relevant result</li>
        </ul>
      </section>

      <section>
        <h2 id="regression-testing">Regression Testing</h2>
        <p>
          Semantic search regression testing compares ranking quality between two versions:
        </p>
        <ul>
          <li><strong>Baseline</strong> - Your current ranking system</li>
          <li><strong>Candidate</strong> - New ranking system or updated embeddings</li>
        </ul>
        <p>
          SPANCHOR identifies which queries got better, worse, or stayed the same.
        </p>
      </section>
    </DocumentationPage>
  );
};

export default Concepts;
