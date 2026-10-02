import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Copy, Check, Terminal, ArrowRight } from 'lucide-react';
import { fadeIn, slideUp } from '../../utils/animations';
import Button from '../ui/Button';

const quickstartSnippet = `from spanchor import evaluate, GoldSet

# Load source anchor ground truth set
gold_set = GoldSet.from_json("gold_set.json")

# Evaluate candidate retrieval outputs
result = evaluate(
    gold_set=gold_set,
    retrieved_results="candidate_output.json",
    top_k=[1, 3, 5]
)

# Print regression report
result.print_summary()`;

const QuickstartCTA: React.FC = () => {
  const [copiedInstall, setCopiedInstall] = useState(false);
  const [copiedSnippet, setCopiedSnippet] = useState(false);

  const handleCopyInstall = () => {
    navigator.clipboard.writeText('pip install spanchor');
    setCopiedInstall(true);
    setTimeout(() => setCopiedInstall(false), 2000);
  };

  const handleCopySnippet = () => {
    navigator.clipboard.writeText(quickstartSnippet);
    setCopiedSnippet(true);
    setTimeout(() => setCopiedSnippet(false), 2000);
  };

  return (
    <section id="quickstart-cta" className="w-full py-20 bg-white border-t border-slate-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-slate-900 rounded-xl p-8 md:p-12 text-white shadow-xl grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
          <motion.div
            variants={fadeIn}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.3 }}
            className="lg:col-span-5 space-y-6"
          >
            <div className="inline-flex items-center gap-2 px-3 py-1 bg-sky-900/60 text-sky-300 rounded-full text-xs font-mono font-medium border border-sky-700/50">
              5-MINUTE INTEGRATION
            </div>
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-white">
              Get Started with SPANCHOR
            </h2>
            <p className="text-slate-300 text-base leading-relaxed">
              Install the open-source Python package and start detecting RAG retrieval regressions in your CI pipeline today.
            </p>

            <div className="pt-2">
              <p className="text-xs font-mono text-slate-400 mb-2 uppercase tracking-wider">Installation</p>
              <div className="flex items-center justify-between bg-slate-950 border border-slate-800 rounded-md px-4 py-3 font-mono text-sm text-sky-400">
                <div className="flex items-center gap-3">
                  <Terminal className="w-4 h-4 text-slate-500" />
                  <span>pip install spanchor</span>
                </div>
                <button
                  onClick={handleCopyInstall}
                  className="text-slate-400 hover:text-white transition-colors"
                  aria-label="Copy install command"
                >
                  {copiedInstall ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <div className="flex items-center gap-4 pt-4">
              <Button
                variant="primary"
                onClick={() => window.location.href = '/docs/quickstart'}
                className="bg-sky-600 hover:bg-sky-500 text-white font-medium px-6 py-3 rounded-md flex items-center gap-2 text-sm"
              >
                Read Quickstart <ArrowRight className="w-4 h-4" />
              </Button>
            </div>
          </motion.div>

          <motion.div
            variants={slideUp}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.3 }}
            className="lg:col-span-7 bg-slate-950 border border-slate-800 rounded-lg overflow-hidden shadow-2xl"
          >
            <div className="px-4 py-3 bg-slate-900 border-b border-slate-800 flex items-center justify-between text-xs font-mono text-slate-400">
              <span className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-red-500/80 inline-block" />
                <span className="w-3 h-3 rounded-full bg-amber-500/80 inline-block" />
                <span className="w-3 h-3 rounded-full bg-emerald-500/80 inline-block" />
                <span className="ml-2">eval_pipeline.py</span>
              </span>
              <button
                onClick={handleCopySnippet}
                className="flex items-center gap-1.5 hover:text-white transition-colors"
                aria-label="Copy snippet"
              >
                {copiedSnippet ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                <span>{copiedSnippet ? 'Copied' : 'Copy'}</span>
              </button>
            </div>
            <pre className="p-6 font-mono text-xs sm:text-sm text-slate-200 overflow-x-auto leading-relaxed">
              <code>{quickstartSnippet}</code>
            </pre>
          </motion.div>
        </div>
      </div>
    </section>
  );
};

export default QuickstartCTA;
