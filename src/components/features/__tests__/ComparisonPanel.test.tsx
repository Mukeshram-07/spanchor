import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import ComparisonPanel from '../ComparisonPanel';

// Mock framer-motion to simplify testing
vi.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: { children?: React.ReactNode; [key: string]: unknown }) => <div {...props}>{children}</div>,
  },
}));

describe('ComparisonPanel', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    
    // Mock window.matchMedia
    window.matchMedia = vi.fn().mockReturnValue({
      matches: false,
      media: '(prefers-reduced-motion: reduce)',
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    } as unknown as MediaQueryList);
  });

  afterEach(() => {
    vi.runOnlyPendingTimers();
    vi.useRealTimers();
  });

  it('renders the component with heading', () => {
    render(<ComparisonPanel />);
    expect(screen.getByText('Detect retrieval regressions')).toBeInTheDocument();
  });

  it('renders both baseline and candidate columns', () => {
    render(<ComparisonPanel />);
    expect(screen.getByText('BASELINE')).toBeInTheDocument();
    expect(screen.getByText('CANDIDATE')).toBeInTheDocument();
  });

  it('displays all metric labels', () => {
    render(<ComparisonPanel />);
    const labels = screen.getAllByText(/Recall@5|Precision@5|Hit@5/);
    expect(labels.length).toBeGreaterThan(0);
  });

  it('displays summary section with outcome labels', () => {
    render(<ComparisonPanel />);
    expect(screen.getByText('Improved')).toBeInTheDocument();
    expect(screen.getByText('Unchanged')).toBeInTheDocument();
    expect(screen.getByText('Regressed')).toBeInTheDocument();
  });

  it('renders with responsive grid layout', () => {
    const { container } = render(<ComparisonPanel />);
    const gridContainer = container.querySelector('.grid');
    expect(gridContainer).toBeInTheDocument();
    expect(gridContainer).toHaveClass('grid-cols-1', 'md:grid-cols-2');
  });

  it('applies correct styling classes for professional appearance', () => {
    const { container } = render(<ComparisonPanel />);
    const section = container.querySelector('section');
    expect(section).toHaveClass('w-full', 'py-12', 'md:py-16');
    expect(section).toHaveClass('bg-gradient-to-b', 'from-primary-50');
  });

  it('renders cards with proper borders', () => {
    const { container } = render(<ComparisonPanel />);
    const cards = container.querySelectorAll('[class*="border-2"]');
    expect(cards.length).toBeGreaterThan(0);
  });

  it('renders summary cards with appropriate colors', () => {
    const { container } = render(<ComparisonPanel />);
    const improvementCard = container.querySelector('.bg-success-50');
    const unchangedCard = container.querySelector('.bg-neutral-50');
    const regressionCard = container.querySelector('.bg-warning-50');
    
    expect(improvementCard).toBeInTheDocument();
    expect(unchangedCard).toBeInTheDocument();
    expect(regressionCard).toBeInTheDocument();
  });

  it('accepts showAnimation prop', () => {
    const { rerender } = render(<ComparisonPanel showAnimation={true} />);
    expect(screen.getByText('Detect retrieval regressions')).toBeInTheDocument();
    
    rerender(<ComparisonPanel showAnimation={false} />);
    expect(screen.getByText('Detect retrieval regressions')).toBeInTheDocument();
  });

  it('accepts custom className prop', () => {
    const { container } = render(<ComparisonPanel className="custom-class" />);
    const section = container.querySelector('section');
    expect(section).toHaveClass('custom-class');
  });

  it('has proper accessibility attributes', () => {
    const { container } = render(<ComparisonPanel />);
    const section = container.querySelector('section');
    expect(section).toHaveAttribute('aria-labelledby', 'comparison-heading');
    
    const heading = screen.getByText('Detect retrieval regressions');
    expect(heading).toHaveAttribute('id', 'comparison-heading');
  });

  it('displays monospace font for metrics', () => {
    const { container } = render(<ComparisonPanel />);
    const monoElements = container.querySelectorAll('.font-mono');
    expect(monoElements.length).toBeGreaterThan(0);
  });

  it('renders footer note about animation', () => {
    render(<ComparisonPanel />);
    expect(screen.getByText(/Metrics animate into view/)).toBeInTheDocument();
  });
});
