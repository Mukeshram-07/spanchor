import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Play, RotateCcw, Copy, Check, Terminal, CheckCircle2, AlertTriangle } from 'lucide-react';

const PYTHON_DEMO_CODE = `from spanchor import evaluate

# Run evaluation on candidate retriever
result = evaluate(
    queries=queries,
    retrieved=retrieved,
    gold=gold,
)

print(result)`;

type SimState = 'READY' | 'LOADING_DATA' | 'EVALUATING' | 'MATCHING_ANCHORS' | 'CALCULATING_METRICS' | 'REGRESSION_ANALYSIS' | 'COMPLETE';

interface ExecutionQuery {
  id: string;
  name: string;
  status: 'SUCCESS' | 'REGRESSED';
  iou: number;
}

const sampleQueries: ExecutionQuery[] = [
  { id: 'CS-Q-101', name: 'CloudSync SSL port 8443 config', status: 'SUCCESS', iou: 1.00 },
  { id: 'CS-Q-102', name: 'Database verify-full connection string', status: 'SUCCESS', iou: 0.92 },
  { id: 'CS-Q-103', name: 'Upload timeout retry count', status: 'REGRESSED', iou: 0.35 },
  { id: 'CS-Q-104', name: 'Memory limit fallback policy', status: 'SUCCESS', iou: 0.88 },
  { id: 'CS-Q-105', name: 'Cluster migration node sequence', status: 'SUCCESS', iou: 0.95 },
];

