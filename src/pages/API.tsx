import React from 'react';
import Navbar from '../components/layouts/Navbar';
import Footer from '../components/layouts/Footer';
import CodeEditor from '../components/features/CodeEditor';

const API: React.FC = () => {
  return (
    <div className="min-h-screen bg-white flex flex-col">
      <Navbar />

      <main className="flex-1 py-16 px-4 sm:px-6 lg:px-8 max-w-5xl mx-auto w-full">
        {/* HERO SECTION */}
        <section className="mb-20">
          <h1 className="text-5xl font-bold text-slate-900 mb-4">API Reference</h1>
          <p className="text-xl text-slate-700 mb-6 leading-relaxed max-w-3xl">
            Complete Python interfaces and CLI tools for SPANCHOR. Define source-anchored evaluations, measure retrieval quality with verified metrics, and detect regressions in CI/CD pipelines.
          </p>
          <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 font-mono text-xs text-slate-700">
            <div className="text-slate-500 mb-2">import spanchor</div>
            <div className="text-slate-600">
              <div>Document, Anchor, Query, RetrievalResult, Run, ComparisonResult</div>
              <div className="mt-1">evaluate(), compare(), check_corpus()</div>
              <div className="mt-1">SpanchorError, AnchorResolutionError, ... (10 exceptions)</div>
            </div>
          </div>
        </section>

        {/* TABLE OF CONTENTS */}
        <section className="mb-20 py-8 border-t border-b border-slate-200">
          <h2 className="text-xs font-mono font-semibold text-slate-500 uppercase tracking-widest mb-6">On This Page</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-3">
            <a href="#core-objects" className="group flex items-start gap-2 text-slate-700 hover:text-sky-600 transition-colors">
              <span className="text-slate-400 group-hover:text-sky-400 mt-0.5">›</span>
              <span className="font-medium">01 Core Objects</span>
            </a>
            <a href="#evaluation" className="group flex items-start gap-2 text-slate-700 hover:text-sky-600 transition-colors">
              <span className="text-slate-400 group-hover:text-sky-400 mt-0.5">›</span>
              <span className="font-medium">02 Evaluation</span>
            </a>
            <a href="#metrics" className="group flex items-start gap-2 text-slate-700 hover:text-sky-600 transition-colors">
              <span className="text-slate-400 group-hover:text-sky-400 mt-0.5">›</span>
              <span className="font-medium">03 Metrics</span>
            </a>
            <a href="#comparison" className="group flex items-start gap-2 text-slate-700 hover:text-sky-600 transition-colors">
              <span className="text-slate-400 group-hover:text-sky-400 mt-0.5">›</span>
              <span className="font-medium">04 Comparison</span>
            </a>
            <a href="#regression" className="group flex items-start gap-2 text-slate-700 hover:text-sky-600 transition-colors">
              <span className="text-slate-400 group-hover:text-sky-400 mt-0.5">›</span>
              <span className="font-medium">05 Regression / CI</span>
            </a>
            <a href="#cli" className="group flex items-start gap-2 text-slate-700 hover:text-sky-600 transition-colors">
              <span className="text-slate-400 group-hover:text-sky-400 mt-0.5">›</span>
              <span className="font-medium">06 CLI Reference</span>
            </a>
            <a href="#exceptions" className="group flex items-start gap-2 text-slate-700 hover:text-sky-600 transition-colors">
              <span className="text-slate-400 group-hover:text-sky-400 mt-0.5">›</span>
              <span className="font-medium">07 Exceptions</span>
            </a>
            <a href="#types" className="group flex items-start gap-2 text-slate-700 hover:text-sky-600 transition-colors">
              <span className="text-slate-400 group-hover:text-sky-400 mt-0.5">›</span>
              <span className="font-medium">08 Type Reference</span>
            </a>
          </div>
        </section>

        {/* CORE OBJECTS */}
        <section id="core-objects" className="mb-24 scroll-mt-20">
          <div className="mb-16">
            <h2 className="text-4xl font-bold text-slate-900 mb-2">01 Core Objects</h2>
            <p className="text-slate-600">Six frozen dataclasses represent the complete SPANCHOR evaluation workflow.</p>
          </div>

          {/* Document */}
          <div className="mb-16 pb-16 border-b border-slate-200">
            <div className="flex items-baseline gap-4 mb-4">
              <h3 className="text-2xl font-mono font-bold text-slate-900">Document</h3>
              <span className="text-xs font-mono bg-slate-100 text-slate-600 px-2 py-1 rounded">class</span>
            </div>
            <p className="text-slate-700 mb-6 text-sm">Canonical source document with SHA256 hash. Text is normalized to NFC and line endings standardized for reproducible evaluation.</p>
            
            <div className="mb-8">
              <h4 className="text-xs font-mono font-semibold text-slate-500 uppercase tracking-widest mb-4">Signature</h4>
              <div className="bg-slate-50 border border-slate-200 rounded p-4 font-mono text-sm text-slate-900 overflow-x-auto">
                Document(document_id: str, text: str, sha256: str, schema_version: str = "0.1.0")
              </div>
            </div>

            <div className="mb-8">
              <h4 className="text-xs font-mono font-semibold text-slate-500 uppercase tracking-widest mb-4">Fields</h4>
              <div className="space-y-3 text-sm">
                <div className="flex flex-col sm:flex-row sm:gap-4">
                  <span className="font-mono font-bold text-sky-700 flex-shrink-0 sm:w-36">document_id</span>
                  <div className="flex-grow">
                    <div className="font-mono text-slate-600">str</div>
                    <div className="text-slate-700 mt-1">Unique document identifier (e.g., "docs/deployment.md")</div>
                  </div>
                </div>
                <div className="flex flex-col sm:flex-row sm:gap-4">
                  <span className="font-mono font-bold text-sky-700 flex-shrink-0 sm:w-36">text</span>
                  <div className="flex-grow">
                    <div className="font-mono text-slate-600">str</div>
                    <div className="text-slate-700 mt-1">Canonicalized text content (NFC normalized, Unix line endings)</div>
                  </div>
                </div>
                <div className="flex flex-col sm:flex-row sm:gap-4">
                  <span className="font-mono font-bold text-sky-700 flex-shrink-0 sm:w-36">sha256</span>
                  <div className="flex-grow">
                    <div className="font-mono text-slate-600">str</div>
                    <div className="text-slate-700 mt-1">SHA256 hash of canonical text (hex string)</div>
                  </div>
                </div>
                <div className="flex flex-col sm:flex-row sm:gap-4">
                  <span className="font-mono font-bold text-sky-700 flex-shrink-0 sm:w-36">schema_version</span>
                  <div className="flex-grow">
                    <div className="font-mono text-slate-600">str = "0.1.0"</div>
                    <div className="text-slate-700 mt-1">Schema version (frozen at 0.1.0 for compatibility)</div>
                  </div>
                </div>
              </div>
            </div>

            <div className="mb-8">
              <h4 className="text-xs font-mono font-semibold text-slate-500 uppercase tracking-widest mb-4">Class Methods</h4>
              <div className="bg-slate-50 border border-slate-200 rounded p-4 font-mono text-sm text-slate-900 overflow-x-auto">
                @classmethod<br/>
                from_text(document_id: str, raw_text: str) → Document
              </div>
              <p className="text-slate-700 text-sm mt-2">Create Document from raw text with automatic canonicalization and SHA256 hashing.</p>
            </div>

            <div className="mb-4">
              <h4 className="text-xs font-mono font-semibold text-slate-500 uppercase tracking-widest mb-4">Example</h4>
              <CodeEditor
                code={`from spanchor import Document

# From raw text (auto-canonicalize & hash)
doc = Document.from_text(
    "docs/deployment.md",
    "Database connection strings must use sslmode=verify-full..."
)

# Or construct directly
doc2 = Document(
    document_id="docs/auth.md",
    text="OAuth2 implementation requires...",
    sha256="a1b2c3d4e5f6...",
    schema_version="0.1.0"
)`}
                language="python"
                filename="document.py"
                showLineNumbers={false}
                showCopyButton={true}
                showResetButton={false}
              />
            </div>
          </div>

          {/* Anchor */}
          <div className="mb-16 pb-16 border-b border-slate-200">
            <div className="flex items-baseline gap-4 mb-4">
              <h3 className="text-2xl font-mono font-bold text-slate-900">Anchor</h3>
              <span className="text-xs font-mono bg-slate-100 text-slate-600 px-2 py-1 rounded">class</span>
            </div>
            <p className="text-slate-700 mb-6 text-sm">Character span [start, end) within a Document defining ground-truth evidence for a Query.</p>
            
            <div className="mb-8">
              <h4 className="text-xs font-mono font-semibold text-slate-500 uppercase tracking-widest mb-4">Signature</h4>
              <div className="bg-slate-50 border border-slate-200 rounded p-4 font-mono text-sm text-slate-900 overflow-x-auto">
                Anchor(document_id: str, start: int, end: int, expected_text_hash: str, schema_version: str = "0.1.0")
              </div>
            </div>

            <div className="mb-8">
              <h4 className="text-xs font-mono font-semibold text-slate-500 uppercase tracking-widest mb-4">Fields</h4>
              <div className="space-y-3 text-sm">
                <div className="flex flex-col sm:flex-row sm:gap-4">
                  <span className="font-mono font-bold text-sky-700 flex-shrink-0 sm:w-36">document_id</span>
                  <div className="flex-grow">
                    <div className="font-mono text-slate-600">str</div>
                    <div className="text-slate-700 mt-1">Parent document ID</div>
                  </div>
                </div>
                <div className="flex flex-col sm:flex-row sm:gap-4">
                  <span className="font-mono font-bold text-sky-700 flex-shrink-0 sm:w-36">start</span>
                  <div className="flex-grow">
                    <div className="font-mono text-slate-600">int</div>
                    <div className="text-slate-700 mt-1">Start offset (0-indexed, inclusive)</div>
                  </div>
                </div>
                <div className="flex flex-col sm:flex-row sm:gap-4">
                  <span className="font-mono font-bold text-sky-700 flex-shrink-0 sm:w-36">end</span>
                  <div className="flex-grow">
                    <div className="font-mono text-slate-600">int</div>
                    <div className="text-slate-700 mt-1">End offset (exclusive, [start, end) half-open interval)</div>
                  </div>
                </div>
                <div className="flex flex-col sm:flex-row sm:gap-4">
                  <span className="font-mono font-bold text-sky-700 flex-shrink-0 sm:w-36">expected_text_hash</span>
                  <div className="flex-grow">
                    <div className="font-mono text-slate-600">str</div>
                    <div className="text-slate-700 mt-1">SHA256 hash of text at [start, end)</div>
                  </div>
                </div>
                <div className="flex flex-col sm:flex-row sm:gap-4">
                  <span className="font-mono font-bold text-sky-700 flex-shrink-0 sm:w-36">schema_version</span>
                  <div className="flex-grow">
                    <div className="font-mono text-slate-600">str = "0.1.0"</div>
                    <div className="text-slate-700 mt-1">Schema version</div>
                  </div>
                </div>
              </div>
            </div>

            <div className="mb-8">
              <h4 className="text-xs font-mono font-semibold text-slate-500 uppercase tracking-widest mb-4">Methods</h4>
              <div className="bg-slate-50 border border-slate-200 rounded p-4 font-mono text-sm text-slate-900 overflow-x-auto">
                validate(document: Document) → None
              </div>
              <p className="text-slate-700 text-sm mt-2">Validate anchor against canonical document. Raises <span className="font-mono">AnchorResolutionError</span> if hash mismatch or out of bounds.</p>
            </div>

            <div className="mb-4">
              <h4 className="text-xs font-mono font-semibold text-slate-500 uppercase tracking-widest mb-4">Example</h4>
              <CodeEditor
                code={`from spanchor import Anchor

anchor = Anchor(
    document_id="docs/deployment.md",
    start=142,
    end=288,
    expected_text_hash="a1b2c3d4e5f6..."
)

# Validate against canonical document
doc = Document.from_text("docs/deployment.md", raw_text)
anchor.validate(doc)  # Raises AnchorResolutionError if invalid`}
                language="python"
                filename="anchor.py"
                showLineNumbers={false}
                showCopyButton={true}
                showResetButton={false}
              />
            </div>
          </div>

          {/* Query */}
          <div className="mb-16 pb-16 border-b border-slate-200">
            <div className="flex items-baseline gap-4 mb-4">
              <h3 className="text-2xl font-mono font-bold text-slate-900">Query</h3>
              <span className="text-xs font-mono bg-slate-100 text-slate-600 px-2 py-1 rounded">class</span>
            </div>
            <p className="text-slate-700 mb-6 text-sm">Question + ground-truth Anchors tuple. The unit of evaluation in SPANCHOR.</p>
            
            <div className="mb-8">
              <h4 className="text-xs font-mono font-semibold text-slate-500 uppercase tracking-widest mb-4">Signature</h4>
              <div className="bg-slate-50 border border-slate-200 rounded p-4 font-mono text-sm text-slate-900 overflow-x-auto">
                Query(query_id: str, question: str, anchors: tuple[Anchor, ...], schema_version: str = "0.1.0")
              </div>
            </div>

            <div className="mb-8">
              <h4 className="text-xs font-mono font-semibold text-slate-500 uppercase tracking-widest mb-4">Fields</h4>
              <div className="space-y-3 text-sm">
                <div className="flex flex-col sm:flex-row sm:gap-4">
                  <span className="font-mono font-bold text-sky-700 flex-shrink-0 sm:w-36">query_id</span>
                  <div className="flex-grow">
                    <div className="font-mono text-slate-600">str</div>
                    <div className="text-slate-700 mt-1">Unique query identifier (e.g., "q1", "question-42")</div>
                  </div>
                </div>
                <div className="flex flex-col sm:flex-row sm:gap-4">
                  <span className="font-mono font-bold text-sky-700 flex-shrink-0 sm:w-36">question</span>
                  <div className="flex-grow">
                    <div className="font-mono text-slate-600">str</div>
                    <div className="text-slate-700 mt-1">Question text to be evaluated against retrieval results</div>
                  </div>
                </div>
                <div className="flex flex-col sm:flex-row sm:gap-4">
                  <span className="font-mono font-bold text-sky-700 flex-shrink-0 sm:w-36">anchors</span>
                  <div className="flex-grow">
                    <div className="font-mono text-slate-600">tuple[Anchor, ...]</div>
                    <div className="text-slate-700 mt-1">Immutable tuple of ground-truth evidence</div>
                  </div>
                </div>
                <div className="flex flex-col sm:flex-row sm:gap-4">
                  <span className="font-mono font-bold text-sky-700 flex-shrink-0 sm:w-36">schema_version</span>
                  <div className="flex-grow">
                    <div className="font-mono text-slate-600">str = "0.1.0"</div>
                    <div className="text-slate-700 mt-1">Schema version</div>
                  </div>
                </div>
              </div>
            </div>

            <div className="mb-4">
              <h4 className="text-xs font-mono font-semibold text-slate-500 uppercase tracking-widest mb-4">Example</h4>
              <CodeEditor
                code={`from spanchor import Query, Anchor

anchor1 = Anchor(
    document_id="docs/deployment.md",
    start=142,
    end=288,
    expected_text_hash="a1b2c3d4..."
)

query = Query(
    query_id="q1",
    question="How do I set up database SSL connections?",
    anchors=(anchor1,)  # Single anchor, can be multiple
)`}
                language="python"
                filename="query.py"
                showLineNumbers={false}
                showCopyButton={true}
                showResetButton={false}
              />
            </div>
          </div>

          {/* RetrievalResult */}
          <div className="mb-16 pb-16 border-b border-slate-200">
            <div className="flex items-baseline gap-4 mb-4">
              <h3 className="text-2xl font-mono font-bold text-slate-900">RetrievalResult</h3>
              <span className="text-xs font-mono bg-slate-100 text-slate-600 px-2 py-1 rounded">class</span>
            </div>
            <p className="text-slate-700 mb-6 text-sm">Retrieval output (span form or chunk-text form). Supports both pre-mapped spans and raw text requiring span mapping.</p>
            
            <div className="mb-8">
              <h4 className="text-xs font-mono font-semibold text-slate-500 uppercase tracking-widest mb-4">Signature</h4>
              <div className="bg-slate-50 border border-slate-200 rounded p-4 font-mono text-sm text-slate-900 overflow-x-auto">
                <div>RetrievalResult(</div>
                <div className="ml-4">rank: int, score: float,</div>
                <div className="ml-4">document_id: str | None = None,</div>
                <div className="ml-4">start: int | None = None, end: int | None = None,</div>
                <div className="ml-4">text: str | None = None,</div>
                <div className="ml-4">span_type: str = "text", metadata: dict = {}, schema_version: str = "0.1.0"</div>
                <div>)</div>
              </div>
            </div>

            <div className="mb-8">
              <h4 className="text-xs font-mono font-semibold text-slate-500 uppercase tracking-widest mb-4">Fields</h4>
              <div className="space-y-3 text-sm">
                <div className="flex flex-col sm:flex-row sm:gap-4">
                  <span className="font-mono font-bold text-sky-700 flex-shrink-0 sm:w-36">rank</span>
                  <div className="flex-grow">
                    <div className="font-mono text-slate-600">int</div>
                    <div className="text-slate-700 mt-1">Positive integer rank (1-indexed from retriever)</div>
                  </div>
                </div>
                <div className="flex flex-col sm:flex-row sm:gap-4">
                  <span className="font-mono font-bold text-sky-700 flex-shrink-0 sm:w-36">score</span>
                  <div className="flex-grow">
                    <div className="font-mono text-slate-600">float</div>
                    <div className="text-slate-700 mt-1">Numeric relevance score from retriever</div>
                  </div>
                </div>
                <div className="flex flex-col sm:flex-row sm:gap-4">
                  <span className="font-mono font-bold text-sky-700 flex-shrink-0 sm:w-36">document_id</span>
                  <div className="flex-grow">
                    <div className="font-mono text-slate-600">str | None</div>
                    <div className="text-slate-700 mt-1">Document ID (required for span form)</div>
                  </div>
                </div>
                <div className="flex flex-col sm:flex-row sm:gap-4">
                  <span className="font-mono font-bold text-sky-700 flex-shrink-0 sm:w-36">start, end</span>
                  <div className="flex-grow">
                    <div className="font-mono text-slate-600">int | None</div>
                    <div className="text-slate-700 mt-1">Character offsets (required for span form, None for text form)</div>
                  </div>
                </div>
                <div className="flex flex-col sm:flex-row sm:gap-4">
                  <span className="font-mono font-bold text-sky-700 flex-shrink-0 sm:w-36">text</span>
                  <div className="flex-grow">
                    <div className="font-mono text-slate-600">str | None</div>
                    <div className="text-slate-700 mt-1">Text chunk (required for text form, None for span form)</div>
                  </div>
                </div>
                <div className="flex flex-col sm:flex-row sm:gap-4">
                  <span className="font-mono font-bold text-sky-700 flex-shrink-0 sm:w-36">span_type</span>
                  <div className="flex-grow">
                    <div className="font-mono text-slate-600">str = "text"</div>
                    <div className="text-slate-700 mt-1">Type classifier (e.g., "text", "table", "metadata")</div>
                  </div>
                </div>
                <div className="flex flex-col sm:flex-row sm:gap-4">
                  <span className="font-mono font-bold text-sky-700 flex-shrink-0 sm:w-36">metadata</span>
                  <div className="flex-grow">
                    <div className="font-mono text-slate-600">dict[str, Any]</div>
                    <div className="text-slate-700 mt-1">Optional additional information for tracking</div>
                  </div>
                </div>
              </div>
            </div>

            <div className="mb-4">
              <h4 className="text-xs font-mono font-semibold text-slate-500 uppercase tracking-widest mb-4">Example</h4>
              <CodeEditor
                code={`from spanchor import RetrievalResult

# Span form (pre-mapped to document)
result1 = RetrievalResult(
    rank=1,
    score=0.95,
    document_id="docs/deployment.md",
    start=142,
    end=288,
    span_type="text"
)

# Text form (needs mapping)
result2 = RetrievalResult(
    rank=2,
    score=0.87,
    text="SSL configuration requires certificate paths...",
    span_type="text"
)`}
                language="python"
                filename="retrieval_result.py"
                showLineNumbers={false}
                showCopyButton={true}
                showResetButton={false}
              />
            </div>
          </div>

          {/* Run */}
          <div className="mb-16 pb-16 border-b border-slate-200">
            <div className="flex items-baseline gap-4 mb-4">
              <h3 className="text-2xl font-mono font-bold text-slate-900">Run</h3>
              <span className="text-xs font-mono bg-slate-100 text-slate-600 px-2 py-1 rounded">class</span>
            </div>
            <p className="text-slate-700 mb-6 text-sm">Complete evaluation output from <code className="font-mono">evaluate()</code>. Contains all metrics, statistics, and configuration.</p>
            
            <div className="mb-8">
              <h4 className="text-xs font-mono font-semibold text-slate-500 uppercase tracking-widest mb-4">Signature</h4>
              <div className="bg-slate-50 border border-slate-200 rounded p-4 font-mono text-sm text-slate-900 overflow-x-auto">
                <div>Run(</div>
                <div className="ml-4">timestamp: str,</div>
                <div className="ml-4">queries: tuple[Query, ...],</div>
                <div className="ml-4">per_query_metrics: dict[str, dict[str, float]],</div>
                <div className="ml-4">aggregate_metrics: dict[str, float],</div>
                <div className="ml-4">config: dict[str, Any],</div>
                <div className="ml-4">mapper_stats: dict[str, int],</div>
                <div className="ml-4">schema_version: str = "0.1.0"</div>
                <div>)</div>
              </div>
            </div>

            <div className="mb-8">
              <h4 className="text-xs font-mono font-semibold text-slate-500 uppercase tracking-widest mb-4">Fields</h4>
              <div className="space-y-3 text-sm">
                <div className="flex flex-col sm:flex-row sm:gap-4">
                  <span className="font-mono font-bold text-sky-700 flex-shrink-0 sm:w-44">timestamp</span>
                  <div className="flex-grow">
                    <div className="font-mono text-slate-600">str</div>
                    <div className="text-slate-700 mt-1">ISO format timestamp (e.g., "2024-01-15T10:30:00Z")</div>
                  </div>
                </div>
                <div className="flex flex-col sm:flex-row sm:gap-4">
                  <span className="font-mono font-bold text-sky-700 flex-shrink-0 sm:w-44">queries</span>
                  <div className="flex-grow">
                    <div className="font-mono text-slate-600">tuple[Query, ...]</div>
                    <div className="text-slate-700 mt-1">Immutable tuple of evaluated Query objects</div>
                  </div>
                </div>
                <div className="flex flex-col sm:flex-row sm:gap-4">
                  <span className="font-mono font-bold text-sky-700 flex-shrink-0 sm:w-44">per_query_metrics</span>
                  <div className="flex-grow">
                    <div className="font-mono text-slate-600">dict[str, dict[str, float]]</div>
                    <div className="text-slate-700 mt-1">Metrics per query_id (e.g., <code className="font-mono">{'"q1": {"recall@5": 0.85, "precision@5": 0.90}'}</code>)</div>
                  </div>
                </div>
                <div className="flex flex-col sm:flex-row sm:gap-4">
                  <span className="font-mono font-bold text-sky-700 flex-shrink-0 sm:w-44">aggregate_metrics</span>
                  <div className="flex-grow">
                    <div className="font-mono text-slate-600">dict[str, float]</div>
                    <div className="text-slate-700 mt-1">Macro-averaged metrics (e.g., <code className="font-mono">{'"mean_recall@5": 0.85'}</code>)</div>
                  </div>
                </div>
                <div className="flex flex-col sm:flex-row sm:gap-4">
                  <span className="font-mono font-bold text-sky-700 flex-shrink-0 sm:w-44">config</span>
                  <div className="flex-grow">
                    <div className="font-mono text-slate-600">dict[str, Any]</div>
                    <div className="text-slate-700 mt-1">Configuration used: k, min_overlap, ambiguity_policy, aggregation_method</div>
                  </div>
                </div>
                <div className="flex flex-col sm:flex-row sm:gap-4">
                  <span className="font-mono font-bold text-sky-700 flex-shrink-0 sm:w-44">mapper_stats</span>
                  <div className="flex-grow">
                    <div className="font-mono text-slate-600">dict[str, int]</div>
                    <div className="text-slate-700 mt-1">Chunk-to-span mapping stats: MAPPED_EXACT, MAPPED_NORMALIZED, AMBIGUOUS, UNMAPPED</div>
                  </div>
                </div>
              </div>
            </div>

            <div className="mb-4">
              <h4 className="text-xs font-mono font-semibold text-slate-500 uppercase tracking-widest mb-4">Example</h4>
              <CodeEditor
                code={`from spanchor import evaluate

run = evaluate(
    documents=[doc1, doc2],
    queries=[query1, query2],
    retrieval_results={"q1": [result1, result2], "q2": [result3]},
    k=5
)

# Access results
print(f"Timestamp: {run.timestamp}")
print(f"Queries: {len(run.queries)}")
print(f"Recall@5: {run.aggregate_metrics['mean_recall@5']}")
print(f"Mapper: {run.mapper_stats}")`}
                language="python"
                filename="run.py"
                showLineNumbers={false}
                showCopyButton={true}
                showResetButton={false}
              />
            </div>
          </div>

          {/* ComparisonResult */}
          <div className="mb-16">
            <div className="flex items-baseline gap-4 mb-4">
              <h3 className="text-2xl font-mono font-bold text-slate-900">ComparisonResult</h3>
              <span className="text-xs font-mono bg-slate-100 text-slate-600 px-2 py-1 rounded">class</span>
            </div>
            <p className="text-slate-700 mb-6 text-sm">Output from <code className="font-mono">compare()</code>. Detects regressions by comparing baseline vs candidate Run objects with policy thresholds.</p>
            
            <div className="mb-8">
              <h4 className="text-xs font-mono font-semibold text-slate-500 uppercase tracking-widest mb-4">Signature</h4>
              <div className="bg-slate-50 border border-slate-200 rounded p-4 font-mono text-sm text-slate-900 overflow-x-auto">
                <div>ComparisonResult(</div>
                <div className="ml-4">per_query_deltas: dict[str, dict[str, float]],</div>
                <div className="ml-4">per_query_status: dict[str, Literal["IMPROVED", "REGRESSION", "UNCHANGED"]],</div>
                <div className="ml-4">aggregate_deltas: dict[str, float],</div>
                <div className="ml-4">has_regression: bool</div>
                <div>)</div>
              </div>
            </div>

            <div className="mb-8">
              <h4 className="text-xs font-mono font-semibold text-slate-500 uppercase tracking-widest mb-4">Fields</h4>
              <div className="space-y-3 text-sm">
                <div className="flex flex-col sm:flex-row sm:gap-4">
                  <span className="font-mono font-bold text-sky-700 flex-shrink-0 sm:w-44">per_query_deltas</span>
                  <div className="flex-grow">
                    <div className="font-mono text-slate-600">dict[str, dict[str, float]]</div>
                    <div className="text-slate-700 mt-1">Metric deltas (candidate - baseline) per query_id</div>
                  </div>
                </div>
                <div className="flex flex-col sm:flex-row sm:gap-4">
                  <span className="font-mono font-bold text-sky-700 flex-shrink-0 sm:w-44">per_query_status</span>
                  <div className="flex-grow">
                    <div className="font-mono text-slate-600">dict[str, str]</div>
                    <div className="text-slate-700 mt-1">Status per query: "IMPROVED", "REGRESSION", or "UNCHANGED"</div>
                  </div>
                </div>
                <div className="flex flex-col sm:flex-row sm:gap-4">
                  <span className="font-mono font-bold text-sky-700 flex-shrink-0 sm:w-44">aggregate_deltas</span>
                  <div className="flex-grow">
                    <div className="font-mono text-slate-600">dict[str, float]</div>
                    <div className="text-slate-700 mt-1">Macro-averaged metric deltas across all queries</div>
                  </div>
                </div>
                <div className="flex flex-col sm:flex-row sm:gap-4">
                  <span className="font-mono font-bold text-sky-700 flex-shrink-0 sm:w-44">has_regression</span>
                  <div className="flex-grow">
                    <div className="font-mono text-slate-600">bool</div>
                    <div className="text-slate-700 mt-1">True if any query regressed beyond policy threshold</div>
                  </div>
                </div>
              </div>
            </div>

            <div className="mb-4">
              <h4 className="text-xs font-mono font-semibold text-slate-500 uppercase tracking-widest mb-4">Example</h4>
              <CodeEditor
                code={`from spanchor import compare

result = compare(
    baseline=baseline_run,
    candidate=candidate_run,
    policy={"mean_recall@5": -0.05}  # Fail if recall drops > 5%
)

if result.has_regression:
    print("❌ Regression detected!")
    for q_id, status in result.per_query_status.items():
        if status == "REGRESSION":
            print(f"Query {q_id}: {result.per_query_deltas[q_id]}")
else:
    print("✅ All tests passed")`}
                language="python"
                filename="comparison.py"
                showLineNumbers={false}
                showCopyButton={true}
                showResetButton={false}
              />
            </div>
          </div>
        </section>

        {/* EVALUATION SECTION */}
        <section id="evaluation" className="mb-24 scroll-mt-20">
          <div className="mb-16">
            <h2 className="text-4xl font-bold text-slate-900 mb-2">02 Evaluation</h2>
            <p className="text-slate-600">Core evaluation function with configurable policies.</p>
          </div>

          <div className="mb-8 pb-16 border-b border-slate-200">
            <h3 className="text-2xl font-mono font-bold text-slate-900 mb-6">evaluate()</h3>
            
            <div className="mb-8">
              <h4 className="text-xs font-mono font-semibold text-slate-500 uppercase tracking-widest mb-4">Signature</h4>
              <div className="bg-slate-50 border border-slate-200 rounded p-4 font-mono text-sm text-slate-900 overflow-x-auto">
                <div>evaluate(</div>
                <div className="ml-4">documents: list[Document],</div>
                <div className="ml-4">queries: list[Query],</div>
                <div className="ml-4">retrieval_results: dict[str, list[RetrievalResult]],</div>
                <div className="ml-4">k: int = 5,</div>
                <div className="ml-4">min_overlap: float = 0.5,</div>
                <div className="ml-4">max_unmapped_rate: float = 0.1,</div>
                <div className="ml-4">ambiguity_policy: str = "first_unclaimed",</div>
                <div className="ml-4">aggregation_method: str = "macro"</div>
                <div>) → Run</div>
              </div>
            </div>

            <div className="mb-8">
              <h4 className="text-xs font-mono font-semibold text-slate-500 uppercase tracking-widest mb-4">Parameters</h4>
              <div className="space-y-4 text-sm">
                <div className="flex flex-col sm:flex-row sm:gap-4">
                  <span className="font-mono font-bold text-sky-700 flex-shrink-0 sm:w-40">documents</span>
                  <div className="flex-grow">
                    <div className="font-mono text-slate-600">list[Document]</div>
                    <div className="text-slate-700 mt-1">Canonical source documents (use Document.from_text())</div>
                  </div>
                </div>
                <div className="flex flex-col sm:flex-row sm:gap-4">
                  <span className="font-mono font-bold text-sky-700 flex-shrink-0 sm:w-40">queries</span>
                  <div className="flex-grow">
                    <div className="font-mono text-slate-600">list[Query]</div>
                    <div className="text-slate-700 mt-1">Evaluation questions with ground-truth anchors</div>
                  </div>
                </div>
                <div className="flex flex-col sm:flex-row sm:gap-4">
                  <span className="font-mono font-bold text-sky-700 flex-shrink-0 sm:w-40">retrieval_results</span>
                  <div className="flex-grow">
                    <div className="font-mono text-slate-600">dict[str, list[RetrievalResult]]</div>
                    <div className="text-slate-700 mt-1">Results indexed by query_id</div>
                  </div>
                </div>
                <div className="flex flex-col sm:flex-row sm:gap-4">
                  <span className="font-mono font-bold text-sky-700 flex-shrink-0 sm:w-40">k</span>
                  <div className="flex-grow">
                    <div className="font-mono text-slate-600">int = 5</div>
                    <div className="text-slate-700 mt-1">Cutoff for @k metrics (recall@k, precision@k, etc.)</div>
                  </div>
                </div>
                <div className="flex flex-col sm:flex-row sm:gap-4">
                  <span className="font-mono font-bold text-sky-700 flex-shrink-0 sm:w-40">min_overlap</span>
                  <div className="flex-grow">
                    <div className="font-mono text-slate-600">float = 0.5</div>
                    <div className="text-slate-700 mt-1">Minimum IoU (intersection over union) for span match (0.0–1.0)</div>
                  </div>
                </div>
                <div className="flex flex-col sm:flex-row sm:gap-4">
                  <span className="font-mono font-bold text-sky-700 flex-shrink-0 sm:w-40">max_unmapped_rate</span>
                  <div className="flex-grow">
                    <div className="font-mono text-slate-600">float = 0.1</div>
                    <div className="text-slate-700 mt-1">Max allowed unmapped text-form results (0.0–1.0). Raises if exceeded.</div>
                  </div>
                </div>
                <div className="flex flex-col sm:flex-row sm:gap-4">
                  <span className="font-mono font-bold text-sky-700 flex-shrink-0 sm:w-40">ambiguity_policy</span>
                  <div className="flex-grow">
                    <div className="font-mono text-slate-600">str = "first_unclaimed"</div>
                    <div className="text-slate-700 mt-1">Conflict resolution: "first_unclaimed", "all_matches", "longest"</div>
                  </div>
                </div>
                <div className="flex flex-col sm:flex-row sm:gap-4">
                  <span className="font-mono font-bold text-sky-700 flex-shrink-0 sm:w-40">aggregation_method</span>
                  <div className="flex-grow">
                    <div className="font-mono text-slate-600">str = "macro"</div>
                    <div className="text-slate-700 mt-1">Averaging method: "macro" (unweighted mean), "micro" (global)</div>
                  </div>
                </div>
              </div>
            </div>

            <div className="mb-4">
              <h4 className="text-xs font-mono font-semibold text-slate-500 uppercase tracking-widest mb-4">Returns</h4>
              <div className="bg-slate-50 border border-slate-200 rounded p-4 font-mono text-sm text-slate-900">
                Run — Complete evaluation output with metrics and config
              </div>
            </div>

            <div className="mb-4">
              <h4 className="text-xs font-mono font-semibold text-slate-500 uppercase tracking-widest mb-4">Example</h4>
              <CodeEditor
                code={`from spanchor import evaluate

run = evaluate(
    documents=[doc1, doc2, doc3],
    queries=[q1, q2, q3],
    retrieval_results={
        "q1": [res1, res2, res3],
        "q2": [res4, res5],
        "q3": [res6, res7, res8]
    },
    k=5,
    min_overlap=0.5,
    max_unmapped_rate=0.1,
    ambiguity_policy="first_unclaimed",
    aggregation_method="macro"
)

print(run.aggregate_metrics)
print(run.mapper_stats)`}
                language="python"
                filename="evaluate_example.py"
                showLineNumbers={false}
                showCopyButton={true}
                showResetButton={false}
              />
            </div>
          </div>
        </section>

        {/* METRICS SECTION */}
        <section id="metrics" className="mb-24 scroll-mt-20">
          <div className="mb-16">
            <h2 className="text-4xl font-bold text-slate-900 mb-2">03 Metrics</h2>
            <p className="text-slate-600">Five verified metrics computed per query and aggregated. Keys in Run objects use @k notation.</p>
          </div>

          <div className="space-y-12">
            <div className="pb-12 border-b border-slate-200">
              <h3 className="text-xl font-mono font-bold text-slate-900 mb-2">recall@k</h3>
              <p className="text-slate-700 text-sm mb-4">Fraction of ground-truth anchors covered by top-k results. Higher is better (0.0–1.0).</p>
              <p className="text-slate-700 text-sm mb-2 font-mono">Definition: (anchors hit in top-k) / (total anchors)</p>
              <p className="text-slate-700 text-sm">Intersection-over-Union (IoU) ≥ min_overlap required for a hit.</p>
            </div>

            <div className="pb-12 border-b border-slate-200">
              <h3 className="text-xl font-mono font-bold text-slate-900 mb-2">precision@k</h3>
              <p className="text-slate-700 text-sm mb-4">Fraction of top-k results that hit ground-truth anchors. Higher is better (0.0–1.0).</p>
              <p className="text-slate-700 text-sm mb-2 font-mono">Definition: (results hit) / (top-k results)</p>
              <p className="text-slate-700 text-sm">Measures retriever quality; penalizes false positives.</p>
            </div>

            <div className="pb-12 border-b border-slate-200">
              <h3 className="text-xl font-mono font-bold text-slate-900 mb-2">hit@k</h3>
              <p className="text-slate-700 text-sm mb-4">Binary: 1.0 if any anchor is covered in top-k, else 0.0.</p>
              <p className="text-slate-700 text-sm mb-2 font-mono">Definition: 1.0 if ∃ result in top-k with IoU ≥ min_overlap else 0.0</p>
              <p className="text-slate-700 text-sm">Useful for ranking-agnostic evaluation ("does the answer exist?").</p>
            </div>

            <div className="pb-12 border-b border-slate-200">
              <h3 className="text-xl font-mono font-bold text-slate-900 mb-2">full_evidence@k</h3>
              <p className="text-slate-700 text-sm mb-4">Binary: 1.0 if ALL ground-truth anchors are covered in top-k, else 0.0.</p>
              <p className="text-slate-700 text-sm mb-2 font-mono">Definition: 1.0 if all anchors covered in top-k else 0.0</p>
              <p className="text-slate-700 text-sm">Strict mode: all evidence must be retrievable in the result set.</p>
            </div>

            <div>
              <h3 className="text-xl font-mono font-bold text-slate-900 mb-2">iou</h3>
              <p className="text-slate-700 text-sm mb-4">Mean intersection-over-union across all query-result pairs in top-k. Measures span overlap quality.</p>
              <p className="text-slate-700 text-sm mb-2 font-mono">Definition: mean(|intersection| / |union|) for each query-result pair</p>
              <p className="text-slate-700 text-sm">Complements recall/precision; penalizes close-but-wrong spans.</p>
            </div>
          </div>
        </section>

        {/* COMPARISON SECTION */}
        <section id="comparison" className="mb-24 scroll-mt-20">
          <div className="mb-16">
            <h2 className="text-4xl font-bold text-slate-900 mb-2">04 Comparison</h2>
            <p className="text-slate-600">Compare baseline and candidate Runs with policy-based regression detection.</p>
          </div>

          <div className="mb-8 pb-16 border-b border-slate-200">
            <h3 className="text-2xl font-mono font-bold text-slate-900 mb-6">compare()</h3>
            
            <div className="mb-8">
              <h4 className="text-xs font-mono font-semibold text-slate-500 uppercase tracking-widest mb-4">Signature</h4>
              <div className="bg-slate-50 border border-slate-200 rounded p-4 font-mono text-sm text-slate-900 overflow-x-auto">
                <div>compare(</div>
                <div className="ml-4">baseline: Run,</div>
                <div className="ml-4">candidate: Run,</div>
                <div className="ml-4">policy: dict[str, float],</div>
                <div className="ml-4">min_query_count: int | None = None</div>
                <div>) → ComparisonResult</div>
              </div>
            </div>

            <div className="mb-8">
              <h4 className="text-xs font-mono font-semibold text-slate-500 uppercase tracking-widest mb-4">Parameters</h4>
              <div className="space-y-4 text-sm">
                <div className="flex flex-col sm:flex-row sm:gap-4">
                  <span className="font-mono font-bold text-sky-700 flex-shrink-0 sm:w-40">baseline</span>
                  <div className="flex-grow">
                    <div className="font-mono text-slate-600">Run</div>
                    <div className="text-slate-700 mt-1">Baseline evaluation run</div>
                  </div>
                </div>
                <div className="flex flex-col sm:flex-row sm:gap-4">
                  <span className="font-mono font-bold text-sky-700 flex-shrink-0 sm:w-40">candidate</span>
                  <div className="flex-grow">
                    <div className="font-mono text-slate-600">Run</div>
                    <div className="text-slate-700 mt-1">Candidate evaluation run</div>
                  </div>
                </div>
                <div className="flex flex-col sm:flex-row sm:gap-4">
                  <span className="font-mono font-bold text-sky-700 flex-shrink-0 sm:w-40">policy</span>
                  <div className="flex-grow">
                    <div className="font-mono text-slate-600">dict[str, float]</div>
                    <div className="text-slate-700 mt-1">Thresholds by metric name (e.g., <code className="font-mono">{'"mean_recall@5": -0.05'}</code> = fail if recall drops {'>'} 5%)</div>
                  </div>
                </div>
                <div className="flex flex-col sm:flex-row sm:gap-4">
                  <span className="font-mono font-bold text-sky-700 flex-shrink-0 sm:w-40">min_query_count</span>
                  <div className="flex-grow">
                    <div className="font-mono text-slate-600">int | None = None</div>
                    <div className="text-slate-700 mt-1">Minimum queries to run on. If None, uses baseline query count.</div>
                  </div>
                </div>
              </div>
            </div>

            <div className="mb-4">
              <h4 className="text-xs font-mono font-semibold text-slate-500 uppercase tracking-widest mb-4">Returns</h4>
              <div className="bg-slate-50 border border-slate-200 rounded p-4 font-mono text-sm text-slate-900">
                ComparisonResult — Deltas, status, and has_regression flag
              </div>
            </div>

            <div className="mb-4">
              <h4 className="text-xs font-mono font-semibold text-slate-500 uppercase tracking-widest mb-4">Example</h4>
              <CodeEditor
                code={`from spanchor import compare

# CI policy: fail if recall drops more than 5%
policy = {
    "mean_recall@5": -0.05,
    "mean_precision@5": -0.03
}

result = compare(
    baseline=baseline_run,
    candidate=candidate_run,
    policy=policy,
    min_query_count=None
)

if result.has_regression:
    print("❌ Regression: metrics fell below policy thresholds")
    exit(1)
else:
    print("✅ All metrics within policy")
    exit(0)`}
                language="python"
                filename="compare_example.py"
                showLineNumbers={false}
                showCopyButton={true}
                showResetButton={false}
              />
            </div>
          </div>
        </section>

        {/* REGRESSION / CI SECTION */}
        <section id="regression" className="mb-24 scroll-mt-20">
          <div className="mb-16">
            <h2 className="text-4xl font-bold text-slate-900 mb-2">05 Regression / CI</h2>
            <p className="text-slate-600">Detect regressions in CI/CD pipelines by comparing baseline and candidate retrieval runs.</p>
          </div>

          <div className="mb-12">
            <h3 className="text-xl font-bold text-slate-900 mb-4">Workflow</h3>
            <div className="space-y-6 text-sm text-slate-700">
              <div className="flex flex-col sm:flex-row sm:gap-4">
                <div className="font-bold text-sky-600 flex-shrink-0">1.</div>
                <div><strong>Establish Baseline:</strong> Run <code className="font-mono">evaluate()</code> on production or main branch. Save the Run to disk.</div>
              </div>
              <div className="flex flex-col sm:flex-row sm:gap-4">
                <div className="font-bold text-sky-600 flex-shrink-0">2.</div>
                <div><strong>Run Candidate:</strong> On PR or feature branch, run <code className="font-mono">evaluate()</code> with new retrieval model.</div>
              </div>
              <div className="flex flex-col sm:flex-row sm:gap-4">
                <div className="font-bold text-sky-600 flex-shrink-0">3.</div>
                <div><strong>Compare:</strong> Call <code className="font-mono">compare(baseline, candidate, policy)</code> with thresholds.</div>
              </div>
              <div className="flex flex-col sm:flex-row sm:gap-4">
                <div className="font-bold text-sky-600 flex-shrink-0">4.</div>
                <div><strong>Gate Decision:</strong> If <code className="font-mono">result.has_regression == True</code>, fail the CI job. Otherwise, merge.</div>
              </div>
            </div>
          </div>

          <div className="mb-12 bg-blue-50 border border-blue-200 rounded-lg p-6">
            <h4 className="font-bold text-slate-900 mb-3">CI Integration Example</h4>
            <CodeEditor
              code={`# .github/workflows/ci.yml (pseudo)
- name: Evaluate candidate model
  run: |
    python -m spanchor evaluate \\
      --documents docs/ \\
      --queries queries.json \\
      --results retrieval_results.json \\
      --output candidate_run.json

- name: Compare with baseline
  run: |
    python -c "
    from spanchor import Run, compare
    import json
    
    with open('baseline_run.json') as f:
        baseline = Run.from_json(f.read())
    with open('candidate_run.json') as f:
        candidate = Run.from_json(f.read())
    
    policy = {'mean_recall@5': -0.05}
    result = compare(baseline, candidate, policy)
    
    if result.has_regression:
        print('REGRESSION DETECTED')
        exit(1)
    else:
        print('All tests passed')
        exit(0)
    "`}
              language="bash"
              filename="ci_workflow.sh"
              showLineNumbers={false}
              showCopyButton={true}
              showResetButton={false}
            />
          </div>
        </section>

        {/* CLI REFERENCE SECTION */}
        <section id="cli" className="mb-24 scroll-mt-20">
          <div className="mb-16">
            <h2 className="text-4xl font-bold text-slate-900 mb-2">06 CLI Reference</h2>
            <p className="text-slate-600">Command-line interface for SPANCHOR evaluation, comparison, and debugging.</p>
          </div>

          <div className="space-y-12">
            <div className="pb-12 border-b border-slate-200">
              <h3 className="text-xl font-mono font-bold text-slate-900 mb-4">spanchor validate</h3>
              <p className="text-slate-700 text-sm mb-4">Validate corpus health and anchor integrity.</p>
              <div className="bg-slate-50 border border-slate-200 rounded p-4 font-mono text-sm text-slate-900 mb-4 overflow-x-auto">
                spanchor validate [--documents DIR] [--queries FILE]
              </div>
              <p className="text-slate-700 text-sm">Output: List of validation errors or "✅ All anchors valid".</p>
            </div>

            <div className="pb-12 border-b border-slate-200">
              <h3 className="text-xl font-mono font-bold text-slate-900 mb-4">spanchor evaluate</h3>
              <p className="text-slate-700 text-sm mb-4">Run full evaluation and output metrics to JSON.</p>
              <div className="bg-slate-50 border border-slate-200 rounded p-4 font-mono text-sm text-slate-900 mb-4 overflow-x-auto">
                spanchor evaluate --documents DIR --queries FILE --results FILE [--output FILE] [--k 5]
              </div>
              <p className="text-slate-700 text-sm">Output: Run object serialized to JSON. Includes per-query and aggregate metrics.</p>
            </div>

            <div className="pb-12 border-b border-slate-200">
              <h3 className="text-xl font-mono font-bold text-slate-900 mb-4">spanchor compare</h3>
              <p className="text-slate-700 text-sm mb-4">Compare baseline and candidate runs with policy thresholds.</p>
              <div className="bg-slate-50 border border-slate-200 rounded p-4 font-mono text-sm text-slate-900 mb-4 overflow-x-auto">
                spanchor compare --baseline FILE --candidate FILE [--policy FILE] [--json]
              </div>
              <p className="text-slate-700 text-sm">Output: Table or JSON. Exit code 0 if no regression, 1 if regression detected.</p>
            </div>

            <div className="pb-12 border-b border-slate-200">
              <h3 className="text-xl font-mono font-bold text-slate-900 mb-4">spanchor locate</h3>
              <p className="text-slate-700 text-sm mb-4">Debug: Find and display the text at an anchor's character span.</p>
              <div className="bg-slate-50 border border-slate-200 rounded p-4 font-mono text-sm text-slate-900 mb-4 overflow-x-auto">
                spanchor locate --document FILE --start INT --end INT
              </div>
              <p className="text-slate-700 text-sm">Output: Text snippet at [start, end), useful for verifying anchors.</p>
            </div>

            <div className="pb-12 border-b border-slate-200">
              <h3 className="text-xl font-mono font-bold text-slate-900 mb-4">spanchor check-corpus</h3>
              <p className="text-slate-700 text-sm mb-4">Validate corpus health: check for orphaned anchors, hash mismatches, etc.</p>
              <div className="bg-slate-50 border border-slate-200 rounded p-4 font-mono text-sm text-slate-900 mb-4 overflow-x-auto">
                spanchor check-corpus --documents DIR --queries FILE [--fix]
              </div>
              <p className="text-slate-700 text-sm">Output: List of issues or "✅ Corpus is healthy". With --fix, attempt automatic repair.</p>
            </div>

            <div>
              <h3 className="text-xl font-mono font-bold text-slate-900 mb-4">spanchor anchor</h3>
              <p className="text-slate-700 text-sm mb-4">Create or extract anchors from document text (interactive tool).</p>
              <div className="bg-slate-50 border border-slate-200 rounded p-4 font-mono text-sm text-slate-900 mb-4 overflow-x-auto">
                spanchor anchor --document FILE [--query TEXT]
              </div>
              <p className="text-slate-700 text-sm">Output: Anchor JSON object with document_id, start, end, and expected_text_hash.</p>
            </div>
          </div>
        </section>

        {/* EXCEPTIONS SECTION */}
        <section id="exceptions" className="mb-24 scroll-mt-20">
          <div className="mb-16">
            <h2 className="text-4xl font-bold text-slate-900 mb-2">07 Exceptions</h2>
            <p className="text-slate-600">Ten exception types for error handling and debugging.</p>
          </div>

          <div className="space-y-8">
            <div className="pb-8 border-b border-slate-200">
              <h3 className="text-lg font-mono font-bold text-slate-900">SpanchorError</h3>
              <p className="text-slate-700 text-sm">Base exception for all SPANCHOR errors.</p>
            </div>

            <div className="pb-8 border-b border-slate-200">
              <h3 className="text-lg font-mono font-bold text-slate-900">AnchorResolutionError</h3>
              <p className="text-slate-700 text-sm">Anchor validation failed: span out of bounds, hash mismatch, or text not found.</p>
            </div>

            <div className="pb-8 border-b border-slate-200">
              <h3 className="text-lg font-mono font-bold text-slate-900">DocumentNotFoundError</h3>
              <p className="text-slate-700 text-sm">Document ID referenced in anchor or query does not exist in corpus.</p>
            </div>

            <div className="pb-8 border-b border-slate-200">
              <h3 className="text-lg font-mono font-bold text-slate-900">EvaluationError</h3>
              <p className="text-slate-700 text-sm">Evaluation failed (invalid config, unmapped rate exceeded, etc.).</p>
            </div>

            <div className="pb-8 border-b border-slate-200">
              <h3 className="text-lg font-mono font-bold text-slate-900">HashMismatchError</h3>
              <p className="text-slate-700 text-sm">Document text changed but SHA256 hash in anchor does not match.</p>
            </div>

            <div className="pb-8 border-b border-slate-200">
              <h3 className="text-lg font-mono font-bold text-slate-900">InvalidRetrievalResultError</h3>
              <p className="text-slate-700 text-sm">RetrievalResult is malformed (missing required fields, conflicting form, etc.).</p>
            </div>

            <div className="pb-8 border-b border-slate-200">
              <h3 className="text-lg font-mono font-bold text-slate-900">InvalidSchemaError</h3>
              <p className="text-slate-700 text-sm">Object schema version unsupported or data structure invalid.</p>
            </div>

            <div className="pb-8 border-b border-slate-200">
              <h3 className="text-lg font-mono font-bold text-slate-900">OrphanedAnchorError</h3>
              <p className="text-slate-700 text-sm">Anchor's document_id does not exist in corpus.</p>
            </div>

            <div className="pb-8 border-b border-slate-200">
              <h3 className="text-lg font-mono font-bold text-slate-900">ComparisonError</h3>
              <p className="text-slate-700 text-sm">Comparison failed: baseline and candidate have incompatible schemas or query sets.</p>
            </div>

            <div>
              <h3 className="text-lg font-mono font-bold text-slate-900">CorpusIssue</h3>
              <p className="text-slate-700 text-sm">Corpus validation detected issues (via check_corpus()). Contains list of problems.</p>
            </div>
          </div>
        </section>

        {/* TYPE REFERENCE SECTION */}
        <section id="types" className="mb-24 scroll-mt-20">
          <div className="mb-16">
            <h2 className="text-4xl font-bold text-slate-900 mb-2">08 Type Reference</h2>
            <p className="text-slate-600">Compact reference for type aliases and serialization.</p>
          </div>

          <div className="mb-12">
            <h4 className="text-xs font-mono font-semibold text-slate-500 uppercase tracking-widest mb-4">Serialization</h4>
            <p className="text-slate-700 text-sm mb-4">All core objects support JSON serialization via <code className="font-mono">.to_json()</code> and <code className="font-mono">.from_json()</code>.</p>
            <CodeEditor
              code={`from spanchor import Document, Query, Run

# Serialize
doc = Document.from_text("docs/deployment.md", raw_text)
json_str = doc.to_json()

# Deserialize
doc2 = Document.from_json(json_str)

# Run objects save/load from file
run.save("run_output.json")
loaded_run = Run.load("run_output.json")`}
              language="python"
              filename="serialization.py"
              showLineNumbers={false}
              showCopyButton={true}
              showResetButton={false}
            />
          </div>

          <div>
            <h4 className="text-xs font-mono font-semibold text-slate-500 uppercase tracking-widest mb-4">Type Aliases</h4>
            <div className="space-y-3 text-sm">
              <div className="flex flex-col sm:flex-row sm:gap-4">
                <span className="font-mono font-bold text-sky-700 flex-shrink-0 sm:w-40">DocumentMap</span>
                <div className="flex-grow">
                  <div className="font-mono text-slate-600">dict[str, Document]</div>
                  <div className="text-slate-700 mt-1">Indexed documents by document_id</div>
                </div>
              </div>
              <div className="flex flex-col sm:flex-row sm:gap-4">
                <span className="font-mono font-bold text-sky-700 flex-shrink-0 sm:w-40">MetricsDict</span>
                <div className="flex-grow">
                  <div className="font-mono text-slate-600">dict[str, float]</div>
                  <div className="text-slate-700 mt-1">Metric name → value mapping</div>
                </div>
              </div>
              <div className="flex flex-col sm:flex-row sm:gap-4">
                <span className="font-mono font-bold text-sky-700 flex-shrink-0 sm:w-40">StatusLiteral</span>
                <div className="flex-grow">
                  <div className="font-mono text-slate-600">Literal["IMPROVED", "REGRESSION", "UNCHANGED"]</div>
                  <div className="text-slate-700 mt-1">Comparison status per query</div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* CROSS LINKS SECTION */}
        <section className="mb-20 py-12 bg-slate-50 border border-slate-200 rounded-lg px-8">
          <h2 className="text-2xl font-bold text-slate-900 mb-6">Learn More</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <a href="/docs" className="group flex items-start gap-3 text-slate-700 hover:text-sky-600 transition-colors">
              <div className="text-2xl">📖</div>
              <div>
                <div className="font-bold">Documentation</div>
                <div className="text-sm text-slate-600">Comprehensive guide to SPANCHOR concepts and workflow</div>
              </div>
            </a>
            <a href="/examples" className="group flex items-start gap-3 text-slate-700 hover:text-sky-600 transition-colors">
              <div className="text-2xl">💻</div>
              <div>
                <div className="font-bold">Examples</div>
                <div className="text-sm text-slate-600">Real-world use cases: evaluation, comparison, CI/CD</div>
              </div>
            </a>
            <a href="/quickstart" className="group flex items-start gap-3 text-slate-700 hover:text-sky-600 transition-colors">
              <div className="text-2xl">🚀</div>
              <div>
                <div className="font-bold">Quickstart</div>
                <div className="text-sm text-slate-600">Get up and running in 5 minutes</div>
              </div>
            </a>
            <a href="/architecture" className="group flex items-start gap-3 text-slate-700 hover:text-sky-600 transition-colors">
              <div className="text-2xl">🏗️</div>
              <div>
                <div className="font-bold">Architecture</div>
                <div className="text-sm text-slate-600">How SPANCHOR works under the hood</div>
              </div>
            </a>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
};

export default API;
