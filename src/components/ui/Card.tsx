import React from 'react';
import { cn } from '../../utils/cn';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  hoverable?: boolean;
}

const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ 
    className,
    children,
    hoverable = false,
    ...props 
  }, ref) => {
    
    const baseStyles = 'bg-primary-bg rounded-lg border border-border p-6 shadow-sm';
    const hoverStyles = hoverable ? 'hover:shadow-md transition-shadow cursor-pointer' : '';
    
    return (
      <div
        ref={ref}
        className={cn(
          baseStyles,
          hoverStyles,
          className
        )}
        {...props}
      >
        {children}
      </div>
    );
  }
);

Card.displayName = 'Card';

export default Card;
