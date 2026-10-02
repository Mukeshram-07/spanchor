import React, { useState } from 'react';
import { Anchor, ShieldAlert, CheckCircle2, FileCode } from 'lucide-react';

const SourceAnchorDemo: React.FC = () => {
  const [hoveredSpan, setHoveredSpan] = useState(false);

  return (
    <section id="source-anchors" className="w-full py-20 bg-white border-b border-slate-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-3.5 py-1 bg-sky-100 text-sky-800 rounded-full text-xs font-mono font-medium mb-4">
            CORE INNOVATION
          </div>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-slate-900 tracking-tight mb-4">
            Why Source Anchors?
          </h2>
          <p className="text-lg text-slate-600">
            Traditional RAG testing uses fragile generated chunk IDs that break when chunk size or embedding models change. SPANCHOR anchors ground truth directly to source document text spans.
          </p>
        </div>

        {/* Conceptual Comparison: CHUNK ID vs SOURCE ANCHOR */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-16">
          
          {/* Fragile Chunk ID Card */}
          <div className="bg-slate-50 border border-slate-200 rounded-xl p-6 sm:p-8 relative">
            <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-200">
              <div className="flex items-center gap-2.5 text-red-700">
                <ShieldAlert className="w-5 h-5" />
                <h3 className="font-bold text-base text-slate-900">Fragile Chunk IDs</h3>
              </div>
              <span className="px-2.5 py-1 bg-red-100 text-red-800 rounded text-xs font-mono font-bold">
                Breaks on re-chunking
              </span>
            </div>

            <p className="text-sm text-slate-600 mb-6 leading-relaxed">
              When chunk size (e.g. 512 → 256 tokens) or overlap changes, chunk hashes change completely. All historical evaluation benchmarks are rendered invalid.
            </p>

            <div className="bg-slate-900 text-slate-200 rounded-md p-4 font-mono text-xs border border-slate-800 space-y-2">
              <div className="text-slate-500"># Chunk Index ID</div>
              <div className="text-red-400">chunk_id: &quot;vec_idx_589201&quot; [MISSING]</div>
              <div className="text-slate-400">embedding_model: &quot;text-embedding-ada-002&quot;</div>
              <div className="text-slate-500">❌ Fails regression testing when index is rebuilt</div>
            </div>
          </div>

          {/* Stable Source Anchor Card */}
          <div className="bg-sky-50/40 border border-sky-200 rounded-xl p-6 sm:p-8 relative">
            <div className="flex items-center justify-between mb-4 pb-3 border-b border-sky-200">
              <div className="flex items-center gap-2.5 text-sky-800">
                <Anchor className="w-5 h-5 text-sky-600" />
                <h3 className="font-bold text-base text-slate-900">Stable Source Anchors</h3>
              </div>
              <span className="px-2.5 py-1 bg-emerald-100 text-emerald-800 rounded text-xs font-mono font-bold">
                100% Deterministic
              </span>
            </div>

            <p className="text-sm text-slate-600 mb-6 leading-relaxed">
              Anchors ground truth evidence directly to document text character ranges and canonical SHA-256 hashes. Immune to chunking strategy changes.
            </p>

            <div className="bg-slate-900 text-slate-200 rounded-md p-4 font-mono text-xs border border-slate-800 space-y-2">
              <div className="text-sky-400">doc_id: &quot;cloudsync-deployment-guide.md&quot;</div>
              <div className="text-amber-300">span_range: [589, 721]</div>
              <div className="text-emerald-400">sha256: &quot;4a9c2b1f8e9102c...&quot;</div>
              <div className="text-slate-300">✓ Remains valid across any chunking or model change</div>
            </div>
          </div>

        </div>

        {/* Interactive Document Viewer & Inspector */}
        <div className="bg-slate-900 rounded-xl border border-slate-800 p-6 sm:p-8 shadow-2xl text-slate-100">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 mb-6 border-b border-slate-800">
            <div className="flex items-center gap-3">
              <FileCode className="w-5 h-5 text-sky-400" />
              <div>
                <span className="text-xs font-mono text-slate-400 uppercase tracking-wider block">
                  Interactive Document Inspector
                </span>
                <h3 className="font-bold font-mono text-slate-100 text-base">cloudsync-deployment-guide.md</h3>
              </div>
            </div>
            <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 rounded text-xs font-mono font-semibold">
              <CheckCircle2 className="w-3.5 h-3.5" /> ANCHOR VALID
            </span>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
            
            {/* LEFT (~55%): Readable Document Excerpt */}
            <div className="lg:col-span-7 bg-slate-950 p-6 rounded-lg border border-slate-800 space-y-4 text-slate-300 text-sm leading-relaxed font-sans">
              <p className="text-slate-400 text-xs font-mono">
                [Offset 0 - 588] CloudSync is an enterprise file synchronization architecture supporting multi-cloud destinations...
              </p>

              {/* Highlighted Blue Evidence Span */}
              <div
                onMouseEnter={() => setHoveredSpan(true)}
                onMouseLeave={() => setHoveredSpan(false)}
                className={`p-4 rounded border transition-all cursor-pointer ${
                  hoveredSpan
                    ? 'bg-sky-950/90 border-sky-400 ring-2 ring-sky-500/30 text-white'
                    : 'bg-sky-950/60 border-sky-500/50 text-sky-100'
                }`}
              >
                <div className="flex items-center justify-between text-[11px] font-mono text-sky-400 font-bold mb-1.5">
                  <span>EVIDENCE SPAN #001 (CHAR 589 → 721)</span>
                  <span className="underline">Hover to inspect anchor</span>
                </div>
                <p className="font-medium text-base">
                  &quot;CloudSync retries failed uploads three times before marking the operation as failed.&quot;
                </p>
              </div>

              <p className="text-slate-400 text-xs font-mono">
                [Offset 722 - 1200] Each retry incorporates exponential backoff to minimize server payload overhead...
              </p>
            </div>

            {/* RIGHT (~45%): Source Anchor Metadata Inspector Card */}
            <div className="lg:col-span-5 bg-slate-900 border border-slate-800 p-6 rounded-lg space-y-5">
              <div className="flex items-center gap-2 pb-3 border-b border-slate-800 text-sky-400 font-mono text-xs font-bold uppercase">
                <Anchor className="w-4 h-4" />
                <span>Source Anchor Metadata</span>
              </div>

              <div className="space-y-3 font-mono text-xs">
                <div className="flex justify-between py-2 border-b border-slate-800">
                  <span className="text-slate-400">Document:</span>
                  <span className="text-slate-200 font-bold">cloudsync-deployment-guide.md</span>
                </div>

                <div className="flex justify-between py-2 border-b border-slate-800">
                  <span className="text-slate-400">Start Offset:</span>
                  <span className="text-amber-400 font-bold">589</span>
                </div>

                <div className="flex justify-between py-2 border-b border-slate-800">
                  <span className="text-slate-400">End Offset:</span>
                  <span className="text-amber-400 font-bold">721</span>
                </div>

                <div className="flex justify-between py-2 border-b border-slate-800">
                  <span className="text-slate-400">Canonical Length:</span>
                  <span className="text-slate-200 font-bold">132 characters</span>
                </div>

                <div className="flex justify-between py-2 border-b border-slate-800">
                  <span className="text-slate-400">Content Hash:</span>
                  <span className="text-emerald-400 font-bold">sha256:4a9c2b1f8e...</span>
                </div>

                <div className="flex justify-between py-2">
                  <span className="text-slate-400">Status:</span>
                  <span className="text-emerald-400 font-bold flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5" /> VALID
                  </span>
                </div>
              </div>
            </div>

          </div>
        </div>

      </div>
    </section>
  );
};

export default SourceAnchorDemo;
