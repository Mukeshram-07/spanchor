import React from 'react';
import { motion } from 'framer-motion';
import { Target, CheckCircle2, Ratio, Percent, Layers, Hash } from 'lucide-react';
import Badge from '../ui/Badge';
import { fadeIn, slideUp } from '../../utils/animations';

interface MetricItem {
  id: string;
  name: string;
  formula: string;
  definition: string;
  interpretation: string;
  icon: React.ReactNode;
  badgeText: string;
  example: string;
}

const metricsList: MetricItem[] = [
  {
    id: 'hit-at-k',
    name: 'Hit@K',
    formula: 'Hit@K = 1 if Σ Match(retrieved_i, gold) > 0 else 0',
    definition: 'Binary indicator showing whether at least one ground-truth source anchor span is retrieved in top K results.',
    interpretation: 'Measures basic retrieval availability.',
    icon: <Target className="w-5 h-5 text-sky-600" />,
    badgeText: 'Binary Success',
    example: 'Hit@5 = 1 (Anchor found in top 5 chunks)'
  },
  {
    id: 'recall-at-k',
    name: 'Recall@K',
    formula: 'Recall@K = |Retrieved Spans ∩ Gold Spans| / |Gold Spans|',
    definition: 'Fraction of ground-truth evidence character length successfully captured by top K retrieved chunks.',
    interpretation: 'Measures evidence completeness.',
    icon: <Percent className="w-5 h-5 text-emerald-600" />,
    badgeText: 'Coverage Ratio',
    example: 'Recall@5 = 0.405 (40.5% of evidence captured)'
  },
  {
    id: 'precision-at-k',
    name: 'Precision@K',
    formula: 'Precision@K = |Retrieved Spans ∩ Gold Spans| / Total Retrieved Length',
    definition: 'Proportion of retrieved context window length that overlaps with verified source anchor spans.',
    interpretation: 'Measures context noise ratio.',
    icon: <Ratio className="w-5 h-5 text-amber-600" />,
    badgeText: 'Density Ratio',
    example: 'Precision@5 = 0.020 (Signal-to-noise density)'
  },
  {
    id: 'iou',
    name: 'IoU (Intersection over Union)',
    formula: 'IoU = Length(Retrieved ∩ Gold) / Length(Retrieved ∪ Gold)',
    definition: 'Ratio of overlapping character area to the combined union area of retrieved chunk and ground truth span.',
    interpretation: 'Measures exact span boundary alignment.',
    icon: <Layers className="w-5 h-5 text-purple-600" />,
    badgeText: 'Boundary Alignment',
    example: 'IoU = 0.782 (78.2% exact overlap)'
  },
  {
    id: 'full-evidence-at-k',
    name: 'Full Evidence@K',
    formula: 'Full Evidence@K = ∏ I(Retrieved in Top K(span_i))',
    definition: 'Binary check verifying whether ALL required source anchor spans for multi-span queries are retrieved.',
    interpretation: 'Ensures zero evidence gaps for complex queries.',
    icon: <CheckCircle2 className="w-5 h-5 text-blue-600" />,
    badgeText: 'Multi-Span Complete',
    example: 'Full Evidence@5 = 1 (All 3 anchors found)'
  },
  {
    id: 'retrieved-chars',
    name: 'Retrieved Characters',
    formula: 'Chars = Σ Length(retrieved_chunk_i)',
    definition: 'Total raw character count returned to downstream LLM prompt context window.',
    interpretation: 'Measures context load & token efficiency.',
    icon: <Hash className="w-5 h-5 text-slate-600" />,
    badgeText: 'Context Size',
    example: 'Chars = 4,120 chars (~1,030 tokens)'
  }
];

const MetricsGrid: React.FC = () => {
  return (
    <section id="metrics" className="w-full py-20 bg-slate-50 border-t border-slate-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          variants={fadeIn}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.3 }}
          className="text-center mb-16"
        >
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-sky-100 text-sky-800 rounded-full text-xs font-mono font-medium mb-4">
            EVALUATION METRICS
          </div>
          <h2 className="text-3xl sm:text-4xl font-bold text-slate-900 tracking-tight mb-4">
            Deterministic Retrieval Metrics
          </h2>
          <p className="text-lg text-slate-600 max-w-2xl mx-auto">
            SPANCHOR evaluates retrieval pipelines using exact character span formulas rather than subjective LLM judge scores.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {metricsList.map((m) => (
            <motion.div
              key={m.id}
              variants={slideUp}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, amount: 0.2 }}
              className="bg-white border border-slate-200 rounded-lg p-6 shadow-sm hover:shadow-md transition-all flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-4">
                  <div className="p-2.5 bg-slate-100 rounded-md">
                    {m.icon}
                  </div>
                  <Badge label={m.badgeText} variant="tech" />
                </div>
                <h3 className="text-xl font-bold text-slate-900 mb-2">
                  {m.name}
                </h3>
                <p className="text-sm text-slate-600 mb-4 leading-relaxed">
                  {m.definition}
                </p>
              </div>

              <div className="pt-4 border-t border-slate-100 font-mono text-xs space-y-2">
                <div className="p-2 bg-slate-50 border border-slate-200 rounded text-slate-700 font-medium overflow-x-auto">
                  {m.formula}
                </div>
                <div className="text-slate-500 text-[11px] flex justify-between items-center">
                  <span>Example output:</span>
                  <span className="font-semibold text-slate-700">{m.example}</span>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default MetricsGrid;
