import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import Navbar from '../components/layouts/Navbar';
import Footer from '../components/layouts/Footer';
import { Copy, Check, Terminal, ArrowRight, GitBranch, Package } from 'lucide-react';
import { SPANCHOR_VERSION_TAG } from '../config/version';

/* ─────────────────────────────────────────────────────── */
/*  1. HERO                                                */
/* ─────────────────────────────────────────────────────── */
const Hero: React.FC = () => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText('pip install spanchor');
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <section className="py-20 md:py-28 border-b border-slate-200">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1 bg-slate-100 text-slate-600 rounded-full text-xs font-mono font-medium border border-slate-200 mb-6">
          {SPANCHOR_VERSION_TAG} &mdash; Open Source &middot; Apache-2.0 &middot; Python 3.11–3.13
        </div>

        <h1 className="text-5xl sm:text-6xl font-extrabold text-slate-900 tracking-tight leading-[1.1] mb-6">
          SPANCHOR
        </h1>

        <p className="text-xl sm:text-2xl text-slate-600 font-normal leading-relaxed mb-4 max-w-3xl mx-auto">
          Source-anchored regression testing for RAG retrieval pipelines.
        </p>

        <p className="text-base text-slate-500 leading-relaxed mb-10 max-w-2xl mx-auto">
          SPANCHOR evaluates whether your retrieval pipeline consistently
          finds the right source evidence — and detects when pipeline changes
          cause regressions.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-10">
          <Link
            to="/docs/quickstart"
            className="inline-flex items-center gap-2 px-6 py-3 bg-slate-900 hover:bg-slate-700 text-white font-medium rounded-md text-sm transition-colors shadow-sm"
          >
            Get Started <ArrowRight className="w-4 h-4" />
          </Link>
          <Link
            to="/docs"
            className="inline-flex items-center gap-2 px-6 py-3 bg-white border border-slate-300 hover:border-slate-400 text-slate-700 font-medium rounded-md text-sm transition-colors"
          >
            Documentation
          </Link>
          <a
            href="https://github.com/Mukeshram-07/spanchor"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-6 py-3 bg-white border border-slate-300 hover:border-slate-400 text-slate-700 font-medium rounded-md text-sm transition-colors"
          >
            <GitBranch className="w-4 h-4" /> GitHub
          </a>
        </div>

        {/* Install Command */}
        <div className="inline-flex items-center gap-4 bg-slate-950 text-slate-100 rounded-md px-5 py-3 font-mono text-sm border border-slate-800 shadow-md">
          <div className="flex items-center gap-2.5">
            <Terminal className="w-4 h-4 text-sky-400" />
            <span className="text-slate-400">$</span>
            <span>pip install spanchor</span>
          </div>
          <button
            onClick={handleCopy}
            className="text-slate-500 hover:text-white transition-colors ml-2"
            aria-label="Copy install command"
          >
            {copied ? <Check className="w-4 h-4 text-sky-400" /> : <Copy className="w-4 h-4" />}
          </button>
        </div>
      </div>
    </section>
  );
};

/* ─────────────────────────────────────────────────────── */
/*  2. WHAT IT DOES                                        */
/* ─────────────────────────────────────────────────────── */
const WhatItDoes: React.FC = () => (
  <section className="py-16 border-b border-slate-200">
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
      <h2 className="text-2xl font-bold text-slate-900 mb-4">What SPANCHOR does</h2>
      <p className="text-base text-slate-600 leading-relaxed mb-8 max-w-3xl">
        SPANCHOR evaluates retrieved evidence against source-anchored ground truth
        and compares retrieval runs to detect query-level regressions. It gives you
        a deterministic, math-based answer to the question:{' '}
        <em>"Is my retrieval pipeline still finding the right content?"</em>
      </p>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {[
          {
            title: 'Source Anchors',
            desc: 'Ground truth tied directly to character offsets in source documents — stable across chunking changes.',
          },
          {
            title: 'Deterministic Metrics',
            desc: 'Recall@K, Precision@K, Hit@K, and IoU computed with exact character overlap math. No LLM judges.',
          },
          {
            title: 'Baseline vs Candidate',
            desc: 'Compare two retriever runs to measure which queries improved, regressed, or stayed the same.',
          },
          {
            title: 'CI Integration',
            desc: 'Automated exit codes and summary reports for pytest and GitHub Actions pipelines.',
          },
        ].map((item) => (
          <div key={item.title} className="p-5 border border-slate-200 rounded-lg bg-white">
            <h3 className="text-sm font-semibold text-slate-900 mb-1.5">{item.title}</h3>
            <p className="text-sm text-slate-600 leading-relaxed">{item.desc}</p>
          </div>
        ))}
      </div>
    </div>
  </section>
);

