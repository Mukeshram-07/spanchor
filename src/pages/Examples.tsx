import React from 'react';
import Navbar from '../components/layouts/Navbar';
import Footer from '../components/layouts/Footer';
import CodeEditor from '../components/features/CodeEditor';
import { ArrowRight, TrendingUp, AlertTriangle, Minus } from 'lucide-react';

const Examples: React.FC = () => {
  return (
    <div className="min-h-screen bg-white flex flex-col">
      <Navbar />

      <main className="flex-1 py-12 px-4 sm:px-6 lg:px-8 max-w-4xl mx-auto w-full">
        {/* HERO SECTION */}
        <section className="mb-16">
          <h1 className="text-4xl font-bold text-slate-900 mb-3">Examples</h1>
          <p className="text-lg text-slate-700 mb-4">
            See how SPANCHOR fits into real RAG retrieval evaluation workflows.
          </p>
          <p className="text-slate-600">
            These examples show how to define source-anchored gold sets, evaluate retrieval results, and detect regressions between baseline and candidate runs.
          </p>
        </section>

        {/* NAVIGATION / OVERVIEW */}
        <section className="mb-16 py-8 border-t border-b border-slate-200">
          <h2 className="text-sm font-mono font-semibold text-slate-500 uppercase tracking-wider mb-6">Examples Overview</h2>
          <div className="space-y-3">
            <a href="#example-01" className="block group py-3 px-4 rounded border border-slate-200 hover:border-sky-400 hover:bg-blue-50 transition-all">
              <div className="flex items-start justify-between">
                <div>
                  <div className="text-xs font-mono font-bold text-sky-600 mb-1">01</div>
                  <h3 className="font-semibold text-slate-900">Basic Retrieval Evaluation</h3>
                  <p className="text-sm text-slate-600 mt-1">Evaluate whether retrieved chunks contain the source evidence expected for each query.</p>
                </div>
                <ArrowRight className="w-5 h-5 text-slate-400 group-hover:text-sky-600 mt-1 flex-shrink-0 transition-colors" />
              </div>
            </a>
            <a href="#example-02" className="block group py-3 px-4 rounded border border-slate-200 hover:border-sky-400 hover:bg-blue-50 transition-all">
              <div className="flex items-start justify-between">
                <div>
                  <div className="text-xs font-mono font-bold text-sky-600 mb-1">02</div>
                  <h3 className="font-semibold text-slate-900">Regression Comparison</h3>
                  <p className="text-sm text-slate-600 mt-1">Compare two retrieval runs against the same source-anchored evaluation set.</p>
                </div>
                <ArrowRight className="w-5 h-5 text-slate-400 group-hover:text-sky-600 mt-1 flex-shrink-0 transition-colors" />
              </div>
            </a>
            <a href="#example-03" className="block group py-3 px-4 rounded border border-slate-200 hover:border-sky-400 hover:bg-blue-50 transition-all">
              <div className="flex items-start justify-between">
                <div>
                  <div className="text-xs font-mono font-bold text-sky-600 mb-1">03</div>
                  <h3 className="font-semibold text-slate-900">CI Regression Gate</h3>
                  <p className="text-sm text-slate-600 mt-1">Use SPANCHOR in CI to prevent retrieval regressions from silently reaching production.</p>
                </div>
                <ArrowRight className="w-5 h-5 text-slate-400 group-hover:text-sky-600 mt-1 flex-shrink-0 transition-colors" />
              </div>
            </a>
          </div>
        </section>

        {/* EXAMPLE 01: BASIC RETRIEVAL EVALUATION */}
        <section id="example-01" className="mb-20 scroll-mt-20">
          <div className="mb-8">
            <div className="text-xs font-mono font-bold text-sky-600 mb-2">01</div>
            <h2 className="text-3xl font-bold text-slate-900 mb-3">Basic Retrieval Evaluation</h2>
            <p className="text-slate-700">
              Evaluate whether retrieved chunks contain the source evidence expected for each query.
            </p>
          </div>

          {/* Expected Flow */}
          <div className="mb-8 p-6 bg-slate-50 rounded-lg border border-slate-200">
            <h3 className="text-sm font-mono font-semibold text-slate-600 uppercase tracking-wider mb-4">Expected Flow</h3>
            <div className="space-y-2 text-sm text-slate-700 font-mono">
              <div className="flex items-center gap-2">
                <div className="font-semibold text-slate-900">Source Document</div>
                <ArrowRight className="w-4 h-4 text-slate-400" />
              </div>
              <div className="flex items-center gap-2 ml-4">
                <div className="text-slate-600">↓</div>
              </div>
              <div className="flex items-center gap-2">
                <div className="font-semibold text-slate-900">Gold-Set Anchor</div>
                <ArrowRight className="w-4 h-4 text-slate-400" />
              </div>
              <div className="flex items-center gap-2 ml-4">
                <div className="text-slate-600">↓</div>
              </div>
              <div className="flex items-center gap-2">
                <div className="font-semibold text-slate-900">Retrieval Results</div>
                <ArrowRight className="w-4 h-4 text-slate-400" />
              </div>
              <div className="flex items-center gap-2 ml-4">
                <div className="text-slate-600">↓</div>
              </div>
              <div className="flex items-center gap-2">
                <div className="font-semibold text-sky-600">SPANCHOR Evaluation</div>
                <ArrowRight className="w-4 h-4 text-slate-400" />
              </div>
              <div className="flex items-center gap-2 ml-4">
                <div className="text-slate-600">↓</div>
              </div>
              <div className="font-semibold text-slate-900">Recall / Precision / Hit Metrics</div>
            </div>
          </div>

          {/* Python Code */}
          <div className="mb-8">
            <h3 className="text-sm font-mono font-semibold text-slate-600 uppercase tracking-wider mb-3">Python Example</h3>
            <CodeEditor
              code={`from spanchor import evaluate, GoldSet

# Load ground-truth source anchors
gold_set = GoldSet.from_json("gold_set.json")

# Evaluate candidate retrieval outputs
results = evaluate(
    gold_set=gold_set,
    retrieved_results="candidate_retrieved.json",
    top_k=[1, 3, 5]
)

results.print_summary()`}
              language="python"
              filename="evaluate.py"
              showLineNumbers={true}
              showCopyButton={true}
              showResetButton={false}
            />
          </div>

          {/* Expected Output */}
          <div className="p-6 bg-slate-900 rounded-lg border border-slate-700">
            <h3 className="text-xs font-mono font-bold text-slate-400 uppercase tracking-wider mb-3">Example Output</h3>
            <div className="space-y-1 font-mono text-xs text-slate-300">
              <div>Recall@1:    0.667</div>
              <div>Recall@3:    0.800</div>
              <div>Recall@5:    0.900</div>
              <div className="mt-2">Precision@1: 0.667</div>
              <div>Precision@3: 0.733</div>
              <div>Precision@5: 0.800</div>
              <div className="mt-2">Hit@1:       0.667</div>
              <div>Hit@3:       0.900</div>
              <div>Hit@5:       1.000</div>
            </div>
          </div>
        </section>

        {/* EXAMPLE 02: REGRESSION COMPARISON */}
        <section id="example-02" className="mb-20 scroll-mt-20">
          <div className="mb-8">
            <div className="text-xs font-mono font-bold text-sky-600 mb-2">02</div>
            <h2 className="text-3xl font-bold text-slate-900 mb-3">Regression Comparison</h2>
            <p className="text-slate-700">
              Compare two retrieval runs against the same source-anchored evaluation set.
            </p>
          </div>

          {/* Concept Explanation */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div className="p-6 bg-slate-50 rounded-lg border border-slate-200">
              <h3 className="font-semibold text-slate-900 mb-3">Baseline</h3>
              <p className="text-sm text-slate-600 mb-4">Your existing retrieval system (e.g., BM25, previous embedding model).</p>
              <CodeEditor
                code={`{
  "results": [
    {
      "query": "machine learning",
      "retrieved": ["doc_001", "doc_042"]
    }
  ]
}`}
                language="json"
                filename="baseline.json"
                showLineNumbers={false}
                showCopyButton={true}
                showResetButton={false}
              />
            </div>

            <div className="p-6 bg-slate-50 rounded-lg border border-slate-200">
              <h3 className="font-semibold text-slate-900 mb-3">Candidate</h3>
              <p className="text-sm text-slate-600 mb-4">Your new retrieval system (e.g., Hybrid search, new embedding model).</p>
              <CodeEditor
                code={`{
  "results": [
    {
      "query": "machine learning",
      "retrieved": ["doc_001", "doc_089"]
    }
  ]
}`}
                language="json"
                filename="candidate.json"
                showLineNumbers={false}
                showCopyButton={true}
                showResetButton={false}
              />
            </div>
          </div>

          {/* Comparison Code */}
          <div className="mb-8">
            <h3 className="text-sm font-mono font-semibold text-slate-600 uppercase tracking-wider mb-3">Comparison Script</h3>
            <CodeEditor
              code={`from spanchor import evaluate, GoldSet

gold_set = GoldSet.from_json("gold_set.json")

# Evaluate baseline
baseline = evaluate(
    gold_set=gold_set,
    retrieved_results="baseline.json",
    top_k=[5]
)

# Evaluate candidate
candidate = evaluate(
    gold_set=gold_set,
    retrieved_results="candidate.json",
    top_k=[5]
)

# Compare results
comparison = baseline.compare(candidate)
comparison.print_summary()`}
              language="python"
              filename="compare.py"
              showLineNumbers={true}
              showCopyButton={true}
              showResetButton={false}
            />
          </div>

          {/* Regression Table */}
          <div>
            <h3 className="text-sm font-mono font-semibold text-slate-600 uppercase tracking-wider mb-3">Per-Query Changes</h3>
            <div className="overflow-x-auto rounded-lg border border-slate-200">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-slate-50 border-b border-slate-200">
                    <th className="px-4 py-3 text-left font-mono font-semibold text-slate-700">Query</th>
                    <th className="px-4 py-3 text-center font-mono font-semibold text-slate-700">Baseline</th>
                    <th className="px-4 py-3 text-center font-mono font-semibold text-slate-700">Candidate</th>
                    <th className="px-4 py-3 text-center font-mono font-semibold text-slate-700">Delta</th>
                    <th className="px-4 py-3 text-center font-mono font-semibold text-slate-700">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200">
                  <tr>
                    <td className="px-4 py-3 text-slate-700">machine learning</td>
                    <td className="px-4 py-3 text-center text-slate-700 font-mono">0.800</td>
                    <td className="px-4 py-3 text-center text-slate-700 font-mono">0.900</td>
                    <td className="px-4 py-3 text-center text-slate-900 font-mono font-semibold">+0.100</td>
                    <td className="px-4 py-3 text-center">
                      <span className="inline-flex items-center gap-1 text-xs px-2 py-1 rounded border border-emerald-200 bg-emerald-50">
                        <TrendingUp className="w-3 h-3 text-emerald-600" />
                        <span className="text-emerald-700 font-semibold">Improved</span>
                      </span>
                    </td>
                  </tr>
                  <tr>
                    <td className="px-4 py-3 text-slate-700">neural networks</td>
                    <td className="px-4 py-3 text-center text-slate-700 font-mono">0.750</td>
                    <td className="px-4 py-3 text-center text-slate-700 font-mono">0.750</td>
                    <td className="px-4 py-3 text-center text-slate-500 font-mono">0.000</td>
                    <td className="px-4 py-3 text-center">
                      <span className="inline-flex items-center gap-1 text-xs px-2 py-1 rounded border border-slate-200 bg-slate-50">
                        <Minus className="w-3 h-3 text-slate-600" />
                        <span className="text-slate-600 font-semibold">Unchanged</span>
                      </span>
                    </td>
                  </tr>
                  <tr>
                    <td className="px-4 py-3 text-slate-700">deep learning optimization</td>
                    <td className="px-4 py-3 text-center text-slate-700 font-mono">0.850</td>
                    <td className="px-4 py-3 text-center text-slate-700 font-mono">0.420</td>
                    <td className="px-4 py-3 text-center text-slate-900 font-mono font-semibold">-0.430</td>
                    <td className="px-4 py-3 text-center">
                      <span className="inline-flex items-center gap-1 text-xs px-2 py-1 rounded border border-red-200 bg-red-50">
                        <AlertTriangle className="w-3 h-3 text-red-600" />
                        <span className="text-red-700 font-semibold">Regressed</span>
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </section>

        {/* EXAMPLE 03: CI REGRESSION GATE */}
        <section id="example-03" className="mb-20 scroll-mt-20">
          <div className="mb-8">
            <div className="text-xs font-mono font-bold text-sky-600 mb-2">03</div>
            <h2 className="text-3xl font-bold text-slate-900 mb-3">CI Regression Gate</h2>
            <p className="text-slate-700">
              Use SPANCHOR in CI to prevent retrieval regressions from silently reaching production.
            </p>
          </div>

          {/* Terminal Workflow */}
          <div className="mb-8">
            <h3 className="text-sm font-mono font-semibold text-slate-600 uppercase tracking-wider mb-3">Workflow</h3>
            <CodeEditor
              code={`$ spanchor evaluate candidate.json --top-k 5
✓ Loading gold set...
✓ 100 queries evaluated
✓ Evaluation complete

$ spanchor compare baseline.json candidate.json
→ Computing per-query deltas...
→ Detecting regressions...
✓ Comparison complete

Improved:   6 queries
Unchanged:  75 queries
Regressed:  19 queries

⚠ 19 regressions detected. CI gate FAILED.`}
              language="shell"
              filename="Shell"
              showLineNumbers={false}
              showCopyButton={true}
              showResetButton={false}
            />
          </div>

          {/* Integration Info */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="p-6 bg-slate-50 rounded-lg border border-slate-200">
              <h3 className="font-semibold text-slate-900 mb-2">GitHub Actions</h3>
              <CodeEditor
                code={`- name: SPANCHOR Regression Gate
  run: |
    spanchor evaluate \\
      candidate.json \\
      --top-k 5 \\
      --fail-on-regressions 19`}
                language="yaml"
                filename=".github/workflows/ci.yml"
                showLineNumbers={false}
                showCopyButton={true}
                showResetButton={false}
              />
            </div>

            <div className="p-6 bg-slate-50 rounded-lg border border-slate-200">
              <h3 className="font-semibold text-slate-900 mb-2">Exit Code</h3>
              <CodeEditor
                code={`# Success: no regressions
$ echo $?
0

# Failure: regressions detected
$ echo $?
1`}
                language="shell"
                filename="Shell"
                showLineNumbers={false}
                showCopyButton={true}
                showResetButton={false}
              />
            </div>
          </div>

          <p className="text-xs text-slate-500 mt-6 italic">
            Note: This is an illustrative deterministic example. Actual numbers depend on your gold set and retrieval system.
          </p>
        </section>

        {/* DECISION GUIDE */}
        <section className="mb-16 py-8 border-t border-slate-200">
          <h2 className="text-xl font-bold text-slate-900 mb-6">When to use which example?</h2>
          <div className="space-y-4">
            <div className="flex gap-4">
              <div className="text-sky-600 font-bold flex-shrink-0">→</div>
              <div>
                <h3 className="font-semibold text-slate-900">Need to validate retrieval?</h3>
                <p className="text-sm text-slate-600 mt-1">See <a href="#example-01" className="text-sky-600 hover:underline font-semibold">Example 01: Basic Retrieval Evaluation</a></p>
              </div>
            </div>
            <div className="flex gap-4">
              <div className="text-sky-600 font-bold flex-shrink-0">→</div>
              <div>
                <h3 className="font-semibold text-slate-900">Need to compare a new retriever against an existing one?</h3>
                <p className="text-sm text-slate-600 mt-1">See <a href="#example-02" className="text-sky-600 hover:underline font-semibold">Example 02: Regression Comparison</a></p>
              </div>
            </div>
            <div className="flex gap-4">
              <div className="text-sky-600 font-bold flex-shrink-0">→</div>
              <div>
                <h3 className="font-semibold text-slate-900">Need to enforce retrieval quality in CI?</h3>
                <p className="text-sm text-slate-600 mt-1">See <a href="#example-03" className="text-sky-600 hover:underline font-semibold">Example 03: CI Regression Gate</a></p>
              </div>
            </div>
          </div>
        </section>

        {/* NEXT STEPS */}
        <section className="py-8 border-t border-slate-200">
          <h2 className="text-xl font-bold text-slate-900 mb-6">Next Steps</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <a href="/docs/quickstart" className="block p-4 rounded border border-slate-200 hover:border-sky-400 hover:bg-blue-50 transition-all group">
              <div className="font-semibold text-slate-900 group-hover:text-sky-600 transition-colors">→ Quickstart</div>
              <p className="text-sm text-slate-600 mt-1">Step-by-step guide to run your first test.</p>
            </a>
            <a href="/api" className="block p-4 rounded border border-slate-200 hover:border-sky-400 hover:bg-blue-50 transition-all group">
              <div className="font-semibold text-slate-900 group-hover:text-sky-600 transition-colors">→ API Reference</div>
              <p className="text-sm text-slate-600 mt-1">Complete API documentation.</p>
            </a>
            <a href="/docs/architecture" className="block p-4 rounded border border-slate-200 hover:border-sky-400 hover:bg-blue-50 transition-all group">
              <div className="font-semibold text-slate-900 group-hover:text-sky-600 transition-colors">→ Architecture</div>
              <p className="text-sm text-slate-600 mt-1">System design and components.</p>
            </a>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
};

export default Examples;
