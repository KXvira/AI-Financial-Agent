'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import ReportChart, { prepareChartData } from '@/components/ReportChart';
import { exportToExcel, exportToCSV, formatDataForExport } from '@/utils/exportUtils';

interface VATSummaryByRate {
  rate: number;
  taxable_amount: number;
  vat_amount: number;
  transaction_count: number;
}

interface VATTransaction {
  transaction_id: string;
  date: string;
  description: string;
  amount: number;
  vat_amount: number;
  vat_rate: number;
  type: string; // 'input' or 'output'
  category: string;
}

interface VATReport {
  report_type: string;
  report_name: string;
  period_start: string;
  period_end: string;
  generated_at: string;
  currency: string;
  output_vat_total: number;
  output_taxable_amount: number;
  output_transaction_count: number;
  output_by_rate: VATSummaryByRate[];
  input_vat_total: number;
  input_taxable_amount: number;
  input_transaction_count: number;
  input_by_rate: VATSummaryByRate[];
  net_vat_payable: number;
  net_vat_refundable: number;
  output_transactions: VATTransaction[];
  input_transactions: VATTransaction[];
  compliance_status: string;
  filing_deadline: string;
  penalties_applicable: boolean;
}

export default function TaxSummaryPage() {
  const [report, setReport] = useState<VATReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [startDate, setStartDate] = useState('2024-01-01');
  const [endDate, setEndDate] = useState('2024-12-31');
  const [includeTransactions, setIncludeTransactions] = useState(false);

  const fetchReport = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(
        `http://localhost:8000/reports/tax/vat-summary?start_date=${startDate}&end_date=${endDate}&include_transactions=${includeTransactions}`
      );
      
      if (!response.ok) {
        throw new Error('Failed to fetch VAT summary');
      }

      const data = await response.json();
      setReport(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      console.error('Error fetching VAT summary:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReport();
  }, []);

  const handleExportExcel = () => {
    if (!report) return;
    
    const data = formatDataForExport({
      'Period': `${report.period_start} to ${report.period_end}`,
      'Generated': new Date(report.generated_at).toLocaleString(),
      'Filing Deadline': report.filing_deadline,
      'Compliance Status': report.compliance_status,
      '': '',
      'OUTPUT VAT (Sales)': '',
      'Total Sales': `${report.currency} ${report.output_taxable_amount.toLocaleString()}`,
      'VAT Collected': `${report.currency} ${report.output_vat_total.toLocaleString()}`,
      'Transactions': report.output_transaction_count,
      ' ': '',
      'INPUT VAT (Purchases)': '',
      'Total Purchases': `${report.currency} ${report.input_taxable_amount.toLocaleString()}`,
      'VAT Paid': `${report.currency} ${report.input_vat_total.toLocaleString()}`,
      'Transactions ': report.input_transaction_count,
      '  ': '',
      'NET POSITION': '',
      'VAT Payable': `${report.currency} ${report.net_vat_payable.toLocaleString()}`,
      'VAT Refundable': `${report.currency} ${report.net_vat_refundable.toLocaleString()}`,
    });
    
    exportToExcel(data, 'VAT_Summary_Report');
  };

  const handleExportCSV = () => {
    if (!report) return;
    
    const data = formatDataForExport({
      'Period': `${report.period_start} to ${report.period_end}`,
      'Generated': new Date(report.generated_at).toLocaleString(),
      'Filing Deadline': report.filing_deadline,
      'Compliance Status': report.compliance_status,
      'Total Sales': report.output_taxable_amount,
      'VAT Collected': report.output_vat_total,
      'Total Purchases': report.input_taxable_amount,
      'VAT Paid': report.input_vat_total,
      'Net VAT Payable': report.net_vat_payable,
      'Net VAT Refundable': report.net_vat_refundable,
    });
    
    exportToCSV(data, 'VAT_Summary_Report');
  };

  const formatCurrency = (amount: number) => {
    return `KES ${amount.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  };

  const getComplianceColor = (status: string) => {
    switch (status) {
      case 'compliant':
        return 'text-green-600 bg-green-50';
      case 'warning':
        return 'text-yellow-600 bg-yellow-50';
      case 'overdue':
        return 'text-red-600 bg-red-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  // Prepare chart data for VAT by rate
  const prepareVATByRateChart = () => {
    if (!report) return null;

    const labels: string[] = [];
    const outputData: number[] = [];
    const inputData: number[] = [];

    // Combine all unique rates
    const allRates = new Set([
      ...report.output_by_rate.map(r => r.rate),
      ...report.input_by_rate.map(r => r.rate)
    ]);

    allRates.forEach(rate => {
      labels.push(`${rate}%`);
      const outputItem = report.output_by_rate.find(r => r.rate === rate);
      const inputItem = report.input_by_rate.find(r => r.rate === rate);
      outputData.push(outputItem ? outputItem.vat_amount : 0);
      inputData.push(inputItem ? inputItem.vat_amount : 0);
    });

    return prepareChartData(labels, [
      {
        label: 'Output VAT (Sales)',
        data: outputData,
        backgroundColor: 'rgba(16, 185, 129, 0.8)',
        borderColor: 'rgba(16, 185, 129, 1)',
      },
      {
        label: 'Input VAT (Purchases)',
        data: inputData,
        backgroundColor: 'rgba(239, 68, 68, 0.8)',
        borderColor: 'rgba(239, 68, 68, 1)',
      }
    ]);
  };

  // Prepare net position chart
  const prepareNetPositionChart = () => {
    if (!report) return null;

    const labels = ['VAT Collected', 'VAT Paid', 'Net Payable'];
    const data = [report.output_vat_total, report.input_vat_total, report.net_vat_payable];

    return prepareChartData(labels, [{
      label: 'Amount (KES)',
      data: data,
      backgroundColor: [
        'rgba(16, 185, 129, 0.8)',
        'rgba(239, 68, 68, 0.8)',
        'rgba(59, 130, 246, 0.8)'
      ],
      borderColor: [
        'rgba(16, 185, 129, 1)',
        'rgba(239, 68, 68, 1)',
        'rgba(59, 130, 246, 1)'
      ],
    }]);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <Link href="/reports" className="text-blue-600 hover:text-blue-800 mb-4 inline-block">
            ← Back to Reports
          </Link>
          <h1 className="text-3xl font-bold text-gray-900">Tax & VAT Summary</h1>
          <p className="mt-2 text-gray-600">
            Comprehensive VAT report for tax filing and compliance
          </p>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Start Date
              </label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                End Date
              </label>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Include Transactions
              </label>
              <div className="flex items-center h-10">
                <input
                  type="checkbox"
                  checked={includeTransactions}
                  onChange={(e) => setIncludeTransactions(e.target.checked)}
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <label className="ml-2 text-sm text-gray-600">
                  Show detailed transactions
                </label>
              </div>
            </div>
          </div>

          <div className="mt-4 flex flex-wrap gap-3">
            <button
              onClick={fetchReport}
              disabled={loading}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? 'Generating...' : 'Generate Report'}
            </button>
            
            {report && (
              <>
                <button
                  onClick={handleExportExcel}
                  className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                >
                  📊 Export Excel
                </button>
                
                <button
                  onClick={handleExportCSV}
                  className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                >
                  📄 Export CSV
                </button>
              </>
            )}
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <p className="mt-4 text-gray-600">Generating VAT report...</p>
          </div>
        )}

        {/* Report Content */}
        {!loading && report && (
          <>
            {/* Compliance Status Banner */}
            <div className={`rounded-lg p-6 mb-6 ${getComplianceColor(report.compliance_status)}`}>
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold mb-1">
                    Compliance Status: {report.compliance_status.toUpperCase()}
                  </h3>
                  <p className="text-sm">
                    Filing Deadline: {report.filing_deadline}
                  </p>
                  {report.penalties_applicable && (
                    <p className="text-sm font-semibold mt-1">
                      ⚠️ Penalties may be applicable for late filing
                    </p>
                  )}
                </div>
                <div className="text-right">
                  <p className="text-sm">Period</p>
                  <p className="font-semibold">{report.period_start} to {report.period_end}</p>
                </div>
              </div>
            </div>

            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
              {/* Output VAT (Sales) */}
              <div className="bg-gradient-to-br from-green-500 to-green-600 text-white rounded-lg shadow-lg p-6">
                <h3 className="text-lg font-semibold mb-2">Output VAT (Sales)</h3>
                <p className="text-3xl font-bold mb-2">{formatCurrency(report.output_vat_total)}</p>
                <p className="text-sm opacity-90">
                  Sales: {formatCurrency(report.output_taxable_amount)}
                </p>
                <p className="text-sm opacity-90">
                  {report.output_transaction_count} transactions
                </p>
              </div>

              {/* Input VAT (Purchases) */}
              <div className="bg-gradient-to-br from-red-500 to-red-600 text-white rounded-lg shadow-lg p-6">
                <h3 className="text-lg font-semibold mb-2">Input VAT (Purchases)</h3>
                <p className="text-3xl font-bold mb-2">{formatCurrency(report.input_vat_total)}</p>
                <p className="text-sm opacity-90">
                  Purchases: {formatCurrency(report.input_taxable_amount)}
                </p>
                <p className="text-sm opacity-90">
                  {report.input_transaction_count} transactions
                </p>
              </div>

              {/* Net Position */}
              <div className="bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-lg shadow-lg p-6">
                <h3 className="text-lg font-semibold mb-2">Net VAT Position</h3>
                {report.net_vat_payable > 0 ? (
                  <>
                    <p className="text-3xl font-bold mb-2">{formatCurrency(report.net_vat_payable)}</p>
                    <p className="text-sm opacity-90">Amount Payable to Tax Authority</p>
                  </>
                ) : (
                  <>
                    <p className="text-3xl font-bold mb-2">{formatCurrency(report.net_vat_refundable)}</p>
                    <p className="text-sm opacity-90">Amount Reclaimable</p>
                  </>
                )}
              </div>
            </div>

            {/* Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
              {/* VAT by Rate Chart */}
              {prepareVATByRateChart() && (
                <div className="bg-white rounded-lg shadow-md p-6">
                  <h3 className="text-xl font-semibold mb-4">VAT by Rate</h3>
                  <ReportChart
                    type="bar"
                    data={prepareVATByRateChart()!}
                    title="VAT Amount by Tax Rate"
                  />
                </div>
              )}

              {/* Net Position Chart */}
              {prepareNetPositionChart() && (
                <div className="bg-white rounded-lg shadow-md p-6">
                  <h3 className="text-xl font-semibold mb-4">VAT Position</h3>
                  <ReportChart
                    type="bar"
                    data={prepareNetPositionChart()!}
                    title="VAT Collected vs Paid"
                  />
                </div>
              )}
            </div>

            {/* VAT Breakdown by Rate Tables */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
              {/* Output VAT by Rate */}
              {report.output_by_rate.length > 0 && (
                <div className="bg-white rounded-lg shadow-md p-6">
                  <h3 className="text-xl font-semibold mb-4">Output VAT by Rate (Sales)</h3>
                  <div className="overflow-x-auto">
                    <table className="min-w-full">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-4 py-2 text-left text-sm font-semibold text-gray-700">Rate</th>
                          <th className="px-4 py-2 text-right text-sm font-semibold text-gray-700">Taxable Amount</th>
                          <th className="px-4 py-2 text-right text-sm font-semibold text-gray-700">VAT Amount</th>
                          <th className="px-4 py-2 text-right text-sm font-semibold text-gray-700">Count</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-200">
                        {report.output_by_rate.map((item, idx) => (
                          <tr key={idx} className="hover:bg-gray-50">
                            <td className="px-4 py-2 text-sm">{item.rate}%</td>
                            <td className="px-4 py-2 text-sm text-right">{formatCurrency(item.taxable_amount)}</td>
                            <td className="px-4 py-2 text-sm text-right font-semibold">{formatCurrency(item.vat_amount)}</td>
                            <td className="px-4 py-2 text-sm text-right">{item.transaction_count}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Input VAT by Rate */}
              {report.input_by_rate.length > 0 && (
                <div className="bg-white rounded-lg shadow-md p-6">
                  <h3 className="text-xl font-semibold mb-4">Input VAT by Rate (Purchases)</h3>
                  <div className="overflow-x-auto">
                    <table className="min-w-full">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-4 py-2 text-left text-sm font-semibold text-gray-700">Rate</th>
                          <th className="px-4 py-2 text-right text-sm font-semibold text-gray-700">Taxable Amount</th>
                          <th className="px-4 py-2 text-right text-sm font-semibold text-gray-700">VAT Amount</th>
                          <th className="px-4 py-2 text-right text-sm font-semibold text-gray-700">Count</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-200">
                        {report.input_by_rate.map((item, idx) => (
                          <tr key={idx} className="hover:bg-gray-50">
                            <td className="px-4 py-2 text-sm">{item.rate}%</td>
                            <td className="px-4 py-2 text-sm text-right">{formatCurrency(item.taxable_amount)}</td>
                            <td className="px-4 py-2 text-sm text-right font-semibold">{formatCurrency(item.vat_amount)}</td>
                            <td className="px-4 py-2 text-sm text-right">{item.transaction_count}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>

            {/* Detailed Transactions */}
            {includeTransactions && (
              <>
                {/* Output Transactions (Sales) */}
                {report.output_transactions.length > 0 && (
                  <div className="bg-white rounded-lg shadow-md p-6 mb-6">
                    <h3 className="text-xl font-semibold mb-4">Sales Transactions (Output VAT)</h3>
                    <div className="overflow-x-auto">
                      <table className="min-w-full">
                        <thead className="bg-gray-50">
                          <tr>
                            <th className="px-4 py-2 text-left text-sm font-semibold text-gray-700">Date</th>
                            <th className="px-4 py-2 text-left text-sm font-semibold text-gray-700">Description</th>
                            <th className="px-4 py-2 text-right text-sm font-semibold text-gray-700">Amount</th>
                            <th className="px-4 py-2 text-right text-sm font-semibold text-gray-700">VAT Rate</th>
                            <th className="px-4 py-2 text-right text-sm font-semibold text-gray-700">VAT Amount</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200">
                          {report.output_transactions.map((txn, idx) => (
                            <tr key={idx} className="hover:bg-gray-50">
                              <td className="px-4 py-2 text-sm">{txn.date}</td>
                              <td className="px-4 py-2 text-sm">{txn.description}</td>
                              <td className="px-4 py-2 text-sm text-right">{formatCurrency(txn.amount)}</td>
                              <td className="px-4 py-2 text-sm text-right">{txn.vat_rate}%</td>
                              <td className="px-4 py-2 text-sm text-right font-semibold">{formatCurrency(txn.vat_amount)}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}

                {/* Input Transactions (Purchases) */}
                {report.input_transactions.length > 0 && (
                  <div className="bg-white rounded-lg shadow-md p-6 mb-6">
                    <h3 className="text-xl font-semibold mb-4">Purchase Transactions (Input VAT)</h3>
                    <div className="overflow-x-auto">
                      <table className="min-w-full">
                        <thead className="bg-gray-50">
                          <tr>
                            <th className="px-4 py-2 text-left text-sm font-semibold text-gray-700">Date</th>
                            <th className="px-4 py-2 text-left text-sm font-semibold text-gray-700">Description</th>
                            <th className="px-4 py-2 text-right text-sm font-semibold text-gray-700">Amount</th>
                            <th className="px-4 py-2 text-right text-sm font-semibold text-gray-700">VAT Rate</th>
                            <th className="px-4 py-2 text-right text-sm font-semibold text-gray-700">VAT Amount</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200">
                          {report.input_transactions.map((txn, idx) => (
                            <tr key={idx} className="hover:bg-gray-50">
                              <td className="px-4 py-2 text-sm">{txn.date}</td>
                              <td className="px-4 py-2 text-sm">{txn.description}</td>
                              <td className="px-4 py-2 text-sm text-right">{formatCurrency(txn.amount)}</td>
                              <td className="px-4 py-2 text-sm text-right">{txn.vat_rate}%</td>
                              <td className="px-4 py-2 text-sm text-right font-semibold">{formatCurrency(txn.vat_amount)}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
              </>
            )}

            {/* Report Footer */}
            <div className="bg-gray-50 rounded-lg p-6 mt-6">
              <p className="text-sm text-gray-600">
                Report generated on {new Date(report.generated_at).toLocaleString()}
              </p>
              <p className="text-xs text-gray-500 mt-2">
                * This report is for informational purposes. Please verify with your tax advisor before filing.
              </p>
            </div>
          </>
        )}
      </main>
    </div>
  );
}
