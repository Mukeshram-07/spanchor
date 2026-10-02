import React, { useEffect } from 'react';
import { X } from 'lucide-react';
import { cn } from '../../utils/cn';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  className?: string;
}

const Modal = React.forwardRef<HTMLDivElement, ModalProps>(
  ({ 
    isOpen,
    onClose,
    title,
    children,
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
    
    if (!isOpen) return null;
    
    const handleOverlayClick = (e: React.MouseEvent) => {
      if (e.target === e.currentTarget) {
        onClose();
      }
    };
    
    return (
      <div
        className="fixed inset-0 z-50 flex items-center justify-center"
        role="presentation"
        onClick={handleOverlayClick}
      >
        {/* Overlay */}
        <div 
          className="absolute inset-0 bg-black/50"
          aria-hidden="true"
        />
        
        {/* Modal */}
        <div
          ref={ref}
          className={cn(
            'relative bg-primary-bg rounded-lg shadow-lg max-w-md w-full mx-4 max-h-[90vh] overflow-auto',
            className
          )}
          role="dialog"
          aria-modal="true"
          aria-labelledby={title ? 'modal-title' : undefined}
        >
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-border">
            {title && (
              <h2 
                id="modal-title"
                className="text-lg font-semibold text-text-primary"
              >
                {title}
              </h2>
            )}
            <button
              onClick={onClose}
              className="ml-auto p-1 hover:bg-secondary-bg rounded transition-colors"
              aria-label="Close modal"
            >
              <X className="w-5 h-5 text-text-secondary" />
            </button>
          </div>
          
          {/* Content */}
          <div className="p-6">
            {children}
          </div>
        </div>
      </div>
    );
  }
);

Modal.displayName = 'Modal';

export default Modal;
