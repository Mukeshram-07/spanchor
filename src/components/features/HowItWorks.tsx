import React from 'react';
import { motion } from 'framer-motion';
import { FileText, Anchor, Search, BarChart3, ArrowRight } from 'lucide-react';
import { fadeIn, slideUp } from '../../utils/animations';

interface Step {
  stepNumber: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  details: string[];
}

const steps: Step[] = [
  {
    stepNumber: '01',
    title: 'Canonicalize Documents',
    description: 'Raw source documents are loaded and canonicalized with standardized whitespace and character indexing.',
    icon: <FileText className="w-6 h-6 text-sky-600" />,
    details: [
      'Unicode normalization',
      'Stable character offset indexing',
      'Zero chunk-strategy dependency'
    ]
  },
  {
    stepNumber: '02',
    title: 'Define Source Anchors',
    description: 'Ground-truth evidence spans are anchored directly to source text character offsets and SHA-256 hashes.',
    icon: <Anchor className="w-6 h-6 text-sky-600" />,
    details: [
      'Exact text span bounds',
      'SHA-256 canonical text hashing',
      'Resistant to chunking changes'
    ]
  },
  {
    stepNumber: '03',
    title: 'Evaluate Retrieval Chunks',
    description: 'Candidate retrieval chunks are evaluated against ground truth anchors using character overlap math.',
    icon: <Search className="w-6 h-6 text-sky-600" />,
    details: [
      'Intersection over Union (IoU)',
      'Character span matching',
      'Multi-span query support'
    ]
  },
  {
    stepNumber: '04',
    title: 'Detect Regressions',
    description: 'Metrics are calculated and compared against baseline runs to flag regressions before production deployment.',
    icon: <BarChart3 className="w-6 h-6 text-sky-600" />,
    details: [
      'Recall@K & Precision@K deltas',
      'Query-level regression tagging',
      'Automated CI/CD exit codes'
    ]
  }
];

const HowItWorks: React.FC = () => {
  return (
    <section id="how-it-works" className="w-full py-20 bg-white border-t border-slate-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          variants={fadeIn}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.3 }}
          className="text-center mb-16"
        >
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-sky-100 text-sky-800 rounded-full text-xs font-mono font-medium mb-4">
            CANONICAL PROCESS
          </div>
          <h2 className="text-3xl sm:text-4xl font-bold text-slate-900 tracking-tight mb-4">
            How SPANCHOR Works
          </h2>
          <p className="text-lg text-slate-600 max-w-2xl mx-auto">
            A 4-step canonical workflow for reliable, reproducible retrieval testing.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 relative">
          {steps.map((step, idx) => (
            <motion.div
              key={step.stepNumber}
              variants={slideUp}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, amount: 0.2 }}
              className="bg-slate-50 border border-slate-200 rounded-lg p-6 relative flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-4">
                  <span className="font-mono text-2xl font-bold text-sky-600">
                    {step.stepNumber}
                  </span>
                  <div className="p-2 bg-white rounded-md border border-slate-200 shadow-sm">
                    {step.icon}
                  </div>
                </div>
                <h3 className="text-lg font-bold text-slate-900 mb-2">
                  {step.title}
                </h3>
                <p className="text-sm text-slate-600 mb-4 leading-relaxed">
                  {step.description}
                </p>
              </div>

              <div className="pt-4 border-t border-slate-200">
                <ul className="space-y-1.5">
                  {step.details.map((detail, dIdx) => (
                    <li key={dIdx} className="text-xs text-slate-600 flex items-center gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-sky-500 flex-shrink-0" />
                      <span>{detail}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {idx < steps.length - 1 && (
                <div className="hidden lg:block absolute -right-3 top-1/2 -translate-y-1/2 z-10 text-slate-300">
                  <ArrowRight className="w-6 h-6" />
                </div>
              )}
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default HowItWorks;
