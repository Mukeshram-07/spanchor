import React from 'react';
import { motion } from 'framer-motion';
import { GitBranch, Package, ExternalLink, Star } from 'lucide-react';
import { fadeIn } from '../../utils/animations';

const GitHubPyPICTA: React.FC = () => {
  return (
    <section id="community-cta" className="w-full py-16 bg-slate-50 border-t border-slate-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          variants={fadeIn}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.3 }}
          className="flex flex-col sm:flex-row items-center justify-between gap-6 bg-white border border-slate-200 rounded-lg p-8 shadow-sm"
        >
          <div>
            <h3 className="text-xl font-bold text-slate-900 mb-1">
              Open Source & Community Driven
            </h3>
            <p className="text-sm text-slate-600">
              Inspect source code, file issue reports, or contribute to SPANCHOR on GitHub and PyPI.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-4">
            <a
              href="https://github.com/Mukeshram-07/spanchor"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2.5 px-5 py-2.5 bg-slate-900 hover:bg-slate-800 text-white font-medium rounded-md text-sm transition-all shadow-sm"
            >
              <GitBranch className="w-4 h-4" />
              <span>GitHub Repository</span>
              <span className="flex items-center gap-1 bg-slate-800 px-2 py-0.5 rounded text-xs text-amber-300 font-mono">
                <Star className="w-3 h-3 fill-amber-300" /> Star
              </span>
            </a>

            <a
              href="https://pypi.org/project/spanchor/"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2.5 px-5 py-2.5 bg-white border border-slate-300 hover:border-slate-400 text-slate-800 font-medium rounded-md text-sm transition-all"
            >
              <Package className="w-4 h-4 text-sky-600" />
              <span>PyPI Package</span>
              <ExternalLink className="w-3.5 h-3.5 text-slate-400" />
            </a>
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default GitHubPyPICTA;
