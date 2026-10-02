import React from 'react';
import { motion } from 'framer-motion';
import { Check, X } from 'lucide-react';
import { fadeIn, slideUp } from '../../utils/animations';

interface MatrixRow {
  capability: string;
  isSupported: boolean;
  explanation: string;
}

const matrixData: MatrixRow[] = [
  {
    capability: 'Source-Anchored Retrieval Regression Testing',
    isSupported: true,
    explanation: 'Evaluates whether candidate retrievers consistently retrieve verified ground-truth text evidence.'
  },
  {
    capability: 'Deterministic Math-Based Metric Calculations',
    isSupported: true,
    explanation: 'Uses exact character overlap (IoU, Recall@K) instead of expensive, non-reproducible LLM calls.'
  },
  {
    capability: 'Pytest & GitHub Actions CI Integration',
    isSupported: true,
    explanation: 'Provides automated exit codes and summary reports to block retrieval regression PRs.'
  },
  {
    capability: 'Vector Database / Index Store',
    isSupported: false,
    explanation: 'SPANCHOR does not store embeddings or build vector index structures (e.g. Pinecone, Milvus, Qdrant).'
  },
  {
    capability: 'Embedding Model Generator',
    isSupported: false,
    explanation: 'SPANCHOR does not generate text embeddings or fine-tune embedding models.'
  },
  {
    capability: 'LLM Response Judge / Chatbot Framework',
    isSupported: false,
    explanation: 'SPANCHOR evaluates retrieval output, not downstream LLM generation or chat outputs.'
  },
  {
    capability: 'PDF / OCR Document Converter',
    isSupported: false,
    explanation: 'Document parsing and OCR processing must happen prior to SPANCHOR evaluation.'
  },
  {
    capability: 'Hosted SaaS Platform / Cloud Tracking',
    isSupported: false,
    explanation: 'SPANCHOR is a 100% open-source, local-first Python library and CLI.'
  }
];

const WhatItIsNot: React.FC = () => {
  return (
    <section id="what-it-is-not" className="w-full py-20 bg-slate-50 border-t border-slate-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          variants={fadeIn}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.3 }}
          className="text-center mb-16"
        >
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-sky-100 text-sky-800 rounded-full text-xs font-mono font-medium mb-4">
            SCOPE BOUNDARIES
          </div>
          <h2 className="text-3xl sm:text-4xl font-bold text-slate-900 tracking-tight mb-4">
            What SPANCHOR Is (And Is Not)
          </h2>
          <p className="text-lg text-slate-600 max-w-2xl mx-auto">
            SPANCHOR is strictly focused on retrieval regression testing. We keep boundaries clear so you can integrate it seamlessly into your existing tech stack.
          </p>
        </motion.div>

        <motion.div
          variants={slideUp}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.2 }}
          className="bg-white border border-slate-200 rounded-lg overflow-hidden shadow-sm"
        >
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-100 border-b border-slate-200 text-slate-700 text-xs font-mono uppercase tracking-wider">
                  <th className="py-3.5 px-6 font-semibold">Capability / System</th>
                  <th className="py-3.5 px-6 font-semibold text-center w-32">Status</th>
                  <th className="py-3.5 px-6 font-semibold">Technical Scope Boundary</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 text-sm">
                {matrixData.map((row, idx) => (
                  <tr key={idx} className={row.isSupported ? 'bg-emerald-50/20' : 'hover:bg-slate-50'}>
                    <td className="py-4 px-6 font-medium text-slate-900">
                      {row.capability}
                    </td>
                    <td className="py-4 px-6 text-center">
                      {row.isSupported ? (
                        <span className="inline-flex items-center gap-1 px-2.5 py-1 bg-emerald-100 text-emerald-800 rounded-md text-xs font-bold font-mono">
                          <Check className="w-3.5 h-3.5" /> YES
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 px-2.5 py-1 bg-slate-100 text-slate-600 rounded-md text-xs font-bold font-mono">
                          <X className="w-3.5 h-3.5" /> NO
                        </span>
                      )}
                    </td>
                    <td className="py-4 px-6 text-slate-600 text-xs sm:text-sm leading-relaxed">
                      {row.explanation}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default WhatItIsNot;
