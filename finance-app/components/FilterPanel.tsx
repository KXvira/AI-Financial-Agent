'use client';

import { useState } from 'react';

export interface DatePreset {
  label: string;
  startDate: string;
  endDate: string;
}

export interface FilterPanelProps {
  startDate: string;
  endDate: string;
  onStartDateChange: (date: string) => void;
  onEndDateChange: (date: string) => void;
  onApplyFilters?: () => void;
  showCustomerFilter?: boolean;
  customers?: string[];
  selectedCustomers?: string[];
  onCustomerChange?: (customers: string[]) => void;
  showStatusFilter?: boolean;
  statuses?: string[];
  selectedStatuses?: string[];
  onStatusChange?: (statuses: string[]) => void;
  showAmountFilter?: boolean;
  minAmount?: number;
  maxAmount?: number;
  onMinAmountChange?: (amount: number) => void;
  onMaxAmountChange?: (amount: number) => void;
}

export default function FilterPanel({
  startDate,
  endDate,
  onStartDateChange,
  onEndDateChange,
  onApplyFilters,
  showCustomerFilter = false,
  customers = [],
  selectedCustomers = [],
  onCustomerChange,
  showStatusFilter = false,
  statuses = ['Paid', 'Pending', 'Overdue'],
  selectedStatuses = [],
  onStatusChange,
  showAmountFilter = false,
  minAmount = 0,
  maxAmount = 0,
  onMinAmountChange,
  onMaxAmountChange,
}: FilterPanelProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  // Date presets
  const getDatePresets = (): DatePreset[] => {
    const today = new Date();
    const formatDate = (date: Date) => date.toISOString().split('T')[0];

    return [
      {
        label: 'Today',
        startDate: formatDate(today),
        endDate: formatDate(today),
      },
      {
        label: 'This Week',
        startDate: formatDate(new Date(today.getFullYear(), today.getMonth(), today.getDate() - today.getDay())),
        endDate: formatDate(today),
      },
      {
        label: 'This Month',
        startDate: formatDate(new Date(today.getFullYear(), today.getMonth(), 1)),
        endDate: formatDate(today),
      },
      {
        label: 'Last Month',
        startDate: formatDate(new Date(today.getFullYear(), today.getMonth() - 1, 1)),
        endDate: formatDate(new Date(today.getFullYear(), today.getMonth(), 0)),
      },
      {
        label: 'This Quarter',
        startDate: formatDate(new Date(today.getFullYear(), Math.floor(today.getMonth() / 3) * 3, 1)),
        endDate: formatDate(today),
      },
      {
        label: 'This Year',
        startDate: formatDate(new Date(today.getFullYear(), 0, 1)),
        endDate: formatDate(today),
      },
      {
        label: 'Last Year',
        startDate: formatDate(new Date(today.getFullYear() - 1, 0, 1)),
        endDate: formatDate(new Date(today.getFullYear() - 1, 11, 31)),
      },
      {
        label: 'All Time',
        startDate: '2020-01-01',
        endDate: formatDate(today),
      },
    ];
  };

  const applyPreset = (preset: DatePreset) => {
    onStartDateChange(preset.startDate);
    onEndDateChange(preset.endDate);
    if (onApplyFilters) {
      setTimeout(() => onApplyFilters(), 100);
    }
  };

  const toggleCustomer = (customer: string) => {
    if (!onCustomerChange) return;
    
    const newSelection = selectedCustomers.includes(customer)
      ? selectedCustomers.filter(c => c !== customer)
      : [...selectedCustomers, customer];
    
    onCustomerChange(newSelection);
  };

  const toggleStatus = (status: string) => {
    if (!onStatusChange) return;
    
    const newSelection = selectedStatuses.includes(status)
      ? selectedStatuses.filter(s => s !== status)
      : [...selectedStatuses, status];
    
    onStatusChange(newSelection);
  };

  const clearFilters = () => {
    const today = new Date().toISOString().split('T')[0];
    onStartDateChange('2024-01-01');
    onEndDateChange(today);
    if (onCustomerChange) onCustomerChange([]);
    if (onStatusChange) onStatusChange([]);
    if (onMinAmountChange) onMinAmountChange(0);
    if (onMaxAmountChange) onMaxAmountChange(0);
    if (onApplyFilters) {
      setTimeout(() => onApplyFilters(), 100);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6 mb-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-semibold text-gray-900">🔍 Filters</h2>
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="text-blue-600 hover:text-blue-800 text-sm font-medium"
        >
          {isExpanded ? '▲ Hide Filters' : '▼ Show Filters'}
        </button>
      </div>

      {/* Quick Date Presets */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Quick Date Ranges
        </label>
        <div className="flex flex-wrap gap-2">
          {getDatePresets().map((preset) => (
            <button
              key={preset.label}
              onClick={() => applyPreset(preset)}
              className="px-3 py-1.5 text-sm bg-gray-100 hover:bg-blue-100 text-gray-700 hover:text-blue-700 rounded-lg transition-colors"
            >
              {preset.label}
            </button>
          ))}
        </div>
      </div>

      {/* Custom Date Range */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Start Date
          </label>
          <input
            type="date"
            value={startDate}
            onChange={(e) => onStartDateChange(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            End Date
          </label>
          <input
            type="date"
            value={endDate}
            onChange={(e) => onEndDateChange(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
        <div className="flex items-end gap-2">
          <button
            onClick={onApplyFilters}
            className="flex-1 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            🔄 Apply
          </button>
          <button
            onClick={clearFilters}
            className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
            title="Clear all filters"
          >
            ✕
          </button>
        </div>
      </div>

      {/* Advanced Filters (Collapsible) */}
      {isExpanded && (
        <div className="border-t border-gray-200 pt-4 mt-4 space-y-4">
          {/* Customer Filter */}
          {showCustomerFilter && customers.length > 0 && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Filter by Customer ({selectedCustomers.length} selected)
              </label>
              <div className="max-h-40 overflow-y-auto border border-gray-200 rounded-lg p-3 space-y-2">
                {customers.map((customer) => (
                  <label key={customer} className="flex items-center cursor-pointer hover:bg-gray-50 p-1 rounded">
                    <input
                      type="checkbox"
                      checked={selectedCustomers.includes(customer)}
                      onChange={() => toggleCustomer(customer)}
                      className="mr-2 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <span className="text-sm text-gray-700">{customer}</span>
                  </label>
                ))}
              </div>
            </div>
          )}

          {/* Status Filter */}
          {showStatusFilter && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Filter by Status ({selectedStatuses.length} selected)
              </label>
              <div className="flex flex-wrap gap-2">
                {statuses.map((status) => (
                  <button
                    key={status}
                    onClick={() => toggleStatus(status)}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                      selectedStatuses.includes(status)
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {status}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Amount Range Filter */}
          {showAmountFilter && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Amount Range
              </label>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs text-gray-600 mb-1">Min Amount</label>
                  <input
                    type="number"
                    value={minAmount || ''}
                    onChange={(e) => onMinAmountChange?.(Number(e.target.value))}
                    placeholder="0"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-600 mb-1">Max Amount</label>
                  <input
                    type="number"
                    value={maxAmount || ''}
                    onChange={(e) => onMaxAmountChange?.(Number(e.target.value))}
                    placeholder="No limit"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
