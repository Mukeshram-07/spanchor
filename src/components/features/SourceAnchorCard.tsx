import React from 'react';
import { cn } from '../../utils/cn';
import Card from '../ui/Card';
import StatusIndicator from '../ui/StatusIndicator';

interface SourceAnchorCardProps extends React.HTMLAttributes<HTMLDivElement> {
  document: string;
  start: string;
  end: string;
  status: 'success' | 'warning' | 'error';
  hash: string;
}

const SourceAnchorCard = React.forwardRef<HTMLDivElement, SourceAnchorCardProps>(
  (
    {
      document,
      start,
      end,
      status,
      hash,
      className,
      ...props
    },
    ref
  ) => {
    return (
      <Card
        ref={ref}
        className={cn('space-y-4', className)}
        {...props}
      >
        {/* Header with document name */}
        <div className="border-b border-border pb-4">
          <h3 className="text-sm font-semibold text-text-primary truncate">
            {document}
          </h3>
        </div>

        {/* Content grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {/* Start position */}
          <div className="space-y-1">
            <p className="text-xs font-medium text-text-secondary uppercase tracking-wide">
              Start
            </p>
            <p className="text-sm font-mono text-text-primary">
              {start}
            </p>
          </div>

          {/* End position */}
          <div className="space-y-1">
            <p className="text-xs font-medium text-text-secondary uppercase tracking-wide">
              End
            </p>
            <p className="text-sm font-mono text-text-primary">
              {end}
            </p>
          </div>
        </div>

        {/* Status indicator row */}
        <div className="flex items-center justify-between pt-2 border-t border-border">
          <div className="flex items-center gap-2">
            <p className="text-xs font-medium text-text-secondary uppercase tracking-wide">
              Status
            </p>
            <StatusIndicator status={status} size="sm" showLabel={true} />
          </div>
        </div>

        {/* Hash row */}
        <div className="flex items-center justify-between">
          <p className="text-xs font-medium text-text-secondary uppercase tracking-wide">
            Hash
          </p>
          <p className="text-xs font-mono text-success">
            {hash}
          </p>
        </div>
      </Card>
    );
  }
);

SourceAnchorCard.displayName = 'SourceAnchorCard';

export default SourceAnchorCard;
