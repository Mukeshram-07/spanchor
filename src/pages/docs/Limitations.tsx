import React from 'react';
import DocumentationPage from '../../components/docs/DocumentationPage';

const Limitations: React.FC = () => {
  return (
    <DocumentationPage
      title="Limitations & Known Issues"
      description="Understand the current limitations of SPANCHOR"
      route="/docs/limitations"
    >
      <section>
        <h2 id="current-limitations">Current Limitations</h2>
        <p>
          While SPANCHOR is powerful, it has some current limitations. We're working to address these.
        </p>
      </section>

      <section>
        <h2 id="gold-set-dependencies">Gold Set Dependencies</h2>
        <p>
          <strong>Issue:</strong> Evaluation quality is directly dependent on gold set quality.
        </p>
        <p className="mt-2">
          <strong>Impact:</strong> Poor quality or biased gold sets lead to poor evaluation results.
        </p>
        <p className="mt-2">
          <strong>Mitigation:</strong> Invest in curating high-quality, representative gold sets.
        </p>
      </section>

      <section>
        <h2 id="static-gold-sets">Static Gold Sets</h2>
        <p>
          <strong>Issue:</strong> Gold sets don't automatically update with content changes.
        </p>
        <p className="mt-2">
          <strong>Impact:</strong> Tests may become less representative over time.
        </p>
        <p className="mt-2">
          <strong>Mitigation:</strong> Periodically review and update gold sets.
        </p>
      </section>

      <section>
        <h2 id="limited-adapters">Limited Adapter Support</h2>
        <p>
          <strong>Issue:</strong> Not all search backends are supported out of the box.
        </p>
        <p className="mt-2">
          <strong>Impact:</strong> You may need to implement a custom adapter.
        </p>
        <p className="mt-2">
          <strong>Mitigation:</strong> See <a href="/docs/adapters" className="text-accent hover:underline">Adapters documentation</a> for creating custom adapters.
        </p>
      </section>

      <section>
        <h2 id="scaling">Scalability Considerations</h2>
        <p>
          <strong>Issue:</strong> Very large gold sets (100K+ queries) may require optimization.
        </p>
        <p className="mt-2">
          <strong>Impact:</strong> Evaluation time increases linearly with gold set size.
        </p>
        <p className="mt-2">
          <strong>Mitigation:</strong> Use batching, caching, and parallel evaluation.
        </p>
      </section>

      <section>
        <h2 id="metric-limitations">Metric Limitations</h2>
        <p>
          <strong>Issue:</strong> Standard IR metrics don't capture all dimensions of search quality.
        </p>
        <p className="mt-2">
          <strong>Examples:</strong>
        </p>
        <ul>
          <li>Diversity of results</li>
          <li>Freshness of content</li>
          <li>User satisfaction</li>
          <li>Performance speed</li>
        </ul>
        <p className="mt-2">
          <strong>Mitigation:</strong> Combine multiple metrics and gather user feedback.
        </p>
      </section>

      <section>
        <h2 id="relevance-judgments">Relevance Judgment Subjectivity</h2>
        <p>
          <strong>Issue:</strong> What's "relevant" can be subjective and context-dependent.
        </p>
        <p className="mt-2">
          <strong>Impact:</strong> Different annotators may label results differently.
        </p>
        <p className="mt-2">
          <strong>Mitigation:</strong> Use inter-annotator agreement studies and clear guidelines.
        </p>
      </section>

      <section>
        <h2 id="language-support">Language Support</h2>
        <p>
          <strong>Issue:</strong> SPANCHOR primarily targets English-language content.
        </p>
        <p className="mt-2">
          <strong>Impact:</strong> Multi-language evaluation may be less effective.
        </p>
        <p className="mt-2">
          <strong>Status:</strong> Multi-language support is on the roadmap.
        </p>
      </section>

      <section>
        <h2 id="known-issues">Known Issues</h2>
        <div className="space-y-4 my-4">
          <div className="p-4 bg-secondary-bg rounded-lg border border-border">
            <h3 className="font-semibold text-accent">Issue #1: Large Batch Timeouts</h3>
            <p className="text-sm text-text-secondary mt-1">
              Evaluating 10K+ queries in a single batch may timeout. Workaround: Use pagination.
            </p>
          </div>
          <div className="p-4 bg-secondary-bg rounded-lg border border-border">
            <h3 className="font-semibold text-accent">Issue #2: Embedding Cache</h3>
            <p className="text-sm text-text-secondary mt-1">
              Embedding cache not cleared between test runs. Workaround: Restart Python process.
            </p>
          </div>
          <div className="p-4 bg-secondary-bg rounded-lg border border-border">
            <h3 className="font-semibold text-accent">Issue #3: Unicode in Gold Sets</h3>
            <p className="text-sm text-text-secondary mt-1">
              Some Unicode characters may not be handled correctly. Workaround: Use UTF-8 encoding.
            </p>
          </div>
        </div>
      </section>

      <section>
        <h2 id="roadmap">Roadmap</h2>
        <p>
          We're actively working on improvements:
        </p>
        <ul>
          <li>Multi-language support</li>
          <li>Real-time metrics streaming</li>
          <li>Advanced visualization dashboard</li>
          <li>Integration with popular LLM frameworks</li>
          <li>GraphQL API</li>
        </ul>
      </section>

      <section>
        <h2 id="feedback">Report Issues</h2>
        <p>
          Found a bug or have a feature request? 
          <a href="https://github.com/Mukeshram-07/spanchor/issues" className="text-accent hover:underline" target="_blank" rel="noopener noreferrer">
            Open an issue on GitHub
          </a>
        </p>
      </section>
    </DocumentationPage>
  );
};

export default Limitations;
