import React from 'react';
import { TrendingUp, Minus, AlertTriangle } from 'lucide-react';

const ComparisonPanel: React.FC = () => {
  return (
    <section id="comparison" className="w-full py-20 bg-slate-50 border-b border-slate-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-3.5 py-1 bg-sky-100 text-sky-800 rounded-full text-xs font-mono font-medium mb-4">
            REGRESSION ANALYSIS
          </div>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-slate-900 tracking-tight mb-4">
            Baseline vs Candidate Comparison
          </h2>
          <p className="text-lg text-slate-600">
            Compare retriever iterations objectively. Detect metric regressions before deploying retriever or embedding model updates to production.
          </p>
        </div>

        {/* Two Large Structured Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
          
          {/* BASELINE CARD */}
          <div className="bg-white border border-slate-200 rounded-xl p-6 sm:p-8 shadow-sm">
            <div className="flex items-center justify-between pb-4 mb-6 border-b border-slate-200">
              <div>
                <span className="text-xs font-mono font-bold uppercase tracking-wider text-slate-400 block mb-1">
                  Retriever Version 1
                </span>
                <h3 className="text-2xl font-extrabold text-slate-900">BASELINE (BM25)</h3>
              </div>
              <span className="px-3 py-1 bg-slate-100 text-slate-700 text-xs font-mono font-semibold rounded">
                Control Group
              </span>
            </div>

            <div className="space-y-6">
              <div>
                <div className="flex justify-between text-xs font-mono mb-1.5">
                  <span className="text-slate-600 font-bold">Recall@5</span>
                  <span className="text-slate-900 font-bold">0.405</span>
                </div>
                <div className="w-full bg-slate-100 h-3 rounded-full overflow-hidden">
                  <div className="bg-slate-700 h-full rounded-full" style={{ width: '40.5%' }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs font-mono mb-1.5">
                  <span className="text-slate-600 font-bold">Precision@5</span>
                  <span className="text-slate-900 font-bold">0.020</span>
                </div>
                <div className="w-full bg-slate-100 h-3 rounded-full overflow-hidden">
                  <div className="bg-slate-700 h-full rounded-full" style={{ width: '20%' }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs font-mono mb-1.5">
                  <span className="text-slate-600 font-bold">Hit@5</span>
                  <span className="text-slate-900 font-bold">0.410</span>
                </div>
                <div className="w-full bg-slate-100 h-3 rounded-full overflow-hidden">
                  <div className="bg-slate-700 h-full rounded-full" style={{ width: '41.0%' }} />
                </div>
              </div>
            </div>
          </div>

          {/* CANDIDATE CARD */}
          <div className="bg-white border border-slate-200 rounded-xl p-6 sm:p-8 shadow-sm">
            <div className="flex items-center justify-between pb-4 mb-6 border-b border-slate-200">
              <div>
                <span className="text-xs font-mono font-bold uppercase tracking-wider text-sky-600 block mb-1">
                  Retriever Version 2
                </span>
                <h3 className="text-2xl font-extrabold text-slate-900">CANDIDATE (Hybrid)</h3>
              </div>
              <span className="px-3 py-1 bg-sky-100 text-sky-800 text-xs font-mono font-semibold rounded">
                Under Test
              </span>
            </div>

            <div className="space-y-6">
              <div>
                <div className="flex justify-between text-xs font-mono mb-1.5">
                  <span className="text-slate-600 font-bold">Recall@5</span>
                  <span className="text-red-600 font-bold flex items-center gap-1">
                    0.249 <span className="text-[11px]">(-0.156)</span>
                  </span>
                </div>
                <div className="w-full bg-slate-100 h-3 rounded-full overflow-hidden">
                  <div className="bg-red-500 h-full rounded-full" style={{ width: '24.9%' }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs font-mono mb-1.5">
                  <span className="text-slate-600 font-bold">Precision@5</span>
                  <span className="text-red-600 font-bold flex items-center gap-1">
                    0.017 <span className="text-[11px]">(-0.003)</span>
                  </span>
                </div>
                <div className="w-full bg-slate-100 h-3 rounded-full overflow-hidden">
                  <div className="bg-red-500 h-full rounded-full" style={{ width: '17%' }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs font-mono mb-1.5">
                  <span className="text-slate-600 font-bold">Hit@5</span>
                  <span className="text-red-600 font-bold flex items-center gap-1">
                    0.260 <span className="text-[11px]">(-0.150)</span>
                  </span>
                </div>
                <div className="w-full bg-slate-100 h-3 rounded-full overflow-hidden">
                  <div className="bg-red-500 h-full rounded-full" style={{ width: '26.0%' }} />
                </div>
              </div>
            </div>
          </div>

        </div>

        {/* Query Delta Outcome Summary Badges */}
        <div className="bg-white border border-slate-200 rounded-xl p-6 sm:p-8 shadow-sm flex flex-col sm:flex-row items-center justify-between gap-6">
          <div>
            <h4 className="text-lg font-bold text-slate-900 mb-1">
              Query Regression Breakdown (100 Queries)
            </h4>
            <p className="text-sm text-slate-600">
              Factual breakdown of query retrieval performance transitions.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <div className="flex items-center gap-2 px-4 py-2 bg-emerald-50 border border-emerald-200 rounded-lg text-emerald-800 text-sm font-mono font-bold">
              <TrendingUp className="w-4 h-4 text-emerald-600" />
              <span>6 Improved</span>
            </div>

            <div className="flex items-center gap-2 px-4 py-2 bg-slate-100 border border-slate-200 rounded-lg text-slate-700 text-sm font-mono font-bold">
              <Minus className="w-4 h-4 text-slate-500" />
              <span>75 Unchanged</span>
            </div>

            <div className="flex items-center gap-2 px-4 py-2 bg-red-50 border border-red-200 rounded-lg text-red-800 text-sm font-mono font-bold">
              <AlertTriangle className="w-4 h-4 text-red-600" />
              <span>19 Regressed</span>
            </div>
          </div>
        </div>

      </div>
    </section>
  );
};

export default ComparisonPanel;