/* ─────────────────────────────────────────────────────── */
/*  3. THE PROBLEM                                         */
/* ─────────────────────────────────────────────────────── */
const TheProblem: React.FC = () => (
  <section className="py-16 border-b border-slate-200 bg-slate-50">
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
      <h2 className="text-2xl font-bold text-slate-900 mb-4">The problem</h2>
      <p className="text-base text-slate-600 leading-relaxed mb-6 max-w-3xl">
        RAG pipeline changes can silently alter which evidence is retrieved.
        Any of the following can change retrieval behavior without obvious indication:
      </p>
      <ul className="grid grid-cols-2 sm:grid-cols-3 gap-2 mb-6">
        {[
          'Chunk size or overlap',
          'Embedding model version',
          'Retriever algorithm',
          'Vector database upgrade',
          'Reranking strategy',
          'Document updates',
        ].map((item) => (
          <li
            key={item}
            className="flex items-center gap-2 px-3 py-2 bg-white border border-slate-200 rounded text-sm text-slate-700 font-mono"
          >
            <span className="w-1.5 h-1.5 rounded-full bg-slate-400 flex-shrink-0" />
            {item}
          </li>
        ))}
      </ul>
      <p className="text-base text-slate-600 leading-relaxed max-w-3xl">
        Without regression tests, you only discover these changes when your application
        produces wrong answers. SPANCHOR makes retrieval changes testable before they reach production.
      </p>
    </div>
  </section>
);

