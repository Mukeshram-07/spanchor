import React from 'react';
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import SourceAnchorCard from '../SourceAnchorCard';

describe('SourceAnchorCard', () => {
  const defaultProps = {
    document: 'cloudsync-guide.md',
    start: '1248',
    end: '1327',
    status: 'success' as const,
    hash: 'verified',
  };

  it('renders all required fields', () => {
    render(<SourceAnchorCard {...defaultProps} />);

    expect(screen.getByText('cloudsync-guide.md')).toBeDefined();
    expect(screen.getByText('1248')).toBeDefined();
    expect(screen.getByText('1327')).toBeDefined();
    expect(screen.getByText('verified')).toBeDefined();
  });

  it('displays the Start label', () => {
    render(<SourceAnchorCard {...defaultProps} />);
    expect(screen.getByText('Start')).toBeDefined();
  });

  it('displays the End label', () => {
    render(<SourceAnchorCard {...defaultProps} />);
    expect(screen.getByText('End')).toBeDefined();
  });

  it('displays the Status label', () => {
    render(<SourceAnchorCard {...defaultProps} />);
    expect(screen.getByText('Status')).toBeDefined();
  });

  it('displays the Hash label', () => {
    render(<SourceAnchorCard {...defaultProps} />);
    expect(screen.getByText('Hash')).toBeDefined();
  });

  it('renders with success status indicator', () => {
    render(<SourceAnchorCard {...defaultProps} status="success" />);
    const statusImg = screen.getByRole('img', { name: /status: success/i });
    expect(statusImg).toBeDefined();
  });

  it('renders with warning status indicator', () => {
    render(<SourceAnchorCard {...defaultProps} status="warning" />);
    const statusImg = screen.getByRole('img', { name: /status: warning/i });
    expect(statusImg).toBeDefined();
  });

  it('renders with error status indicator', () => {
    render(<SourceAnchorCard {...defaultProps} status="error" />);
    const statusImg = screen.getByRole('img', { name: /status: error/i });
    expect(statusImg).toBeDefined();
  });

  it('supports custom className', () => {
    const { container } = render(
      <SourceAnchorCard {...defaultProps} className="custom-class" />
    );
    const card = container.firstChild as HTMLElement;
    expect(card.className.includes('custom-class')).toBe(true);
  });

  it('applies responsive grid layout', () => {
    const { container } = render(<SourceAnchorCard {...defaultProps} />);
    const gridDiv = container.querySelector('.grid') as HTMLElement;
    expect(gridDiv).toBeDefined();
    expect(gridDiv.className.includes('grid-cols-1')).toBe(true);
    expect(gridDiv.className.includes('sm:grid-cols-2')).toBe(true);
  });
});

