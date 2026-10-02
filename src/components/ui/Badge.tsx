import React from 'react';
import { cn } from '../../utils/cn';

interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'tech' | 'status' | 'secondary' | 'primary';
  status?: 'success' | 'warning' | 'error' | 'info';
  label?: string;
  children?: React.ReactNode;
}

const Badge = React.forwardRef<HTMLDivElement, BadgeProps>(
  ({ 
    variant = 'tech', 
    status = 'info',
    label,
    className,
    children,
    ...props 
  }, ref) => {
    
    const baseStyles = 'inline-flex items-center px-3 py-1 rounded-full text-sm font-medium';
    
    const variantStyles = {
      tech: 'bg-secondary-bg text-text-primary border border-border',
      primary: 'bg-primary-100 text-primary-700 border border-primary-300',
      secondary: 'bg-secondary-100 text-secondary-700 border border-secondary-300',
      status: 'flex gap-1',
    };
    
    const statusStyles = {
      success: 'bg-green-50 text-success border border-green-200',
      warning: 'bg-orange-50 text-warning border border-orange-200',
      error: 'bg-red-50 text-error border border-red-200',
      info: 'bg-blue-50 text-accent border border-blue-200',
    };
    
    const statusBgColor = {
      success: '#00AA00',
      warning: '#FF9900',
      error: '#CC0000',
      info: '#0066CC',
    };
    
    const styleClass = variant === 'status' 
      ? cn(baseStyles, variantStyles[variant], statusStyles[status], className)
      : cn(baseStyles, variantStyles[variant as keyof Omit<typeof variantStyles, 'status'>], className);
    
    const content = label || children;
    
    return (
      <div
        ref={ref}
        className={styleClass}
        role="status"
        aria-label={typeof content === 'string' ? content : undefined}
        {...props}
      >
        {variant === 'status' && (
          <span 
            className="w-2 h-2 rounded-full"
            style={{ backgroundColor: statusBgColor[status] }}
          />
        )}
        {content}
      </div>
    );
  }
);

Badge.displayName = 'Badge';

export default Badge;
