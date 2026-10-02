import React, { useEffect } from 'react';
import { X } from 'lucide-react';
import { motion } from 'framer-motion';
import type { Variants } from 'framer-motion';
import { cn } from '../../utils/cn';

interface DrawerProps {
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
  side?: 'left' | 'right';
  title?: string;
  className?: string;
}

const Drawer = React.forwardRef<HTMLDivElement, DrawerProps>(
  ({ 
    isOpen,
    onClose,
    children,
    side = 'left',
    title,
    className,
  }, ref) => {
    
    useEffect(() => {
      if (isOpen) {
        document.body.style.overflow = 'hidden';
      } else {
        document.body.style.overflow = 'unset';
      }
      
      return () => {
        document.body.style.overflow = 'unset';
      };
    }, [isOpen]);
    
    const slideVariants: Variants = {
      hidden: {
        x: side === 'left' ? '-100%' : '100%',
      },
      visible: {
        x: 0,
        transition: {
          duration: 0.3,
          ease: 'easeOut',
        },
      },
      exit: {
        x: side === 'left' ? '-100%' : '100%',
        transition: {
          duration: 0.3,
          ease: 'easeIn',
        },
      },
    };
    
    if (!isOpen) return null;
    
    const handleOverlayClick = (e: React.MouseEvent) => {
      if (e.target === e.currentTarget) {
        onClose();
      }
    };
    
    return (
      <div
        className="fixed inset-0 z-50 flex"
        role="presentation"
        onClick={handleOverlayClick}
      >
        {/* Overlay */}
        <motion.div 
          className="absolute inset-0 bg-black/30"
          aria-hidden="true"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.3 }}
        />
        
        {/* Drawer */}
        <motion.div
          ref={ref}
          className={cn(
            'relative bg-primary-bg h-full w-80 max-w-[90vw] shadow-lg flex flex-col',
            side === 'right' ? 'ml-auto' : '',
            className
          )}
          role="dialog"
          aria-modal="true"
          aria-labelledby={title ? 'drawer-title' : undefined}
          variants={slideVariants}
          initial="hidden"
          animate="visible"
          exit="exit"
        >
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-border">
            {title && (
              <h2 
                id="drawer-title"
                className="text-lg font-semibold text-text-primary"
              >
                {title}
              </h2>
            )}
            <button
              onClick={onClose}
              className="ml-auto p-1 hover:bg-secondary-bg rounded transition-colors"
              aria-label="Close drawer"
            >
              <X className="w-5 h-5 text-text-secondary" />
            </button>
          </div>
          
          {/* Content */}
          <div className="flex-1 overflow-y-auto p-4">
            {children}
          </div>
        </motion.div>
      </div>
    );
  }
);

Drawer.displayName = 'Drawer';

export default Drawer;
