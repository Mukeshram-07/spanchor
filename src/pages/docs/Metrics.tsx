import React from 'react';
import DocumentationPage from '../../components/docs/DocumentationPage';

const Metrics: React.FC = () => {
  return (
    <DocumentationPage
      title="Evaluation Metrics"
      description="Understand search quality metrics used by SPANCHOR"
      route="/docs/metrics"
    >
      <section>
        <h2 id="metrics-overview">Metrics Overview</h2>
        <p>
          SPANCHOR uses standard information retrieval metrics to evaluate search quality. 
          These metrics are computed against your gold set.
        </p>
      </section>

      <section>
        <h2 id="recall-at-k">Recall@K</h2>
        <p>
          <strong>Definition:</strong> Percentage of relevant documents that appear in the top K results.
        </p>
        <p className="font-mono bg-secondary-bg p-3 rounded text-sm mt-2">
          Recall@K = (# relevant docs in top K) / (# total relevant docs)
        </p>
        <p className="mt-3">
          <strong>Example:</strong> If 5 relevant documents exist and 3 appear in top 10:
        </p>
        <p className="font-mono bg-secondary-bg p-3 rounded text-sm mt-2">
          Recall@10 = 3/5 = 0.60 (60%)
        </p>
        <p className="mt-3">
          <strong>When to use:</strong> Measures completeness of retrieval. Higher is better.
        </p>
      </section>

      <section>
        <h2 id="precision-at-k">Precision@K</h2>
        <p>
          <strong>Definition:</strong> Percentage of top K results that are actually relevant.
        </p>
        <p className="font-mono bg-secondary-bg p-3 rounded text-sm mt-2">
          Precision@K = (# relevant docs in top K) / K
        </p>
        <p className="mt-3">
          <strong>Example:</strong> If top 10 results contain 7 relevant documents:
        </p>
        <p className="font-mono bg-secondary-bg p-3 rounded text-sm mt-2">
          Precision@10 = 7/10 = 0.70 (70%)
        </p>
        <p className="mt-3">
          <strong>When to use:</strong> Measures result accuracy. Higher is better.
        </p>
      </section>

      <section>
        <h2 id="hit-rate">Hit Rate@K</h2>
        <p>
          <strong>Definition:</strong> Percentage of queries with at least one relevant result in top K.
        </p>
        <p className="font-mono bg-secondary-bg p-3 rounded text-sm mt-2">
          Hit Rate@K = (# queries with ≥1 relevant doc in top K) / (# total queries)
        </p>
        <p className="mt-3">
          <strong>Example:</strong> 95 out of 100 queries have a relevant result in top 10:
        </p>
        <p className="font-mono bg-secondary-bg p-3 rounded text-sm mt-2">
          Hit Rate@10 = 95/100 = 0.95 (95%)
        </p>
        <p className="mt-3">
          <strong>When to use:</strong> Measures success rate. Essential for user experience.
        </p>
      </section>

      <section>
        <h2 id="mrr">Mean Reciprocal Rank (MRR)</h2>
        <p>
          <strong>Definition:</strong> Average of the inverse rank of the first relevant result.
        </p>
        <p className="font-mono bg-secondary-bg p-3 rounded text-sm mt-2">
          MRR = (1/rank1 + 1/rank2 + ... + 1/rankN) / N
        </p>
        <p className="mt-3">
          <strong>Example:</strong> First relevant doc at rank 1, 3, and 2:
        </p>
        <p className="font-mono bg-secondary-bg p-3 rounded text-sm mt-2">
          MRR = (1/1 + 1/3 + 1/2) / 3 = 0.611
        </p>
        <p className="mt-3">
          <strong>When to use:</strong> Measures ranking quality of first relevant result.
        </p>
      </section>

      <section>
        <h2 id="ndcg">Normalized Discounted Cumulative Gain (NDCG)</h2>
        <p>
          <strong>Definition:</strong> Ranking quality metric that considers position and relevance scores.
        </p>
        <p>
          <strong>When to use:</strong> When using multi-level relevance judgments (0-5 scale).
        </p>
      </section>

      <section>
        <h2 id="choosing-metrics">Choosing the Right Metrics</h2>
        <div className="space-y-4 mt-4">
          <div className="p-4 bg-secondary-bg rounded-lg border border-border">
            <h3 className="font-semibold text-accent mb-2">For General Search</h3>
            <p className="text-sm text-text-secondary">Use Recall@10 + Hit Rate@10 + Precision@10</p>
          </div>
          <div className="p-4 bg-secondary-bg rounded-lg border border-border">
            <h3 className="font-semibold text-accent mb-2">For Q&A Systems</h3>
            <p className="text-sm text-text-secondary">Use Hit Rate@1 + MRR (first answer quality)</p>
          </div>
          <div className="p-4 bg-secondary-bg rounded-lg border border-border">
            <h3 className="font-semibold text-accent mb-2">For Multi-level Judgments</h3>
            <p className="text-sm text-text-secondary">Use NDCG@10 + Recall@10</p>
          </div>
        </div>
      </section>
    </DocumentationPage>
  );
};

export default Metrics;
