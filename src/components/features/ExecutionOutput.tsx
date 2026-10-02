import React from 'react';
import { motion } from 'framer-motion';
import { CheckCircle, AlertCircle, Loader } from 'lucide-react';
import type { ExecutionStep } from '../../types';
import { cn } from '../../utils/cn';

interface ExecutionOutputProps {
  steps: ExecutionStep[];
  currentStatus: string;
  progress: number;
  isRunning: boolean;
  className?: string;
}

/**
 * ExecutionOutput Component
 *
 * Displays the execution trace and status of simulation steps.
 * Shows current status, progress indicator, and completed steps.
 */
const ExecutionOutput: React.FC<ExecutionOutputProps> = ({
  steps,
  currentStatus,
  progress,
  isRunning,
  className,
}) => {
  const getStatusIcon = (index: number, completed: number) => {
    if (index < completed) {
      return <CheckCircle className="w-5 h-5 text-success-600" />;
    }
    if (index === completed && isRunning) {
      return <Loader className="w-5 h-5 text-primary-600 animate-spin" />;
    }
    return <AlertCircle className="w-5 h-5 text-neutral-400" />;
  };

  const completedSteps = Math.ceil((progress / 100) * steps.length);

  return (
    <div
      className={cn(
        'rounded-lg border border-neutral-200 bg-white overflow-hidden',
        className
      )}
    >
      {/* Header */}
      <div className="border-b border-neutral-200 px-4 py-3 bg-neutral-50">
        <h3 className="text-sm font-semibold text-neutral-900">Execution Output</h3>
      </div>

      {/* Content */}
      <div className="p-4 space-y-4">
        {/* Status and Progress */}
        <div className="space-y-2">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-neutral-700">
              Status: <span className="text-primary-600">{currentStatus}</span>
            </span>
            <span className="text-xs text-neutral-500">{progress}%</span>
          </div>
          <div className="w-full bg-neutral-200 rounded-full h-2 overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.3 }}
              className="h-full bg-gradient-to-r from-primary-500 to-primary-600"
            />
          </div>
        </div>

        {/* Steps List */}
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {steps.map((step, index) => (
            <motion.div
              key={step.id}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="flex items-start gap-3 p-3 rounded-lg bg-neutral-50 border border-neutral-100"
            >
              <div className="mt-0.5">{getStatusIcon(index, completedSteps)}</div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-neutral-900 truncate">
                  {step.name}
                </p>
                <p className="text-xs text-neutral-600 mt-0.5 line-clamp-2">
                  {step.description}
                </p>
                <p className="text-xs text-neutral-500 mt-1">
                  {step.duration}s
                </p>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Footer Note */}
        <div className="pt-2 border-t border-neutral-100">
          <p className="text-xs text-neutral-500 text-center">
            Frontend simulation • Deterministic results
          </p>
        </div>
      </div>
    </div>
  );
};

export default ExecutionOutput;
