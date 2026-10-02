import React, { useEffect } from 'react';
import { motion } from 'framer-motion';
import { useAnimatedMetric } from '../../hooks/useAnimatedMetric';
import Card from '../ui/Card';
import { cn } from '../../utils/cn';

interface MetricsDisplayProps {
  recall?: number;
  precision?: number;
  hit?: number;
  title?: string;
  className?: string;
  triggerAnimation?: boolean;
}

/**
 * MetricsDisplay Component
 *
 * Displays evaluation metrics (Recall, Precision, Hit) with smooth animations.
 */
const MetricsDisplay: React.FC<MetricsDisplayProps> = ({
  recall = 0.405,
  precision = 0.02,
  hit = 0.41,
  title = 'Evaluation Metrics',
  className,
  triggerAnimation = true,
}) => {
  const recallMetric = useAnimatedMetric(recall, 1200);
  const precisionMetric = useAnimatedMetric(precision, 1200);
  const hitMetric = useAnimatedMetric(hit, 1200);

  useEffect(() => {
    if (triggerAnimation) {
      const timer = setTimeout(() => {
        recallMetric.startAnimation();
        precisionMetric.startAnimation();
        hitMetric.startAnimation();
      }, 100);

      return () => clearTimeout(timer);
    }
  }, [triggerAnimation, recallMetric, precisionMetric, hitMetric]);

  const formatMetric = (value: number): string => {
    return value.toFixed(3);
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 10 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.4 },
    },
  };

  return (
    <Card className={cn('bg-gradient-to-br from-primary-50 to-primary-100 border-primary-200', className)}>
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="space-y-6"
      >
        {/* Title */}
        <motion.div variants={itemVariants}>
          <h3 className="text-lg font-semibold text-neutral-900">{title}</h3>
        </motion.div>

        {/* Metrics Grid */}
        <motion.div variants={itemVariants} className="grid grid-cols-3 gap-4">
          {/* Recall */}
          <div className="text-center p-3 rounded-lg bg-white border border-primary-100">
            <p className="text-xs font-medium text-neutral-600 mb-2">Recall@5</p>
            <p className="text-2xl md:text-3xl font-bold text-primary-600 font-mono">
              {formatMetric(recallMetric.displayValue)}
            </p>
          </div>

          {/* Precision */}
          <div className="text-center p-3 rounded-lg bg-white border border-primary-100">
            <p className="text-xs font-medium text-neutral-600 mb-2">Precision@5</p>
            <p className="text-2xl md:text-3xl font-bold text-primary-600 font-mono">
              {formatMetric(precisionMetric.displayValue)}
            </p>
          </div>

          {/* Hit */}
          <div className="text-center p-3 rounded-lg bg-white border border-primary-100">
            <p className="text-xs font-medium text-neutral-600 mb-2">Hit@5</p>
            <p className="text-2xl md:text-3xl font-bold text-primary-600 font-mono">
              {formatMetric(hitMetric.displayValue)}
            </p>
          </div>
        </motion.div>
      </motion.div>
    </Card>
  );
};

export default MetricsDisplay;
