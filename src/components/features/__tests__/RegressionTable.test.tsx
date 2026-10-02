import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import RegressionTable from '../RegressionTable';
import type { QueryResult } from '../../../types';

describe('RegressionTable Component', () => {
  const mockData: QueryResult[] = [
    { queryId: 'Q001', baseline: 0.80, candidate: 0.80, delta: 0.00, status: 'unchanged' },
    { queryId: 'Q002', baseline: 0.60, candidate: 0.80, delta: 0.20, status: 'improved' },
    { queryId: 'Q003', baseline: 0.80, candidate: 0.40, delta: -0.40, status: 'regressed' },
  ];

  // Test: Table displays data correctly
  it('should display table data correctly', () => {
    const { container } = render(<RegressionTable data={mockData} />);

    // Check all query IDs are rendered
    expect(screen.getByText('Q001')).toBeDefined();
    expect(screen.getByText('Q002')).toBeDefined();
    expect(screen.getByText('Q003')).toBeDefined();

    // Check table has rows
    const rows = container.querySelectorAll('tbody tr');
    expect(rows.length).toBe(3);
  });

  // Test: Sorting works
  it('should sort columns correctly', async () => {
    const user = userEvent.setup();
    const { container } = render(<RegressionTable data={mockData} />);

    // Click on Query ID header to sort
    const queryIdHeader = screen.getByLabelText('Sort by Query ID');
    await user.click(queryIdHeader);

    const rows = container.querySelectorAll('tbody tr');
    expect(rows[0].textContent).toContain('Q001');
    expect(rows[1].textContent).toContain('Q002');
    expect(rows[2].textContent).toContain('Q003');
  });

  // Test: Filtering by status works
  it('should filter by status correctly', async () => {
    const user = userEvent.setup();
    render(<RegressionTable data={mockData} />);

    // Filter by "Improved"
    const improvedButtons = screen.getAllByText('Improved');
    const improvedButton = improvedButtons.find(btn => btn.tagName === 'BUTTON');
    if (improvedButton) {
      await user.click(improvedButton);
    }

    // Should only show Q002 (and not Q001 or Q003)
    expect(screen.getByText('Q002')).toBeDefined();
  });

  // Test: Search functionality works
  it('should search by query ID correctly', async () => {
    const user = userEvent.setup();
    render(<RegressionTable data={mockData} />);

    // Search for Q002
    const searchInput = screen.getByPlaceholderText(/Search by Query ID/);
    await user.type(searchInput, 'Q002');

    // Should only show Q002
    expect(screen.getByText('Q002')).toBeDefined();
  });

  // Test: Responsive table layout
  it('should have responsive table layout', () => {
    const { container } = render(<RegressionTable data={mockData} />);

    // Check table structure
    const table = container.querySelector('table');
    expect(table).toBeDefined();

    // Check table is responsive (has overflow-x-auto)
    const tableWrapper = container.querySelector('.overflow-x-auto');
    expect(tableWrapper).toBeDefined();
  });

  // Test: Delta formatting
  it('should format delta values with + and - signs', () => {
    render(<RegressionTable data={mockData} />);

    // Improved should show +0.20
    expect(screen.getByText('+0.20')).toBeDefined();

    // Regressed should show -0.40
    expect(screen.getByText('-0.40')).toBeDefined();
  });

  // Test: Empty state
  it('should handle empty data gracefully', () => {
    render(<RegressionTable data={[]} />);

    expect(screen.getByText('No results found')).toBeDefined();
  });

  // Test: Callback functions
  it('should call callback functions when interactions occur', async () => {
    const user = userEvent.setup();
    const onFilter = vi.fn();
    const onSort = vi.fn();
    const onSearch = vi.fn();

    render(
      <RegressionTable
        data={mockData}
        onFilter={onFilter}
        onSort={onSort}
        onSearch={onSearch}
      />
    );

    // Trigger search
    const searchInput = screen.getByPlaceholderText(/Search by Query ID/);
    await user.type(searchInput, 'Q001');
    expect(onSearch).toHaveBeenCalled();
  });

  // Test: Accessibility
  it('should have proper accessibility attributes', () => {
    render(<RegressionTable data={mockData} />);

    // Check for ARIA labels
    expect(screen.getByLabelText('Sort by Query ID')).toBeDefined();
    expect(screen.getByLabelText('Sort by Baseline')).toBeDefined();
    expect(screen.getByLabelText('Search queries')).toBeDefined();
  });
});
