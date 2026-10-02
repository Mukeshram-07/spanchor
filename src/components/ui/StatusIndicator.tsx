import React from 'react';
import { Check, AlertCircle, X } from 'lucide-react';
import { cn } from '../../utils/cn';

interface StatusIndicatorProps extends React.HTMLAttributes<HTMLDivElement> {
  status: 'success' | 'warning' | 'error';
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
}

const StatusIndicator = React.forwardRef<HTMLDivElement, StatusIndicatorProps>(
  ({ 
    status,
    size = 'md',
    showLabel = false,
    className,
    ...props 
  }, ref) => {
    
    const sizeMap = {
      sm: 'w-4 h-4',
      md: 'w-6 h-6',
      lg: 'w-8 h-8',
    };
    
    const colorMap = {
      success: 'text-success',
      warning: 'text-warning',
      error: 'text-error',
    };
    
    const labelMap = {
      success: '✓',
      warning: '⚠',
      error: '✗',
    };
    
    const iconMap = {
      success: <Check className={sizeMap[size]} aria-hidden="true" />,
      warning: <AlertCircle className={sizeMap[size]} aria-hidden="true" />,
      error: <X className={sizeMap[size]} aria-hidden="true" />,
    };
    
    return (
      <div
        ref={ref}
        className={cn(
          'flex items-center gap-2',
          colorMap[status],
          className
        )}
        role="img"
        aria-label={`Status: ${status}`}
        {...props}
      >
        {iconMap[status]}
        {showLabel && <span className="text-sm font-medium">{labelMap[status]}</span>}
      </div>
    );
  }
);

StatusIndicator.displayName = 'StatusIndicator';

export default StatusIndicator;
