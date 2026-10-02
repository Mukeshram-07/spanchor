import React from 'react';
import { motion } from 'framer-motion';
import Navbar from '../components/layouts/Navbar';
import Footer from '../components/layouts/Footer';
import { useReducedMotion } from '../hooks/useReducedMotion';

const Architecture: React.FC = () => {
  const prefersReducedMotion = useReducedMotion();

  const itemVariants = {
    hidden: { opacity: 0, y: prefersReducedMotion ? 0 : 10 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: prefersReducedMotion ? 0 : 0.6 },
    },
  };

  return (
    <div className="min-h-screen bg-white flex flex-col font-sans text-slate-900">
      <Navbar />

      <main className="flex-1 py-16 px-4 sm:px-6 lg:px-8 max-w-6xl mx-auto w-full">
        {/* HERO SECTION — Compact, no duplication */}
        <motion.section
          variants={itemVariants}
          initial="hidden"
          animate="visible"
          className="mb-16"
        >
          <h1 className="text-5xl font-bold text-slate-900 mb-3">SPANCHOR Architecture</h1>
          <p className="text-lg text-slate-700 mb-6 max-w-3xl">
            Where source-anchored retrieval evaluation fits inside a RAG pipeline.
          </p>
          <p className="text-slate-600 mb-8 leading-relaxed max-w-3xl">
            SPANCHOR sits between retrieval output and evaluation decisions. It maps retrieved evidence back to canonical source spans, measures retrieval quality, and compares baseline and candidate runs for regression detection.
          </p>
        </motion.section>

        {/* MAIN SYSTEM ARCHITECTURE DIAGRAM */}
        <motion.section
          variants={itemVariants}
          initial="hidden"
          animate="visible"
          className="mb-20"
        >
          <div className="bg-gradient-to-br from-slate-50 to-slate-100 border border-slate-300 rounded-xl p-8 sm:p-12 overflow-x-auto">
            <div className="font-mono text-sm text-slate-700 min-w-max space-y-6">
              {/* Row 1: Source Documents */}
              <div className="flex items-center justify-center gap-4">
                <div className="px-6 py-3 bg-white border-2 border-slate-800 rounded font-bold text-slate-900 min-w-max">
                  SOURCE DOCUMENTS
                </div>
              </div>

              {/* Arrow */}
              <div className="flex justify-center">
                <div className="text-slate-600 text-2xl">↓</div>
              </div>

              {/* Row 2: Canonicalization */}
              <div className="flex items-center justify-center gap-4">
                <div className="px-6 py-3 bg-white border-2 border-slate-700 rounded font-bold text-slate-900 min-w-max">
                  CANONICALIZATION
                </div>
              </div>
              <div className="flex justify-center text-xs text-slate-600 px-4">
                <span className="text-center">normalize • hash • deterministic</span>
              </div>

              {/* Arrow */}
              <div className="flex justify-center">
                <div className="text-slate-600 text-2xl">↓</div>
              </div>

              {/* Row 3: Source Anchors & Gold Set */}
              <div className="flex items-center justify-center gap-4">
                <div className="px-6 py-3 bg-white border-2 border-slate-700 rounded font-bold text-slate-900 min-w-max">
                  SOURCE ANCHORS / GOLD SET
                </div>
              </div>
              <div className="flex justify-center text-xs text-slate-600 px-4">
                <span className="text-center">document_id + [start, end) + hash</span>
              </div>

              {/* Arrow */}
              <div className="flex justify-center">
                <div className="text-slate-600 text-2xl">↓</div>
              </div>

              {/* Row 4: RAG System */}
              <div className="flex items-center justify-center gap-4">
                <div className="px-8 py-4 bg-indigo-50 border-2 border-indigo-600 rounded font-bold text-indigo-900 min-w-max">
                  RAG RETRIEVAL SYSTEM
                </div>
              </div>
              <div className="flex justify-center text-xs text-slate-600 px-4 space-x-4">
                <span>Retriever</span>
                <span>•</span>
                <span>Vector Store</span>
                <span>•</span>
                <span>Embeddings</span>
              </div>

              {/* Arrow */}
              <div className="flex justify-center">
                <div className="text-slate-600 text-2xl">↓</div>
              </div>

              {/* Row 5: Retrieved Results */}
              <div className="flex items-center justify-center gap-4">
                <div className="px-6 py-3 bg-white border-2 border-slate-700 rounded font-bold text-slate-900 min-w-max">
                  RETRIEVED RESULTS
                </div>
              </div>
              <div className="flex justify-center text-xs text-slate-600 px-4">
                <span className="text-center">query / document / span / text</span>
              </div>

              {/* Arrow */}
              <div className="flex justify-center">
                <div className="text-slate-600 text-2xl">↓</div>
              </div>

              {/* Row 6: SPANCHOR (BOLD BOUNDARY) */}
              <div className="flex items-center justify-center gap-4">
                <div className="px-8 py-6 bg-sky-600 text-white rounded-lg font-bold text-lg min-w-max border-4 border-sky-800 shadow-lg">
                  ╔════════════════════════════════════════════╗<br />
                  ║            SPANCHOR ENGINE                 ║<br />
                  ║  • Anchor Resolution                       ║<br />
                  ║  • Evidence Matching (IoU)                 ║<br />
                  ║  • Retrieval Evaluation                    ║<br />
                  ║  • Metrics (Recall, Precision, Hit, IoU)   ║<br />
                  ║  • Baseline vs Candidate Comparison        ║<br />
                  ║  • Regression Detection                    ║<br />
                  ╚════════════════════════════════════════════╝
                </div>
              </div>

              {/* Arrow */}
              <div className="flex justify-center">
                <div className="text-slate-600 text-2xl">↓</div>
              </div>

              {/* Row 7: CI / Decision */}
              <div className="flex items-center justify-center gap-4">
                <div className="px-6 py-3 bg-white border-2 border-slate-700 rounded font-bold text-slate-900 min-w-max">
                  CI / DECISION
                </div>
              </div>
              <div className="flex justify-center text-xs text-slate-600 px-4">
                <span className="text-center">pass • investigate • fail</span>
              </div>
            </div>
          </div>
        </motion.section>

        {/* 3. WHERE SPANCHOR SITS */}
        <motion.section
          variants={itemVariants}
          initial="hidden"
          animate="visible"
          className="mb-20 border-l-4 border-sky-600 pl-6"
        >
          <h2 className="text-3xl font-bold text-slate-900 mb-4">Where SPANCHOR Sits</h2>
          <p className="text-slate-600 mb-8">
            The application and retriever remain responsible for retrieving evidence. SPANCHOR evaluates whether that evidence still corresponds to the source-anchored expectations.
          </p>
          <div className="bg-slate-50 border border-slate-200 rounded-lg p-8 font-mono text-sm space-y-4">
            <div className="text-slate-700">USER QUERY</div>
            <div className="text-center text-slate-400">↓</div>
            <div className="text-slate-700">RAG RETRIEVER</div>
            <div className="text-center text-slate-400">↓</div>
            <div className="text-slate-700">RETRIEVED EVIDENCE</div>
            <div className="border-t-2 border-b-2 border-sky-600 py-4 my-4 text-center font-bold text-sky-700">
              ━━━━━━━━━━━━━ SPANCHOR ━━━━━━━━━━━━━
            </div>
            <div className="text-center text-slate-400">↓</div>
            <div className="text-slate-700">METRICS</div>
            <div className="text-center text-slate-400">↓</div>
            <div className="text-slate-700">REGRESSION DECISION</div>
          </div>
        </motion.section>

        {/* 4. SOURCE-ANCHORED EVIDENCE MODEL */}
        <motion.section
          variants={itemVariants}
          initial="hidden"
          animate="visible"
          className="mb-20"
        >
          <h2 className="text-3xl font-bold text-slate-900 mb-4">Source-Anchored Evidence Model</h2>
          <p className="text-slate-600 mb-8">
            An anchor identifies expected evidence using the source document identity plus a span. The relationship between document, canonical text, source span, and anchor:
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
            {/* Left: Visual representation */}
            <div className="bg-slate-50 border border-slate-200 rounded-lg p-6 font-mono text-xs space-y-2">
              <div className="text-slate-700 font-bold">Document Structure</div>
              <div className="text-slate-600 mt-4">
                <div>Document</div>
                <div className="ml-4">├── document_id: str</div>
                <div className="ml-4">├── canonical_text: str</div>
                <div className="ml-4">├── sha256: str</div>
                <div className="ml-4">└── Anchor</div>
                <div className="ml-8">├── document_id: str</div>
                <div className="ml-8">├── start: int</div>
                <div className="ml-8">├── end: int</div>
                <div className="ml-8">└── expected_text_hash: str</div>
              </div>
            </div>

            {/* Right: Explanation */}
            <div className="flex flex-col justify-center">
              <div className="space-y-4">
                <div>
                  <h4 className="font-bold text-slate-900 mb-2">document_id</h4>
                  <p className="text-slate-600 text-sm">Unique identifier for the source document (e.g., "docs/deployment.md")</p>
                </div>
                <div>
                  <h4 className="font-bold text-slate-900 mb-2">[start, end)</h4>
                  <p className="text-slate-600 text-sm">Half-open character interval in the canonical text. Stable even if chunking changes.</p>
                </div>
                <div>
                  <h4 className="font-bold text-slate-900 mb-2">expected_text_hash</h4>
                  <p className="text-slate-600 text-sm">SHA-256 hash of the expected text span. Verification mechanism.</p>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-sm text-slate-700">
            <strong className="text-blue-900">Important:</strong> An offset alone is not a stable identity. SPANCHOR anchors combine document_id + [start, end) + hash for deterministic identity.
          </div>
        </motion.section>

        {/* 5. CANONICALIZATION */}
        <motion.section
          variants={itemVariants}
          initial="hidden"
          animate="visible"
          className="mb-20"
        >
          <h2 className="text-3xl font-bold text-slate-900 mb-4">Canonicalization</h2>
          <p className="text-slate-600 mb-8">
            The same source must produce a deterministic representation before span offsets and hashes are used for evaluation. Canonicalization is the foundation for reproducible anchors.
          </p>

          <div className="bg-slate-50 border border-slate-200 rounded-lg p-8 font-mono text-sm space-y-6">
            <div className="text-slate-700 font-bold">Raw Source</div>
            <div className="text-center text-slate-400">↓</div>
            <div className="text-slate-700 font-bold">Unicode Normalization (NFC)</div>
            <div className="text-center text-slate-400">↓</div>
            <div className="text-slate-700 font-bold">Line-Ending Normalization (CRLF → LF)</div>
            <div className="text-center text-slate-400">↓</div>
            <div className="text-slate-700 font-bold">Canonical Text</div>
            <div className="text-center text-slate-400">↓</div>
            <div className="text-slate-700 font-bold">SHA-256 Identity</div>
          </div>

          <p className="text-slate-600 mt-6 text-sm">
            <strong>Why it matters:</strong> Different systems may represent the same text differently (Unicode normalization forms, line endings, whitespace). Canonicalization ensures that SPANCHOR always measures offsets against the same normalized representation.
          </p>
        </motion.section>

        {/* 6. EVALUATION FLOW */}
        <motion.section
          variants={itemVariants}
          initial="hidden"
          animate="visible"
          className="mb-20"
        >
          <h2 className="text-3xl font-bold text-slate-900 mb-4">Evaluation Flow</h2>
          <p className="text-slate-600 mb-8">
            From gold queries to aggregate metrics, SPANCHOR computes per-query evidence overlap and then aggregates to system-level metrics.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
            {/* Left: Flow diagram */}
            <div className="bg-slate-50 border border-slate-200 rounded-lg p-8 font-mono text-xs space-y-3">
              <div className="text-slate-700 font-bold">Gold Queries</div>
              <div className="text-center text-slate-400">↓</div>
              <div className="text-slate-700">Expected Anchors</div>
              <div className="text-center text-slate-400">↓</div>
              <div className="text-slate-700">Retrieval Results</div>
              <div className="text-center text-slate-400">↓</div>
              <div className="text-slate-700 font-bold">Anchor Resolution</div>
              <div className="text-center text-slate-400">↓</div>
              <div className="text-slate-700">Evidence Overlap (IoU)</div>
              <div className="text-center text-slate-400">↓</div>
              <div className="text-slate-700 font-bold">Per-Query Metrics</div>
              <div className="text-center text-slate-400">↓</div>
              <div className="text-slate-700 font-bold text-sky-700">Aggregate Metrics</div>
            </div>

            {/* Right: Metrics definition */}
            <div className="flex flex-col justify-center">
              <div className="space-y-3">
                <h4 className="font-bold text-slate-900 text-lg mb-4">Verified SPANCHOR Metrics</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex gap-3">
                    <span className="font-mono font-bold text-sky-700 flex-shrink-0 w-32">Recall@K</span>
                    <span className="text-slate-600">Fraction of gold anchors retrieved in top K</span>
                  </div>
                  <div className="flex gap-3">
                    <span className="font-mono font-bold text-sky-700 flex-shrink-0 w-32">Precision@K</span>
                    <span className="text-slate-600">Fraction of retrieved results matching gold</span>
                  </div>
                  <div className="flex gap-3">
                    <span className="font-mono font-bold text-sky-700 flex-shrink-0 w-32">Hit@K</span>
                    <span className="text-slate-600">Binary: at least one gold anchor in top K</span>
                  </div>
                  <div className="flex gap-3">
                    <span className="font-mono font-bold text-sky-700 flex-shrink-0 w-32">IoU</span>
                    <span className="text-slate-600">Character overlap between retrieved and gold spans</span>
                  </div>
                  <div className="flex gap-3">
                    <span className="font-mono font-bold text-sky-700 flex-shrink-0 w-32">FullEvidence@K</span>
                    <span className="text-slate-600">All gold anchors retrieved with 100% IoU in top K</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </motion.section>

        {/* 7. BASELINE → CANDIDATE COMPARISON */}
        <motion.section
          variants={itemVariants}
          initial="hidden"
          animate="visible"
          className="mb-20"
        >
          <h2 className="text-3xl font-bold text-slate-900 mb-4">Baseline → Candidate Comparison</h2>
          <p className="text-slate-600 mb-8">
            SPANCHOR compares two runs and classifies per-query deltas to detect regressions.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            {/* Baseline */}
            <div className="bg-slate-50 border border-slate-200 rounded-lg p-6">
              <h4 className="font-bold text-slate-900 mb-4 text-center">BASELINE RUN</h4>
              <div className="font-mono text-xs text-slate-600 space-y-2 mb-4">
                <div>Recall@5: 0.405</div>
                <div>Precision@5: 0.020</div>
                <div>Hit@5: 0.410</div>
              </div>
              <div className="text-center text-slate-400">↓</div>
            </div>

            {/* Comparison */}
            <div className="bg-sky-50 border-2 border-sky-600 rounded-lg p-6">
              <h4 className="font-bold text-sky-900 mb-4 text-center">compare()</h4>
              <div className="font-mono text-xs text-sky-700 space-y-2 text-center">
                <div>per-query deltas</div>
                <div>policy thresholds</div>
                <div>classification</div>
              </div>
            </div>

            {/* Candidate */}
            <div className="bg-slate-50 border border-slate-200 rounded-lg p-6">
              <h4 className="font-bold text-slate-900 mb-4 text-center">CANDIDATE RUN</h4>
              <div className="font-mono text-xs text-slate-600 space-y-2 mb-4">
                <div>Recall@5: 0.249</div>
                <div>Precision@5: 0.017</div>
                <div>Hit@5: 0.260</div>
              </div>
              <div className="text-center text-slate-400">↑</div>
            </div>
          </div>

          <div className="bg-slate-50 border border-slate-200 rounded-lg p-8">
            <h4 className="font-bold text-slate-900 mb-6 text-center">Result: Per-Query Classification</h4>
            <div className="grid grid-cols-3 gap-4 font-mono text-sm">
              <div className="text-center p-4 bg-white border border-slate-200 rounded">
                <div className="font-bold text-slate-900 mb-2">IMPROVED</div>
                <div className="text-slate-600 text-xs">Candidate better than baseline</div>
                <div className="text-xl font-bold text-emerald-600 mt-2">6</div>
              </div>
              <div className="text-center p-4 bg-white border border-slate-200 rounded">
                <div className="font-bold text-slate-900 mb-2">UNCHANGED</div>
                <div className="text-slate-600 text-xs">Within policy threshold</div>
                <div className="text-xl font-bold text-slate-600 mt-2">75</div>
              </div>
              <div className="text-center p-4 bg-white border border-slate-200 rounded">
                <div className="font-bold text-slate-900 mb-2">REGRESSED</div>
                <div className="text-slate-600 text-xs">Candidate worse than baseline</div>
                <div className="text-xl font-bold text-red-600 mt-2">19</div>
              </div>
            </div>
          </div>
        </motion.section>

        {/* 8. REGRESSION GATE */}
        <motion.section
          variants={itemVariants}
          initial="hidden"
          animate="visible"
          className="mb-20 border-l-4 border-red-600 pl-6"
        >
          <h2 className="text-3xl font-bold text-slate-900 mb-4">Regression Gate</h2>
          <p className="text-slate-600 mb-8">
            SPANCHOR provides comparison results and the surrounding CI workflow uses those results. The regression gate is a policy threshold applied during compare().
          </p>

          <div className="bg-slate-900 text-slate-100 rounded-lg p-6 font-mono text-sm mb-8 overflow-x-auto">
            <code className="text-slate-300">
              compare(baseline, candidate, policy={`{"recall@5": 0.05}`})
            </code>
          </div>

          <div className="bg-slate-50 border border-slate-200 rounded-lg p-8 font-mono text-sm space-y-6">
            <div className="text-slate-700 font-bold">Candidate Retrieval Changes</div>
            <div className="text-center text-slate-400">↓</div>
            <div className="text-slate-700">Metric Delta Calculation</div>
            <div className="text-center text-slate-400">↓</div>
            <div className="text-slate-700 font-bold">Policy Threshold Check</div>
            <div className="text-center text-slate-400">↓</div>
            <div className="text-slate-700 font-bold">Regression Classification</div>
            <div className="text-center text-slate-400">↓</div>
            <div className="text-slate-700">CI / Engineering Decision</div>
          </div>

          <p className="text-slate-600 mt-6 text-sm">
            <strong>Key distinction:</strong> SPANCHOR computes the comparison result. Your CI workflow decides how to act on that result (pass, investigate, fail).
          </p>
        </motion.section>

        {/* 9. DATA FLOW / OBJECT MODEL */}
        <motion.section
          variants={itemVariants}
          initial="hidden"
          animate="visible"
          className="mb-20"
        >
          <h2 className="text-3xl font-bold text-slate-900 mb-4">Data Flow & Object Model</h2>
          <p className="text-slate-600 mb-8">
            The relationship between core SPANCHOR objects as they flow through evaluation:
          </p>

          <div className="bg-slate-50 border border-slate-200 rounded-lg p-8 font-mono text-sm space-y-6">
            <div className="text-slate-700 font-bold">Document</div>
            <div className="text-center text-slate-400">↓</div>
            <div className="text-slate-700">Anchor</div>
            <div className="text-center text-slate-400">↓</div>
            <div className="text-slate-700">Query</div>
            <div className="text-center text-slate-400">↓</div>
            <div className="text-slate-700">RetrievalResult</div>
            <div className="text-center text-slate-400">↓</div>
            <div className="text-slate-700 font-bold">evaluate()</div>
            <div className="text-center text-slate-400">↓</div>
            <div className="text-slate-700 font-bold">Run</div>
            <div className="text-center text-slate-400">↓</div>
            <div className="text-slate-700 font-bold">compare()</div>
            <div className="text-center text-slate-400">↓</div>
            <div className="text-slate-700 font-bold text-sky-700">ComparisonResult</div>
          </div>

          <p className="text-slate-600 mt-8 text-sm">
            <strong>Terminology:</strong> These are the actual SPANCHOR public classes. Do not confuse with conceptual terms like "gold set" (which refers to expected anchors) or "retrieval result" (concept; the type is RetrievalResult).
          </p>
        </motion.section>

        {/* 10. WHAT SPANCHOR DOES / DOES NOT DO */}
        <motion.section
          variants={itemVariants}
          initial="hidden"
          animate="visible"
          className="mb-20"
        >
          <h2 className="text-3xl font-bold text-slate-900 mb-4">Capabilities & Boundaries</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Does */}
            <div>
              <h3 className="font-bold text-slate-900 mb-4 text-lg">SPANCHOR Does</h3>
              <ul className="space-y-3 text-slate-600">
                <li className="flex gap-3">
                  <span className="text-emerald-600 font-bold">✓</span>
                  <span>Source-anchored retrieval evaluation</span>
                </li>
                <li className="flex gap-3">
                  <span className="text-emerald-600 font-bold">✓</span>
                  <span>Anchor resolution & verification</span>
                </li>
                <li className="flex gap-3">
                  <span className="text-emerald-600 font-bold">✓</span>
                  <span>Retrieval metrics (Recall, Precision, Hit, IoU)</span>
                </li>
                <li className="flex gap-3">
                  <span className="text-emerald-600 font-bold">✓</span>
                  <span>Baseline/candidate comparison</span>
                </li>
                <li className="flex gap-3">
                  <span className="text-emerald-600 font-bold">✓</span>
                  <span>Regression classification</span>
                </li>
                <li className="flex gap-3">
                  <span className="text-emerald-600 font-bold">✓</span>
                  <span>Deterministic local evaluation</span>
                </li>
              </ul>
            </div>

            {/* Does Not */}
            <div>
              <h3 className="font-bold text-slate-900 mb-4 text-lg">SPANCHOR Does NOT</h3>
              <ul className="space-y-3 text-slate-600">
                <li className="flex gap-3">
                  <span className="text-red-600 font-bold">✗</span>
                  <span>Generate embeddings</span>
                </li>
                <li className="flex gap-3">
                  <span className="text-red-600 font-bold">✗</span>
                  <span>Provide vector databases</span>
                </li>
                <li className="flex gap-3">
                  <span className="text-red-600 font-bold">✗</span>
                  <span>Parse documents or PDFs</span>
                </li>
                <li className="flex gap-3">
                  <span className="text-red-600 font-bold">✗</span>
                  <span>Generate LLM answers</span>
                </li>
                <li className="flex gap-3">
                  <span className="text-red-600 font-bold">✗</span>
                  <span>Host RAG applications</span>
                </li>
                <li className="flex gap-3">
                  <span className="text-red-600 font-bold">✗</span>
                  <span>Replace retrievers or provide a REST backend</span>
                </li>
              </ul>
            </div>
          </div>
        </motion.section>

        {/* 11. ARCHITECTURE PRINCIPLES */}
        <motion.section
          variants={itemVariants}
          initial="hidden"
          animate="visible"
          className="mb-20"
        >
          <h2 className="text-3xl font-bold text-slate-900 mb-4">Architecture Principles</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[
              { title: 'Deterministic', desc: 'Same input always produces same output' },
              { title: 'Local-First', desc: 'Runs locally without external dependencies' },
              { title: 'Source-Anchored', desc: 'Evidence identity tied to source documents' },
              { title: 'Reproducible', desc: 'Results are verifiable and repeatable' },
              { title: 'Schema-Aware', desc: 'Explicit data contracts and types' },
              { title: 'Explicit Limits', desc: 'Clear about what it can and cannot do' },
            ].map((principle, idx) => (
              <div key={idx} className="bg-slate-50 border border-slate-200 rounded-lg p-4">
                <h4 className="font-bold text-slate-900 mb-2">{principle.title}</h4>
                <p className="text-slate-600 text-sm">{principle.desc}</p>
              </div>
            ))}
          </div>
        </motion.section>

        {/* 12. NEXT STEPS */}
        <motion.section
          variants={itemVariants}
          initial="hidden"
          animate="visible"
          className="mb-12 py-12 border-t border-slate-200"
        >
          <h2 className="text-3xl font-bold text-slate-900 mb-6">Next Steps</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <a
              href="/docs/quickstart"
              className="block p-6 rounded-lg border border-slate-200 hover:border-sky-400 hover:shadow-md transition-all"
            >
              <h3 className="font-semibold text-slate-900 mb-2">→ Quickstart</h3>
              <p className="text-sm text-slate-600">Get up and running with SPANCHOR in minutes.</p>
            </a>
            <a
              href="/examples"
              className="block p-6 rounded-lg border border-slate-200 hover:border-sky-400 hover:shadow-md transition-all"
            >
              <h3 className="font-semibold text-slate-900 mb-2">→ Examples</h3>
              <p className="text-sm text-slate-600">Learn from real-world use cases and workflows.</p>
            </a>
            <a
              href="/api"
              className="block p-6 rounded-lg border border-slate-200 hover:border-sky-400 hover:shadow-md transition-all"
            >
              <h3 className="font-semibold text-slate-900 mb-2">→ API Reference</h3>
              <p className="text-sm text-slate-600">Complete documentation of classes and functions.</p>
            </a>
          </div>
        </motion.section>
      </main>

      <Footer />
    </div>
  );
};

export default Architecture;