const PipelineVisualization: React.FC = () => {
  const [state, setState] = useState<SimState>('READY');
  const [copied, setCopied] = useState(false);
  const [visibleQueryCount, setVisibleQueryCount] = useState(0);

  const handleCopyCode = () => {
    navigator.clipboard.writeText(PYTHON_DEMO_CODE);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleReset = () => {
    setState('READY');
    setVisibleQueryCount(0);
  };

  const handleRun = () => {
    if (state !== 'READY' && state !== 'COMPLETE') return;
    
    setState('LOADING_DATA');
    setVisibleQueryCount(0);

    setTimeout(() => {
      setState('EVALUATING');
    }, 400);

    setTimeout(() => {
      setState('MATCHING_ANCHORS');
      setVisibleQueryCount(2);
    }, 900);

    setTimeout(() => {
      setState('CALCULATING_METRICS');
      setVisibleQueryCount(5);
    }, 1500);

    setTimeout(() => {
      setState('REGRESSION_ANALYSIS');
    }, 2000);

    setTimeout(() => {
      setState('COMPLETE');
    }, 2500);
  };

  return (
    <section id="pipeline-demo" className="w-full py-20 bg-slate-50 border-b border-slate-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-12">
          <div className="inline-flex items-center gap-2 px-3.5 py-1 bg-sky-100 text-sky-800 rounded-full text-xs font-mono font-medium mb-4">
            SIGNATURE INTERACTIVE EXPERIENCE
          </div>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-slate-900 tracking-tight mb-4">
            See SPANCHOR in action
          </h2>
          <p className="text-lg text-slate-600">
            Watch a retrieval evaluation move from code execution to deterministic regression results.
          </p>
        </div>

        {/* Large Dark Code & Terminal Workspace */}
        <div className="bg-slate-900 rounded-xl border border-slate-800 shadow-2xl overflow-hidden text-slate-100">
          
          {/* Workspace Top Bar */}
          <div className="px-6 py-4 bg-slate-950 border-b border-slate-800 flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <span className="w-3 h-3 rounded-full bg-red-500/80 inline-block" />
              <span className="w-3 h-3 rounded-full bg-amber-500/80 inline-block" />
              <span className="w-3 h-3 rounded-full bg-emerald-500/80 inline-block" />
              <span className="font-mono text-xs font-semibold text-slate-400 ml-2">
                eval_workspace.py — SPANCHOR Runner
              </span>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-xs font-mono text-slate-400 mr-2">Status:</span>
              <span className={`px-2.5 py-1 rounded text-xs font-mono font-bold ${
                state === 'COMPLETE'
                  ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'
                  : state === 'READY'
                  ? 'bg-slate-800 text-slate-300'
                  : 'bg-sky-500/20 text-sky-400 border border-sky-500/40 animate-pulse'
              }`}>
                {state.replace('_', ' ')}
              </span>
            </div>
          </div>

          {/* Split Pane Workspace Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-12 divide-y lg:divide-y-0 lg:divide-x divide-slate-800">
            
            {/* LEFT PANE (~45%): Code Editor & Controls */}
            <div className="lg:col-span-5 p-6 flex flex-col justify-between space-y-6">
              <div>
                <div className="flex items-center justify-between mb-4 pb-2 border-b border-slate-800 text-xs font-mono text-slate-400">
                  <span>PYTHON EVALUATION SCRIPT</span>
                  <button
                    onClick={handleCopyCode}
                    className="flex items-center gap-1.5 hover:text-white transition-colors"
                  >
                    {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                    <span>{copied ? 'Copied' : 'Copy'}</span>
                  </button>
                </div>

                <div className="rounded-lg bg-slate-950 p-4 border border-slate-800 font-mono text-sm leading-relaxed overflow-x-auto text-slate-200">
                  <pre><code>{PYTHON_DEMO_CODE}</code></pre>
                </div>
              </div>

              {/* Action Control Buttons */}
              <div className="flex items-center gap-3 pt-2">
                <button
                  onClick={handleRun}
                  disabled={state !== 'READY' && state !== 'COMPLETE'}
                  className="flex-1 bg-sky-600 hover:bg-sky-500 disabled:opacity-50 text-white font-medium py-3 px-4 rounded-md flex items-center justify-center gap-2 text-sm transition-all shadow-md"
                >
                  <Play className="w-4 h-4 fill-white" />
                  <span>Run Evaluation</span>
                </button>

                <button
                  onClick={handleReset}
                  className="bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium py-3 px-4 rounded-md flex items-center gap-2 text-sm transition-all border border-slate-700"
                >
                  <RotateCcw className="w-4 h-4" />
                  <span>Reset</span>
                </button>
              </div>
            </div>

            {/* RIGHT PANE (~55%): Live Visualization & Terminal Output */}
            <div className="lg:col-span-7 p-6 flex flex-col justify-between space-y-6 bg-slate-950/60">
              <div>
                <div className="flex items-center justify-between mb-4 pb-2 border-b border-slate-800 text-xs font-mono text-slate-400">
                  <span className="flex items-center gap-2">
                    <Terminal className="w-4 h-4 text-sky-400" />
                    <span>SPANCHOR EXECUTION STREAM</span>
                  </span>
                  <span>100 Benchmark Queries</span>
                </div>

                {/* Animated Executing Queries */}
                <div className="space-y-2 mb-6 min-h-[140px]">
                  {state === 'READY' ? (
                    <div className="h-32 flex flex-col items-center justify-center text-slate-500 text-xs font-mono gap-2 border border-dashed border-slate-800 rounded-lg">
                      <Play className="w-5 h-5 text-slate-600" />
                      <span>Click &quot;Run Evaluation&quot; to execute simulation...</span>
                    </div>
                  ) : (
                    sampleQueries.slice(0, visibleQueryCount).map((q) => (
                      <motion.div
                        key={q.id}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="flex items-center justify-between bg-slate-900 border border-slate-800 px-3.5 py-2 rounded text-xs font-mono"
                      >
                        <div className="flex items-center gap-2.5">
                          <span className="text-sky-400 font-bold">{q.id}</span>
                          <span className="text-slate-300">{q.name}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-[10px] text-slate-500">IoU: {q.iou.toFixed(2)}</span>
                          {q.status === 'SUCCESS' ? (
                            <span className="flex items-center gap-1 text-emerald-400 font-bold">
                              <CheckCircle2 className="w-3.5 h-3.5" /> MATCHED
                            </span>
                          ) : (
                            <span className="flex items-center gap-1 text-red-400 font-bold">
                              <AlertTriangle className="w-3.5 h-3.5" /> REGRESSED
                            </span>
                          )}
                        </div>
                      </motion.div>
                    ))
                  )}
                </div>

                {/* Live Metric Outcome Cards */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2">
                  <div className="bg-slate-900 border border-slate-800 rounded p-3 text-center">
                    <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider block mb-1">
                      Recall@5
                    </span>
                    <span className="text-xl font-bold font-mono text-slate-100">
                      {state === 'COMPLETE' || state === 'REGRESSION_ANALYSIS' ? '0.405' : '—'}
                    </span>
                  </div>

                  <div className="bg-slate-900 border border-slate-800 rounded p-3 text-center">
                    <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider block mb-1">
                      Precision@5
                    </span>
                    <span className="text-xl font-bold font-mono text-slate-100">
                      {state === 'COMPLETE' || state === 'REGRESSION_ANALYSIS' ? '0.020' : '—'}
                    </span>
                  </div>

                  <div className="bg-slate-900 border border-slate-800 rounded p-3 text-center">
                    <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider block mb-1">
                      Hit@5
                    </span>
                    <span className="text-xl font-bold font-mono text-slate-100">
                      {state === 'COMPLETE' || state === 'REGRESSION_ANALYSIS' ? '0.410' : '—'}
                    </span>
                  </div>

                  <div className="bg-slate-900 border border-slate-800 rounded p-3 text-center">
                    <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider block mb-1">
                      Regressions
                    </span>
                    <span className="text-xl font-bold font-mono text-red-400">
                      {state === 'COMPLETE' || state === 'REGRESSION_ANALYSIS' ? '19' : '—'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Terminal Output Log Stream */}
              <div className="bg-slate-950 rounded p-3 font-mono text-xs text-slate-400 border border-slate-800 overflow-x-auto">
                <div className="flex items-center justify-between text-[10px] text-slate-500 mb-1">
                  <span>STDOUT STREAM</span>
                  <span>spanchor evaluate CLI</span>
                </div>
                <code>
                  $ spanchor evaluate --gold-set cloudsync.json --candidate hybrid_v2.json<br />
                  {state !== 'READY' && 'Loading ground truth gold set... ✓ 100 queries loaded\n'}
                  {(state === 'CALCULATING_METRICS' || state === 'REGRESSION_ANALYSIS' || state === 'COMPLETE') &&
                    'Computing metrics... Recall@5: 0.405 | Hit@5: 0.410\n'}
                  {state === 'COMPLETE' && (
                    <span className="text-red-400">✓ Regression analysis complete. 19 regressions detected.</span>
                  )}
                </code>
              </div>

            </div>

          </div>
        </div>

      </div>
    </section>
  );
};

export default PipelineVisualization;
