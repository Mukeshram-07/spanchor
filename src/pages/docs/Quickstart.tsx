import React from 'react';
import DocumentationPage from '../../components/docs/DocumentationPage';
import CodeEditor from '../../components/features/CodeEditor';

const Quickstart: React.FC = () => {
  return (
    <DocumentationPage
      title="Quickstart"
      description="Run your first SPANCHOR test in 5 minutes"
      route="/docs/quickstart"
    >
      <section className="py-8">
        <h2 id="overview" className="text-2xl font-bold text-slate-900 mb-4">Overview</h2>
        <p className="text-slate-700">
          This guide walks you through creating and running your first SPANCHOR test. 
          You'll create a gold set, configure evaluation, and inspect results.
        </p>
      </section>

      <section className="py-8 border-t border-slate-200">
        <h2 id="installation" className="text-2xl font-bold text-slate-900 mb-4">Installation</h2>
        <p className="text-slate-700 mb-4">
          Install SPANCHOR with pip:
        </p>
        <CodeEditor
          code={`pip install spanchor`}
          language="shell"
          filename="Shell"
          showLineNumbers={false}
          showResetButton={false}
        />
        <p className="text-slate-700 text-sm mt-4">
          Requires Python 3.11 or later. For more details, see the <a href="/docs/installation" className="text-sky-600 hover:underline font-semibold">Installation guide</a>.
        </p>
      </section>

      <section className="py-8 border-t border-slate-200">
        <h2 id="step-1" className="text-2xl font-bold text-slate-900 mb-4">Step 1: Create a Gold Set</h2>
        <p className="text-slate-700 mb-4">
          A gold set defines queries and their relevant documents. Create a file called <code className="bg-blue-50 text-blue-900 px-2 py-1 rounded font-mono text-sm font-semibold">gold_set.json</code>:
        </p>
        <CodeEditor
          code={`{
  "queries": [
    {
      "query": "machine learning fundamentals",
      "relevant_documents": ["doc_001", "doc_042", "doc_156"]
    },
    {
      "query": "neural networks architecture",
      "relevant_documents": ["doc_042", "doc_089", "doc_234"]
    },
    {
      "query": "deep learning optimization",
      "relevant_documents": ["doc_089", "doc_156", "doc_345"]
    }
  ]
}`}
          language="json"
          filename="gold_set.json"
          showLineNumbers={true}
          showCopyButton={true}
          showResetButton={false}
        />
      </section>

      <section className="py-8 border-t border-slate-200">
        <h2 id="step-2" className="text-2xl font-bold text-slate-900 mb-4">Step 2: Prepare Retrieval Results</h2>
        <p className="text-slate-700 mb-4">
          Run your retriever against the queries and save the results. Create <code className="bg-blue-50 text-blue-900 px-2 py-1 rounded font-mono text-sm font-semibold">retrieval_results.json</code>:
        </p>
        <CodeEditor
          code={`{
  "results": [
    {
      "query": "machine learning fundamentals",
      "retrieved_documents": ["doc_001", "doc_042", "doc_200", "doc_300"]
    },
    {
      "query": "neural networks architecture",
      "retrieved_documents": ["doc_089", "doc_042", "doc_156", "doc_400"]
    },
    {
      "query": "deep learning optimization",
      "retrieved_documents": ["doc_156", "doc_089", "doc_345", "doc_500"]
    }
  ]
}`}
          language="json"
          filename="retrieval_results.json"
          showLineNumbers={true}
          showCopyButton={true}
          showResetButton={false}
        />
      </section>

      <section className="py-8 border-t border-slate-200">
        <h2 id="step-3" className="text-2xl font-bold text-slate-900 mb-4">Step 3: Run Evaluation</h2>
        <p className="text-slate-700 mb-4">
          Create a Python script to evaluate your retriever. Create <code className="bg-blue-50 text-blue-900 px-2 py-1 rounded font-mono text-sm font-semibold">evaluate.py</code>:
        </p>
        <CodeEditor
          code={`from spanchor import evaluate, GoldSet
import json

# Load gold set
gold_set = GoldSet.from_json("gold_set.json")

# Load retrieval results
with open("retrieval_results.json") as f:
    retrieval_results = json.load(f)

# Run evaluation
result = evaluate(
    gold_set=gold_set,
    retrieved_results=retrieval_results,
    top_k=[1, 5, 10]
)

# Print results
result.print_summary()`}
          language="python"
          filename="evaluate.py"
          showLineNumbers={true}
          showCopyButton={true}
          showResetButton={false}
        />
        <p className="text-slate-700 text-sm mt-4">
          Run the evaluation:
        </p>
        <CodeEditor
          code={`python evaluate.py`}
          language="shell"
          filename="Shell"
          showLineNumbers={false}
          showCopyButton={true}
          showResetButton={false}
        />
      </section>

      <section className="py-8 border-t border-slate-200">
        <h2 id="step-4" className="text-2xl font-bold text-slate-900 mb-4">Step 4: Inspect Results</h2>
        <p className="text-slate-700 mb-4">
          SPANCHOR outputs metrics including:
        </p>
        <ul className="list-disc list-inside space-y-2 text-slate-700">
          <li><strong>Recall@K</strong> — fraction of relevant documents found in top K results</li>
          <li><strong>Precision@K</strong> — fraction of top K results that are relevant</li>
          <li><strong>Hit@K</strong> — percentage of queries with at least one relevant result in top K</li>
        </ul>
        <p className="text-slate-700 mt-4">
          Example output:
        </p>
        <CodeEditor
          code={`Recall@1:    0.667
Recall@5:    0.900
Recall@10:   1.000

Precision@1: 0.667
Precision@5: 0.800
Precision@10:0.750

Hit@1:       0.667
Hit@5:       1.000
Hit@10:      1.000`}
          language="plaintext"
          filename="Output"
          showLineNumbers={false}
          showCopyButton={true}
          showResetButton={false}
        />
      </section>

      <section className="py-8 border-t border-slate-200">
        <h2 id="step-5" className="text-2xl font-bold text-slate-900 mb-4">Step 5: Compare Baseline vs Candidate</h2>
        <p className="text-slate-700 mb-4">
          To detect regressions, compare your candidate retriever against a baseline. Create <code className="bg-blue-50 text-blue-900 px-2 py-1 rounded font-mono text-sm font-semibold">compare.py</code>:
        </p>
        <CodeEditor
          code={`from spanchor import evaluate, GoldSet
import json

gold_set = GoldSet.from_json("gold_set.json")

# Evaluate baseline
with open("baseline_results.json") as f:
    baseline_results = json.load(f)
baseline = evaluate(gold_set, baseline_results, top_k=[5])

# Evaluate candidate
with open("candidate_results.json") as f:
    candidate_results = json.load(f)
candidate = evaluate(gold_set, candidate_results, top_k=[5])

# Compare
comparison = baseline.compare(candidate)
comparison.print_summary()`}
          language="python"
          filename="compare.py"
          showLineNumbers={true}
          showCopyButton={true}
          showResetButton={false}
        />
      </section>

      <section className="py-8 border-t border-slate-200">
        <h2 id="next-steps" className="text-2xl font-bold text-slate-900 mb-4">What's Next?</h2>
        <p className="text-slate-700 mb-4">
          Now that you've run your first evaluation, explore:
        </p>
        <ul className="space-y-2 text-slate-700">
          <li>
            <a href="/docs/concepts" className="text-sky-600 hover:underline font-semibold">→ Core Concepts</a> — Deep dive into SPANCHOR architecture and design
          </li>
          <li>
            <a href="/examples" className="text-sky-600 hover:underline font-semibold">→ Examples</a> — Real-world workflows and use cases
          </li>
          <li>
            <a href="/api" className="text-sky-600 hover:underline font-semibold">→ API Reference</a> — Complete API documentation
          </li>
        </ul>
      </section>
    </DocumentationPage>
  );
};

export default Quickstart;