/* ─────────────────────────────────────────────────────── */
/*  4. HOW IT WORKS — simple flow diagram                  */
/* ─────────────────────────────────────────────────────── */
const HowItWorks: React.FC = () => {
  const steps = [
    { label: 'Source Documents', detail: 'Your raw corpus files' },
    { label: 'Canonicalization', detail: 'Stable character offsets' },
    { label: 'Retrieval', detail: 'Your retriever returns chunks' },
    { label: 'SPANCHOR', detail: 'Evaluates against anchors' },
    { label: 'Metrics', detail: 'Recall@K, Hit@K, Precision@K' },
    { label: 'Regression Detection', detail: 'Query-level comparisons' },
    { label: 'CI / Test Results', detail: 'pytest exit codes, reports' },
  ];

  return (
    <section className="py-16 border-b border-slate-200">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <h2 className="text-2xl font-bold text-slate-900 mb-8">How it works</h2>
        <div className="flex flex-col gap-0">
          {steps.map((step, idx) => (
            <div key={step.label} className="flex items-start gap-4">
              <div className="flex flex-col items-center">
                <div className="w-8 h-8 rounded-full bg-slate-900 text-white flex items-center justify-center text-xs font-bold flex-shrink-0">
                  {idx + 1}
                </div>
                {idx < steps.length - 1 && (
                  <div className="w-px h-8 bg-slate-200 my-1" />
                )}
              </div>
              <div className="pt-1 pb-6">
                <span className="text-sm font-semibold text-slate-900">{step.label}</span>
                <span className="text-sm text-slate-500 ml-2">&mdash; {step.detail}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

/* ─────────────────────────────────────────────────────── */
/*  5. CODE EXAMPLE                                        */
/* ─────────────────────────────────────────────────────── */
const codeExample = `from spanchor import evaluate, GoldSet

# Load source-anchored ground truth
gold_set = GoldSet.from_json("gold_set.json")

# Evaluate candidate retrieval results
result = evaluate(
    gold_set=gold_set,
    retrieved_results="candidate_output.json",
    top_k=[1, 3, 5]
)

# Print summary with regression counts
result.print_summary()`;

const CodeExample: React.FC = () => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(codeExample);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <section className="py-16 border-b border-slate-200 bg-slate-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <h2 className="text-2xl font-bold text-slate-900 mb-2">Quick example</h2>
        <p className="text-sm text-slate-500 mb-6">
          A minimal evaluation run using the SPANCHOR Python API.
        </p>
        <div className="bg-slate-900 rounded-lg overflow-hidden border border-slate-800 shadow-md">
          <div className="flex items-center justify-between px-4 py-2.5 bg-slate-950 border-b border-slate-800">
            <span className="text-xs font-mono text-slate-400">eval_pipeline.py</span>
            <button
              onClick={handleCopy}
              className="flex items-center gap-1.5 text-xs font-mono text-slate-400 hover:text-white transition-colors"
              aria-label="Copy code"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-sky-400" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? 'Copied' : 'Copy'}</span>
            </button>
          </div>
          <pre className="p-5 font-mono text-sm text-slate-200 overflow-x-auto leading-relaxed">
            <code>{codeExample}</code>
          </pre>
        </div>
        <p className="text-xs text-slate-500 mt-3">
          See the full <Link to="/examples" className="text-sky-600 hover:underline">Examples page</Link> or{' '}
          <Link to="/docs/quickstart" className="text-sky-600 hover:underline">Quickstart guide</Link> for more.
        </p>
      </div>
    </section>
  );
};

/* ─────────────────────────────────────────────────────── */
/*  6. DEVELOPER WORKFLOW                                   */
/* ─────────────────────────────────────────────────────── */
const DeveloperWorkflow: React.FC = () => {
  const steps = [
    { step: 'Install', cmd: 'pip install spanchor' },
    { step: 'Create or load gold set', cmd: 'GoldSet.from_json("gold.json")' },
    { step: 'Run retrieval', cmd: 'your_retriever.retrieve(queries)' },
    { step: 'Evaluate', cmd: 'evaluate(gold_set, retrieved)' },
    { step: 'Compare to baseline', cmd: 'compare(baseline, candidate)' },
    { step: 'Run in CI', cmd: 'pytest tests/test_retrieval.py' },
  ];

  return (
    <section className="py-16 border-b border-slate-200">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <h2 className="text-2xl font-bold text-slate-900 mb-8">Developer workflow</h2>
        <div className="space-y-3">
          {steps.map((item, idx) => (
            <div key={idx} className="flex items-center gap-4 p-4 bg-white border border-slate-200 rounded-lg">
              <span className="w-6 h-6 rounded-full bg-slate-100 border border-slate-300 text-slate-600 flex items-center justify-center text-xs font-bold flex-shrink-0">
                {idx + 1}
              </span>
              <span className="text-sm font-medium text-slate-800 w-48 flex-shrink-0">{item.step}</span>
              <code className="text-xs font-mono text-slate-600 bg-slate-50 border border-slate-200 px-2 py-1 rounded">
                {item.cmd}
              </code>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

/* ─────────────────────────────────────────────────────── */
/*  7. INTEGRATIONS & CAPABILITIES                         */
/* ─────────────────────────────────────────────────────── */
const Capabilities: React.FC = () => {
  const items = [
    { label: 'Source Anchors', href: '/docs/anchors' },
    { label: 'Deterministic Metrics', href: '/docs/metrics' },
    { label: 'Baseline vs Candidate', href: '/docs/comparison' },
    { label: 'Query-Level Regression', href: '/docs/comparison' },
    { label: 'LangChain Adapter', href: '/docs/adapters' },
    { label: 'LlamaIndex Adapter', href: '/docs/adapters' },
    { label: 'Gold Set Import', href: '/docs/gold-sets' },
    { label: 'CLI & CI Integration', href: '/docs/cli' },
  ];

  return (
    <section className="py-16 border-b border-slate-200 bg-slate-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <h2 className="text-2xl font-bold text-slate-900 mb-2">Core capabilities</h2>
        <p className="text-sm text-slate-500 mb-6">Click any capability to read the documentation.</p>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {items.map((item) => (
            <Link
              key={item.label}
              to={item.href}
              className="px-4 py-3 bg-white border border-slate-200 rounded-lg text-sm text-slate-700 font-medium hover:border-sky-300 hover:text-sky-700 transition-colors text-center"
            >
              {item.label}
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
};

/* ─────────────────────────────────────────────────────── */
/*  8. FOOTER CTA                                          */
/* ─────────────────────────────────────────────────────── */
const FooterCTA: React.FC = () => (
  <section className="py-16">
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="flex flex-col sm:flex-row items-center justify-between gap-6 p-6 bg-white border border-slate-200 rounded-lg shadow-sm">
        <div>
          <h3 className="text-base font-semibold text-slate-900 mb-1">Open source, Apache-2.0</h3>
          <p className="text-sm text-slate-600">
            Inspect the code, file issues, or contribute on GitHub.
          </p>
        </div>
        <div className="flex flex-wrap gap-3">
          <a
            href="https://github.com/Mukeshram-07/spanchor"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-slate-900 hover:bg-slate-800 text-white font-medium rounded-md text-sm transition-colors"
          >
            <GitBranch className="w-4 h-4" /> GitHub
          </a>
          <a
            href="https://pypi.org/project/spanchor/"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-white border border-slate-300 hover:border-slate-400 text-slate-700 font-medium rounded-md text-sm transition-colors"
          >
            <Package className="w-4 h-4 text-sky-600" /> PyPI
          </a>
        </div>
      </div>
    </div>
  </section>
);

/* ─────────────────────────────────────────────────────── */
/*  PAGE                                                   */
/* ─────────────────────────────────────────────────────── */
const Home: React.FC = () => (
  <div className="w-full min-h-screen flex flex-col bg-white text-slate-900">
    <Navbar />
    <main className="flex-1 w-full">
      <Hero />
      <WhatItDoes />
      <TheProblem />
      <HowItWorks />
      <CodeExample />
      <DeveloperWorkflow />
      <Capabilities />
      <FooterCTA />
    </main>
    <Footer />
  </div>
);

export default Home;
