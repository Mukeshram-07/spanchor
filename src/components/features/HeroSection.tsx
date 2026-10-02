import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useReducedMotion } from '../../hooks/useReducedMotion';
import Button from '../ui/Button';
import { ArrowRight, Terminal, HelpCircle, Search, Anchor, BarChart2, AlertTriangle, CheckCircle2, Copy, Check } from 'lucide-react';

interface HeroSectionProps {
  onDemoClick?: () => void;
  onDocsClick?: () => void;
}

const HeroSection: React.FC<HeroSectionProps> = ({
  onDemoClick,
  onDocsClick,
}) => {
  const prefersReducedMotion = useReducedMotion();
  const [copied, setCopied] = useState(false);
  const [activeStep, setActiveStep] = useState(0);

  // Auto animation for RAG evaluation flow on right pane
  useEffect(() => {
    if (prefersReducedMotion) return;
    const interval = setInterval(() => {
      setActiveStep((prev) => (prev + 1) % 5);
    }, 2200);
    return () => clearInterval(interval);
  }, [prefersReducedMotion]);

  const handleCopyInstall = () => {
    navigator.clipboard.writeText('pip install spanchor');
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDemoClick = () => {
    const demoSection = document.getElementById('pipeline-demo');
    if (demoSection) {
      demoSection.scrollIntoView({ behavior: 'smooth' });
    }
    onDemoClick?.();
  };

  const handleDocsClick = () => {
    window.location.href = '/docs';
    onDocsClick?.();
  };

  const heroNodes = [
    {
      id: 0,
      type: 'QUESTION',
      icon: <HelpCircle className="w-4 h-4 text-sky-600" />,
      title: 'QUESTION',
      detail: '"What caused the deployment failure?"',
      tag: 'Input Query',
      tagBg: 'bg-sky-100 text-sky-800'
    },
    {
      id: 1,
      type: 'RETRIEVER',
      icon: <Search className="w-4 h-4 text-purple-600" />,
      title: 'RETRIEVER',
      detail: 'Hybrid Vector + BM25 (3 candidate chunks retrieved)',
      tag: 'Top-K=3',
      tagBg: 'bg-purple-100 text-purple-800'
    },
    {
      id: 2,
      type: 'SOURCE ANCHOR',
      icon: <Anchor className="w-4 h-4 text-sky-600" />,
      title: 'SOURCE ANCHOR',
      detail: 'cloudsync-deployment-guide.md (Span: 589 → 721)',
      tag: 'SHA-256 Validated',
      tagBg: 'bg-amber-100 text-amber-800'
    },
    {
      id: 3,
      type: 'EVALUATION',
      icon: <BarChart2 className="w-4 h-4 text-blue-600" />,
      title: 'EVALUATION',
      detail: 'Recall@5: 0.405 | IoU: 0.782 | Precision@5: 0.020',
      tag: 'Metrics Computed',
      tagBg: 'bg-blue-100 text-blue-800'
    },
    {
      id: 4,
      type: 'REGRESSION',
      icon: <AlertTriangle className="w-4 h-4 text-red-600" />,
      title: 'REGRESSION',
      detail: '19 regressions detected compared to baseline v1',
      tag: '19 Regressed ⚠',
      tagBg: 'bg-red-100 text-red-800'
    }
  ];

  return (
    <section className="w-full py-12 md:py-20 bg-white border-b border-slate-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
          
          {/* LEFT COLUMN: Eyebrow, Headline, Subhead, CTAs, Install Pill */}
          <div className="lg:col-span-6 space-y-6 text-left">
            {/* Small Eyebrow */}
            <div>
              <span className="inline-flex items-center gap-2 px-3 py-1 bg-sky-50 border border-sky-200 text-sky-800 rounded-full text-xs font-mono font-semibold uppercase tracking-wider">
                <span className="w-2 h-2 rounded-full bg-sky-600 animate-pulse" />
                SOURCE-ANCHORED RAG REGRESSION TESTING
              </span>
            </div>

            {/* Headline */}
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-slate-900 tracking-tight leading-[1.1]">
              Regression testing <br className="hidden sm:inline" />
              for{' '}
              <span className="text-sky-600 underline decoration-sky-300 decoration-4 underline-offset-8">
                RAG retrieval.
              </span>
            </h1>

            {/* Subheading */}
            <p className="text-lg sm:text-xl text-slate-600 leading-relaxed font-normal max-w-2xl">
              Validate whether your retrieval pipeline still finds the evidence it needs — using stable source anchors instead of fragile chunk IDs.
            </p>

            {/* Buttons */}
            <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-4 pt-2">
              <Button
                onClick={handleDemoClick}
                variant="primary"
                size="lg"
                className="bg-sky-600 hover:bg-sky-700 text-white font-semibold px-8 py-3.5 rounded-md shadow-md flex items-center justify-center gap-2 text-base transition-all hover:shadow-lg"
              >
                Try Interactive Demo <ArrowRight className="w-4 h-4" />
              </Button>

              <Button
                onClick={handleDocsClick}
                variant="secondary"
                size="lg"
                className="bg-white text-slate-800 border border-slate-300 hover:bg-slate-50 font-medium px-8 py-3.5 rounded-md text-base transition-all"
              >
                Read Documentation
              </Button>
            </div>

            {/* Install Command Pill */}
            <div className="pt-3">
              <div className="inline-flex items-center justify-between gap-4 bg-slate-900 text-slate-100 rounded-md px-4 py-2.5 font-mono text-xs border border-slate-800 shadow-sm min-w-[280px]">
                <div className="flex items-center gap-2">
                  <Terminal className="w-4 h-4 text-sky-400" />
                  <span className="text-slate-400">$</span>
                  <span className="text-slate-100 font-medium">pip install spanchor</span>
                </div>
                <button
                  onClick={handleCopyInstall}
                  className="text-slate-400 hover:text-white transition-colors"
                  title="Copy command"
                >
                  {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
                </button>
              </div>
            </div>
          </div>

          {/* RIGHT COLUMN: Interactive Sophisticated RAG Evaluation Flow Diagram */}
          <div className="lg:col-span-6">
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-6 sm:p-8 shadow-sm">
              <div className="flex items-center justify-between pb-4 mb-6 border-b border-slate-200">
                <div className="flex items-center gap-2">
                  <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-ping" />
                  <span className="text-xs font-mono font-bold uppercase tracking-wider text-slate-700">
                    Live Evaluation Flow Engine
                  </span>
                </div>
                <span className="text-[11px] font-mono text-slate-400">
                  Step {activeStep + 1} of 5
                </span>
              </div>

              {/* Connected Stacked Nodes */}
              <div className="space-y-4 relative">
                {heroNodes.map((node, index) => {
                  const isActive = index === activeStep;
                  const isPassed = index <= activeStep;

                  return (
                    <div key={node.id} className="relative">
                      <motion.button
                        onClick={() => setActiveStep(index)}
                        animate={{ scale: isActive ? 1.02 : 1 }}
                        className={`w-full p-4 rounded-lg border text-left transition-all ${
                          isActive
                            ? 'bg-white border-sky-600 shadow-md ring-2 ring-sky-500/20'
                            : isPassed
                            ? 'bg-white border-slate-300'
                            : 'bg-white/60 border-slate-200 opacity-60'
                        }`}
                      >
                        <div className="flex items-center justify-between mb-1.5">
                          <div className="flex items-center gap-2.5">
                            <div className={`p-1.5 rounded-md ${isActive ? 'bg-sky-100' : 'bg-slate-100'}`}>
                              {node.icon}
                            </div>
                            <span className="font-mono text-xs font-bold text-slate-900 tracking-wider">
                              {node.title}
                            </span>
                          </div>
                          <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-semibold ${node.tagBg}`}>
                            {node.tag}
                          </span>
                        </div>
                        <p className="text-xs font-mono text-slate-700 pl-8 truncate">
                          {node.detail}
                        </p>
                      </motion.button>

                      {index < heroNodes.length - 1 && (
                        <div className="flex justify-center my-1">
                          <div className={`w-0.5 h-3 ${isPassed ? 'bg-sky-400' : 'bg-slate-200'}`} />
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>

              {/* Step Summary Footer */}
              <div className="mt-6 pt-4 border-t border-slate-200 flex items-center justify-between text-xs font-mono text-slate-500">
                <span>Deterministic Local Evaluation</span>
                <span className="text-sky-600 font-semibold flex items-center gap-1">
                  <CheckCircle2 className="w-3.5 h-3.5" /> Ready for CI
                </span>
              </div>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
};

export default HeroSection;
