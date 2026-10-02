import React from 'react';
import DocumentationPage from '../../components/docs/DocumentationPage';
import { SPANCHOR_VERSION_TAG } from '../../config/version';
import { CheckCircle2, XCircle, ArrowRight } from 'lucide-react';

const DocsIndex: React.FC = () => {
  return (
    <DocumentationPage
      title="SPANCHOR Documentation"
      description={`Source-anchored regression testing for RAG retrieval pipelines. ${SPANCHOR_VERSION_TAG}`}
      route="/docs"
    >
      {/* BADGES - positioned after hero header from DocsLayout */}
      <div className="flex flex-wrap gap-2 mb-8 pb-8 border-b border-slate-200">
        <span className="inline-flex items-center px-3 py-1 bg-blue-50 border border-blue-200 text-blue-700 text-xs font-mono font-semibold rounded-full">
          SOURCE-ANCHORED
        </span>
        <span className="inline-flex items-center px-3 py-1 bg-purple-50 border border-purple-200 text-purple-700 text-xs font-mono font-semibold rounded-full">
          DETERMINISTIC
        </span>
        <span className="inline-flex items-center px-3 py-1 bg-slate-50 border border-slate-300 text-slate-700 text-xs font-mono font-semibold rounded-full">
          LOCAL-FIRST
        </span>
        <span className="inline-flex items-center px-3 py-1 bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs font-mono font-semibold rounded-full">
          CI-READY
        </span>
      </div>

      {/* SECTION 1: WHAT IT DOES */}
      <section className="py-10 border-b border-slate-200">
        <h2 id="what-is" className="text-2xl font-bold text-slate-900 mb-4">What SPANCHOR does</h2>
        <p className="text-slate-700 mb-6">
          SPANCHOR evaluates whether retrieved evidence still matches <strong>source-anchored ground truth</strong> after a retrieval pipeline changes.
        </p>
        
        {/* Visual pipeline */}
        <div className="bg-slate-50 border border-slate-200 rounded-lg p-6 font-mono text-sm">
          <div className="flex flex-col gap-3 text-slate-700">
            <div className="text-center">
              <div className="text-slate-900 font-semibold">Question</div>
              <ArrowRight className="w-4 h-4 mx-auto my-1 text-slate-500" />
              <div className="text-slate-900 font-semibold">Retriever</div>
              <ArrowRight className="w-4 h-4 mx-auto my-1 text-slate-500" />
              <div className="text-slate-900 font-semibold">Retrieved Chunks</div>
              <ArrowRight className="w-4 h-4 mx-auto my-1 text-slate-500" />
              <div className="text-sky-600 font-bold bg-sky-50 px-3 py-1.5 rounded inline-block">★ SPANCHOR ★</div>
              <ArrowRight className="w-4 h-4 mx-auto my-1 text-slate-500" />
              <div className="text-slate-900 font-semibold">Evidence Match</div>
              <ArrowRight className="w-4 h-4 mx-auto my-1 text-slate-500" />
              <div className="text-slate-900 font-semibold">Metrics</div>
              <ArrowRight className="w-4 h-4 mx-auto my-1 text-slate-500" />
              <div className="text-slate-900 font-semibold">Regression Detection</div>
            </div>
          </div>
        </div>
      </section>

      {/* SECTION 2: THE PROBLEM */}
      <section className="py-10 border-b border-slate-200">
        <h2 id="problem" className="text-2xl font-bold text-slate-900 mb-6">The problem it solves</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* BEFORE */}
          <div className="bg-red-50 border border-red-200 rounded-lg p-5">
            <h3 className="font-semibold text-slate-900 mb-4 flex items-center gap-2">
              <span className="text-red-600 font-bold">✗</span> Without SPANCHOR
            </h3>
            <ul className="space-y-2 text-sm text-slate-700 font-mono">
              <li>Retriever changes</li>
              <li className="text-slate-500">↓</li>
              <li>Retrieval results change</li>
              <li className="text-slate-500">↓</li>
              <li className="text-red-600 font-semibold">No reliable signal</li>
              <li className="text-slate-500">↓</li>
              <li className="text-red-600 font-semibold">Potential degradation</li>
            </ul>
          </div>

          {/* WITH SPANCHOR */}
          <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-5">
            <h3 className="font-semibold text-slate-900 mb-4 flex items-center gap-2">
              <span className="text-emerald-600 font-bold">✓</span> With SPANCHOR
            </h3>
            <ul className="space-y-2 text-sm text-slate-700 font-mono">
              <li>Retriever changes</li>
              <li className="text-slate-500">↓</li>
              <li>Baseline vs Candidate</li>
              <li className="text-slate-500">↓</li>
              <li className="text-emerald-600 font-semibold">Source-anchored evaluation</li>
              <li className="text-slate-500">↓</li>
              <li className="text-emerald-600 font-semibold">Per-query regressions</li>
            </ul>
          </div>
        </div>
      </section>

      {/* SECTION 3: WHERE SPANCHOR SITS */}
      <section className="py-10 border-b border-slate-200">
        <h2 id="pipeline" className="text-2xl font-bold text-slate-900 mb-6">Where SPANCHOR sits in RAG</h2>
        <p className="text-slate-700 text-sm mb-4">SPANCHOR evaluates at the retrieval boundary — after you get results, before you hit the CI gate.</p>
        
        <div className="bg-slate-900 text-slate-300 font-mono text-xs p-6 rounded-lg border border-slate-700 overflow-x-auto">
          <pre className="text-sky-400 leading-relaxed whitespace-pre text-center">{`SOURCE DOCUMENTS
        ↓
  CANONICALIZATION
        ↓
    CHUNKING / INDEXING
        ↓
    RETRIEVAL
        ↓
  RETRIEVED RESULTS
        ↓
★ ★ ★ SPANCHOR ★ ★ ★  ← Evaluation happens here
        ↓
    METRICS
        ↓
 REGRESSION DETECTION
        ↓
  CI / TEST RESULTS`}</pre>
        </div>
      </section>

      {/* SECTION 4: HOW IT WORKS */}
      <section className="py-10 border-b border-slate-200">
        <h2 id="how-it-works" className="text-2xl font-bold text-slate-900 mb-6">How it works</h2>
        
        <div className="space-y-4">
          {/* 8-step compact flow */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            {[
              { num: '01', title: 'Source Documents', desc: 'Your raw document corpus' },
              { num: '02', title: 'Source Anchors', desc: 'Character spans + SHA-256 hashes' },
              { num: '03', title: 'Gold Set', desc: 'Q→A mappings to ground truth' },
              { num: '04', title: 'Run Retrieval', desc: 'Execute your candidate retriever' },
              { num: '05', title: 'Evaluate Spans', desc: 'Match retrieved to ground truth' },
              { num: '06', title: 'Calculate Metrics', desc: 'Recall@K, Precision@K, IoU' },
              { num: '07', title: 'Compare Baseline', desc: 'Candidate vs baseline perf' },
              { num: '08', title: 'Detect Regressions', desc: 'Per-query delta ranking' },
            ].map((step, i) => (
              <div key={i} className="bg-slate-50 border border-slate-200 rounded-lg p-4">
                <div className="text-xs font-mono font-bold text-sky-600 mb-1">{step.num}</div>
                <h4 className="text-sm font-semibold text-slate-900 mb-1">{step.title}</h4>
                <p className="text-xs text-slate-600">{step.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* SECTION 5: INSTALLATION */}
      <section className="py-10 border-b border-slate-200">
        <h2 id="installation" className="text-2xl font-bold text-slate-900 mb-4">Installation</h2>
        <pre className="bg-slate-900 text-slate-100 p-4 rounded-lg font-mono text-sm overflow-x-auto mb-3"><code>pip install spanchor</code></pre>
        <p className="text-slate-700 text-sm">
          Requires Python 3.11+. See the{' '}
          <a href="/docs/installation" className="text-sky-600 hover:underline font-semibold">Installation guide</a> for details.
        </p>
      </section>

      {/* SECTION 6: QUICK EXAMPLE */}
      <section className="py-10 border-b border-slate-200">
        <h2 id="quick-example" className="text-2xl font-bold text-slate-900 mb-4">Quick example</h2>
        <pre className="bg-slate-900 text-slate-100 p-4 rounded-lg font-mono text-xs sm:text-sm overflow-x-auto mb-3"><code>{`from spanchor import evaluate, GoldSet

# Load source-anchored ground truth
gold_set = GoldSet.from_json("gold_set.json")

# Evaluate candidate retrieval results
result = evaluate(
    gold_set=gold_set,
    retrieved_results="candidate_output.json",
    top_k=[1, 3, 5]
)

# Print regression summary
result.print_summary()`}</code></pre>
        <p className="text-slate-700 text-sm">
          See the <a href="/docs/quickstart" className="text-sky-600 hover:underline font-semibold">Quickstart</a> for a complete walkthrough.
        </p>
      </section>

      {/* SECTION 7: WHAT IT EVALUATES */}
      <section className="py-10 border-b border-slate-200">
        <h2 id="metrics" className="text-2xl font-bold text-slate-900 mb-6">What it evaluates</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Metrics per query */}
          <div>
            <h3 className="text-sm font-semibold text-slate-900 mb-3 uppercase tracking-wider text-slate-600">Per-Query Metrics</h3>
            <ul className="space-y-2 text-sm text-slate-700">
              <li><code className="bg-slate-100 px-2 py-1 rounded font-mono font-semibold text-slate-900">Recall@K</code> <span className="text-slate-600">— Gold text found in top K</span></li>
              <li><code className="bg-slate-100 px-2 py-1 rounded font-mono font-semibold text-slate-900">Hit@K</code> <span className="text-slate-600">— Binary match in top K</span></li>
              <li><code className="bg-slate-100 px-2 py-1 rounded font-mono font-semibold text-slate-900">Precision@K</code> <span className="text-slate-600">— Relevant results ratio</span></li>
              <li><code className="bg-slate-100 px-2 py-1 rounded font-mono font-semibold text-slate-900">IoU</code> <span className="text-slate-600">— Span overlap match</span></li>
              <li><code className="bg-slate-100 px-2 py-1 rounded font-mono font-semibold text-slate-900">Delta</code> <span className="text-slate-600">— vs baseline change</span></li>
            </ul>
          </div>

          {/* Aggregate output */}
          <div>
            <h3 className="text-sm font-semibold text-slate-900 mb-3 uppercase tracking-wider text-slate-600">Aggregate Output</h3>
            <ul className="space-y-2 text-sm text-slate-700">
              <li><span className="font-semibold text-slate-900">Improved</span> <span className="text-slate-600">— queries better than baseline</span></li>
              <li><span className="font-semibold text-slate-900">Unchanged</span> <span className="text-slate-600">— no performance delta</span></li>
              <li><span className="font-semibold text-slate-900">Regressed</span> <span className="text-slate-600">— worse than baseline</span></li>
              <li><span className="font-semibold text-slate-900">Per-query ranking</span> <span className="text-slate-600">— delta sorted</span></li>
              <li><span className="font-semibold text-slate-900">CI exit codes</span> <span className="text-slate-600">— regression thresholds</span></li>
            </ul>
          </div>
        </div>
      </section>

      {/* SECTION 8: SCOPE / DOES / DOES NOT */}
      <section className="py-10 border-b border-slate-200">
        <h2 id="scope" className="text-2xl font-bold text-slate-900 mb-6">SPANCHOR does & does not</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* DOES */}
          <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-6">
            <div className="flex items-center gap-2 mb-4">
              <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0" />
              <h3 className="text-lg font-semibold text-slate-900">SPANCHOR Does</h3>
            </div>
            <ul className="space-y-2 text-sm text-slate-700">
              <li>✓ Evaluate retrieval accuracy</li>
              <li>✓ Compare baseline vs candidate</li>
              <li>✓ Detect query-level regressions</li>
              <li>✓ Run in CI/CD pipelines</li>
              <li>✓ Work with any retriever</li>
              <li>✓ Stay stable across chunking changes</li>
            </ul>
          </div>

          {/* DOES NOT */}
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <div className="flex items-center gap-2 mb-4">
              <XCircle className="w-5 h-5 text-red-600 flex-shrink-0" />
              <h3 className="text-lg font-semibold text-slate-900">SPANCHOR Does NOT</h3>
            </div>
            <ul className="space-y-2 text-sm text-slate-700">
              <li>✗ Run retrievers (you provide results)</li>
              <li>✗ Generate embeddings or vectors</li>
              <li>✗ Judge LLM answer correctness</li>
              <li>✗ Use cloud/hosted services</li>
              <li>✗ Use LLM judges or semantic sim</li>
              <li>✗ Automate gold set creation</li>
            </ul>
          </div>
        </div>
      </section>

      {/* NEXT STEPS */}
      <section className="py-10">
        <h2 id="next-steps" className="text-2xl font-bold text-slate-900 mb-6">Next steps</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <a href="/docs/quickstart" className="bg-white border border-slate-300 hover:border-sky-400 hover:shadow-md rounded-lg p-5 transition-all">
            <div className="text-sm font-semibold text-sky-600 mb-2">→ Quickstart</div>
            <p className="text-xs text-slate-600">Step-by-step tutorial to get running in 5 minutes.</p>
          </a>
          <a href="/examples" className="bg-white border border-slate-300 hover:border-sky-400 hover:shadow-md rounded-lg p-5 transition-all">
            <div className="text-sm font-semibold text-sky-600 mb-2">→ Examples</div>
            <p className="text-xs text-slate-600">Real-world workflows with complete code.</p>
          </a>
          <a href="https://github.com/Mukeshram-07/spanchor" target="_blank" rel="noopener noreferrer" className="bg-white border border-slate-300 hover:border-sky-400 hover:shadow-md rounded-lg p-5 transition-all">
            <div className="text-sm font-semibold text-sky-600 mb-2">→ GitHub</div>
            <p className="text-xs text-slate-600">Issues, discussions, and community.</p>
          </a>
        </div>
      </section>
    </DocumentationPage>
  );
};

export default DocsIndex;
