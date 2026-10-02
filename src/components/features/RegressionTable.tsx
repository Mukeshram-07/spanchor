import React, { useState, useMemo } from 'react';
import { ChevronUp, ChevronDown, Search, TrendingUp, Minus, AlertTriangle } from 'lucide-react';
import { cn } from '../../utils/cn';
import type { QueryResult } from '../../types';

interface RegressionTableProps {
  data: QueryResult[];
  onFilter?: (status: string) => void;
  onSort?: (column: string, direction: 'asc' | 'desc') => void;
  onSearch?: (query: string) => void;
}

type SortColumn = 'queryId' | 'baseline' | 'candidate' | 'delta' | 'status' | null;
type SortDirection = 'asc' | 'desc';

const RegressionTable = React.forwardRef<HTMLDivElement, RegressionTableProps>(
  ({ data, onFilter, onSort, onSearch }, ref) => {
    const [searchQuery, setSearchQuery] = useState('');
    const [statusFilter, setStatusFilter] = useState<string>('All');
    const [sortColumn, setSortColumn] = useState<SortColumn>(null);
    const [sortDirection, setSortDirection] = useState<SortDirection>('asc');

    const filteredData = useMemo(() => {
      let result = [...data];

      if (statusFilter !== 'All') {
        result = result.filter(
          (item) => item.status.toLowerCase() === statusFilter.toLowerCase()
        );
      }

      if (searchQuery) {
        result = result.filter((item) =>
          item.queryId.toLowerCase().includes(searchQuery.toLowerCase())
        );
      }

      if (sortColumn) {
        result.sort((a, b) => {
          let aVal: number | string;
          let bVal: number | string;

          switch (sortColumn) {
            case 'queryId':
              aVal = a.queryId;
              bVal = b.queryId;
              break;
            case 'baseline':
              aVal = a.baseline;
              bVal = b.baseline;
              break;
            case 'candidate':
              aVal = a.candidate;
              bVal = b.candidate;
              break;
            case 'delta':
              aVal = a.delta;
              bVal = b.delta;
              break;
            case 'status':
              aVal = a.status;
              bVal = b.status;
              break;
            default:
              return 0;
          }

          if (typeof aVal === 'string') {
            return sortDirection === 'asc'
              ? aVal.localeCompare(bVal as string)
              : (bVal as string).localeCompare(aVal);
          }

          return sortDirection === 'asc' ? (aVal as number) - (bVal as number) : (bVal as number) - (aVal as number);
        });
      }

      return result;
    }, [data, statusFilter, searchQuery, sortColumn, sortDirection]);

    const handleSort = (column: SortColumn) => {
      if (sortColumn === column) {
        setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
      } else {
        setSortColumn(column);
        setSortDirection('asc');
      }
      onSort?.(column || '', sortDirection === 'asc' ? 'desc' : 'asc');
    };

    const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      const value = e.target.value;
      setSearchQuery(value);
      onSearch?.(value);
    };

    const handleStatusFilter = (status: string) => {
      setStatusFilter(status);
      onFilter?.(status);
    };

    const formatDelta = (delta: number) => {
      if (delta > 0) return `+${delta.toFixed(2)}`;
      return delta.toFixed(2);
    };

    const renderStatusBadge = (status: string) => {
      const s = status.toUpperCase();
      if (s === 'IMPROVED') {
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded text-xs font-mono font-bold bg-emerald-100 text-emerald-800 border border-emerald-200">
            <TrendingUp className="w-3 h-3 text-emerald-600" /> IMPROVED
          </span>
        );
      }
      if (s === 'REGRESSED') {
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded text-xs font-mono font-bold bg-red-100 text-red-800 border border-red-200">
            <AlertTriangle className="w-3 h-3 text-red-600" /> REGRESSED
          </span>
        );
      }
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded text-xs font-mono font-bold bg-slate-100 text-slate-700 border border-slate-200">
          <Minus className="w-3 h-3 text-slate-400" /> UNCHANGED
        </span>
      );
    };

    const SortIcon = ({ column }: { column: SortColumn }) => {
      if (sortColumn !== column) return null;
      return sortDirection === 'asc' ? <ChevronUp className="w-3.5 h-3.5 inline ml-1" /> : <ChevronDown className="w-3.5 h-3.5 inline ml-1" />;
    };

    return (
      <div ref={ref} className="w-full space-y-4">
        {/* Search & Filter Toolbar */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4 bg-white p-4 border border-slate-200 rounded-lg shadow-sm">
          {/* Search Bar */}
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="text"
              placeholder="Search by Query ID (e.g. CS-Q-101)..."
              value={searchQuery}
              onChange={handleSearchChange}
              aria-label="Search queries"
              className="w-full pl-9 pr-4 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-sky-600 text-sm font-sans"
            />
          </div>

          {/* Filter Tabs */}
          <div className="flex items-center gap-1.5 overflow-x-auto pb-1 sm:pb-0">
            {['All', 'Improved', 'Unchanged', 'Regressed'].map((status) => (
              <button
                key={status}
                onClick={() => handleStatusFilter(status)}
                aria-pressed={statusFilter === status}
                className={cn(
                  'px-3.5 py-1.5 rounded-md font-mono text-xs font-semibold transition-all whitespace-nowrap',
                  statusFilter === status
                    ? 'bg-slate-900 text-white shadow-sm'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                )}
              >
                {status}
              </button>
            ))}
          </div>
        </div>

        {/* Results Info */}
        <div className="text-xs font-mono text-slate-500 flex justify-between items-center px-1">
          <span>Showing {filteredData.length} of {data.length} query evaluation records</span>
          <span>Sorted by: {sortColumn ? sortColumn : 'Default'} ({sortDirection})</span>
        </div>

        {/* High Contrast Table */}
        <div className="overflow-x-auto border border-slate-200 rounded-lg bg-white shadow-sm">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-100 border-b border-slate-200 text-slate-700 font-mono text-xs uppercase tracking-wider">
                <th className="py-3 px-4 font-bold">
                  <button onClick={() => handleSort('queryId')} aria-label="Sort by Query ID" className="hover:text-slate-900">
                    Query ID <SortIcon column="queryId" />
                  </button>
                </th>
                <th className="py-3 px-4 font-bold">
                  <button onClick={() => handleSort('baseline')} aria-label="Sort by Baseline" className="hover:text-slate-900">
                    Baseline Metric <SortIcon column="baseline" />
                  </button>
                </th>
                <th className="py-3 px-4 font-bold">
                  <button onClick={() => handleSort('candidate')} aria-label="Sort by Candidate" className="hover:text-slate-900">
                    Candidate Metric <SortIcon column="candidate" />
                  </button>
                </th>
                <th className="py-3 px-4 font-bold">
                  <button onClick={() => handleSort('delta')} aria-label="Sort by Delta" className="hover:text-slate-900">
                    Delta <SortIcon column="delta" />
                  </button>
                </th>
                <th className="py-3 px-4 font-bold text-center">
                  <button onClick={() => handleSort('status')} aria-label="Sort by Status" className="hover:text-slate-900">
                    Status <SortIcon column="status" />
                  </button>
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 font-mono text-xs">
              {filteredData.length > 0 ? (
                filteredData.map((row, index) => (
                  <tr key={`${row.queryId}-${index}`} className="hover:bg-slate-50 transition-colors">
                    <td className="py-3 px-4 font-bold text-slate-900">{row.queryId}</td>
                    <td className="py-3 px-4 text-slate-700">{row.baseline.toFixed(2)}</td>
                    <td className="py-3 px-4 text-slate-700">{row.candidate.toFixed(2)}</td>
                    <td className={`py-3 px-4 font-bold ${
                      row.delta > 0 ? 'text-emerald-700' : row.delta < 0 ? 'text-red-600' : 'text-slate-500'
                    }`}>
                      {formatDelta(row.delta)}
                    </td>
                    <td className="py-3 px-4 text-center">
                      {renderStatusBadge(row.status)}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={5} className="py-8 text-center text-slate-500 font-sans">
                    No results found
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    );
  }
);

RegressionTable.displayName = 'RegressionTable';

export default RegressionTable;
