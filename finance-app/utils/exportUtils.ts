import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import * as XLSX from 'xlsx';
import Papa from 'papaparse';

// Export to PDF
export const exportToPDF = (
  title: string,
  data: any[],
  columns: string[],
  filename: string = 'report.pdf'
) => {
  const doc = new jsPDF();
  
  // Add title
  doc.setFontSize(18);
  doc.setFont('helvetica', 'bold');
  doc.text(title, 14, 20);
  
  // Add metadata
  doc.setFontSize(10);
  doc.setFont('helvetica', 'normal');
  doc.text(`Generated: ${new Date().toLocaleString()}`, 14, 30);
  
  // Prepare table data
  const tableData = data.map(row => 
    columns.map(col => {
      const value = row[col];
      // Format currency values
      if (typeof value === 'number' && Math.abs(value) >= 100) {
        return new Intl.NumberFormat('en-KE', {
          style: 'currency',
          currency: 'KES',
          minimumFractionDigits: 0,
          maximumFractionDigits: 0,
        }).format(value);
      }
      return value?.toString() || '';
    })
  );
  
  // Add table
  autoTable(doc, {
    head: [columns.map(col => col.replace(/_/g, ' ').toUpperCase())],
    body: tableData,
    startY: 40,
    theme: 'striped',
    headStyles: {
      fillColor: [59, 130, 246], // Blue
      textColor: 255,
      fontStyle: 'bold',
      fontSize: 11,
    },
    bodyStyles: {
      fontSize: 10,
    },
    alternateRowStyles: {
      fillColor: [245, 247, 250],
    },
    margin: { top: 40, left: 14, right: 14 },
  });
  
  // Save PDF
  doc.save(filename);
};

// Export to Excel
export const exportToExcel = (
  data: any[],
  sheetName: string = 'Report',
  filename: string = 'report.xlsx'
) => {
  // Create worksheet
  const ws = XLSX.utils.json_to_sheet(data);
  
  // Create workbook
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, sheetName);
  
  // Add metadata
  const metadata = {
    'Generated At': new Date().toLocaleString(),
    'Report Name': sheetName,
  };
  
  // Write file
  XLSX.writeFile(wb, filename);
};

// Export to CSV
export const exportToCSV = (
  data: any[],
  filename: string = 'report.csv'
) => {
  const csv = Papa.unparse(data);
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  
  if (link.download !== undefined) {
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }
};

// Format data for export (flatten nested objects)
export const formatDataForExport = (data: any, prefix: string = ''): any => {
  const result: any = {};
  
  for (const key in data) {
    if (data.hasOwnProperty(key)) {
      const value = data[key];
      const newKey = prefix ? `${prefix}_${key}` : key;
      
      if (value === null || value === undefined) {
        result[newKey] = '';
      } else if (typeof value === 'object' && !Array.isArray(value)) {
        // Recursively flatten nested objects
        Object.assign(result, formatDataForExport(value, newKey));
      } else if (Array.isArray(value)) {
        // Convert arrays to comma-separated strings
        result[newKey] = value.join(', ');
      } else {
        result[newKey] = value;
      }
    }
  }
  
  return result;
};

// Export Income Statement to PDF
export const exportIncomeStatementPDF = (report: any) => {
  const doc = new jsPDF();
  
  // Title
  doc.setFontSize(20);
  doc.setFont('helvetica', 'bold');
  doc.text('Income Statement', 14, 20);
  
  // Period
  doc.setFontSize(12);
  doc.setFont('helvetica', 'normal');
  doc.text(`Period: ${report.period_start} to ${report.period_end}`, 14, 30);
  doc.text(`Generated: ${new Date(report.generated_at).toLocaleString()}`, 14, 37);
  
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-KE', {
      style: 'currency',
      currency: 'KES',
      minimumFractionDigits: 2,
    }).format(amount);
  };
  
  let yPos = 50;
  
  // Revenue Section
  doc.setFontSize(14);
  doc.setFont('helvetica', 'bold');
  doc.text('Revenue', 14, yPos);
  yPos += 8;
  
  doc.setFontSize(11);
  doc.setFont('helvetica', 'normal');
  doc.text(`Total Invoiced: ${formatCurrency(report.revenue.invoiced_amount)}`, 20, yPos);
  yPos += 6;
  doc.text(`Paid Amount: ${formatCurrency(report.revenue.paid_amount)}`, 20, yPos);
  yPos += 6;
  doc.text(`Pending Amount: ${formatCurrency(report.revenue.pending_amount)}`, 20, yPos);
  yPos += 8;
  
  doc.setFont('helvetica', 'bold');
  doc.text(`Total Revenue: ${formatCurrency(report.revenue.total_revenue)}`, 20, yPos);
  yPos += 15;
  
  // Expenses Section
  doc.setFontSize(14);
  doc.text('Expenses', 14, yPos);
  yPos += 8;
  
  doc.setFontSize(11);
  doc.setFont('helvetica', 'normal');
  
  report.expenses.top_categories.forEach((cat: any) => {
    doc.text(`${cat.category}: ${formatCurrency(cat.amount)} (${cat.percentage}%)`, 20, yPos);
    yPos += 6;
  });
  
  yPos += 4;
  doc.setFont('helvetica', 'bold');
  doc.text(`Total Expenses: ${formatCurrency(report.expenses.total_expenses)}`, 20, yPos);
  yPos += 15;
  
  // Bottom Line
  doc.setFontSize(14);
  doc.text('Summary', 14, yPos);
  yPos += 8;
  
  doc.setFontSize(11);
  doc.setFont('helvetica', 'normal');
  doc.text(`Gross Profit: ${formatCurrency(report.gross_profit)}`, 20, yPos);
  yPos += 8;
  
  doc.setFontSize(12);
  doc.setFont('helvetica', 'bold');
  const netIncomeColor: [number, number, number] = report.net_income >= 0 ? [0, 128, 0] : [255, 0, 0];
  doc.setTextColor(...netIncomeColor);
  doc.text(`Net Income: ${formatCurrency(report.net_income)}`, 20, yPos);
  yPos += 6;
  doc.text(`Profit Margin: ${report.profit_margin}%`, 20, yPos);
  
  doc.save(`income_statement_${report.period_start}_${report.period_end}.pdf`);
};

// Export Cash Flow to PDF
export const exportCashFlowPDF = (report: any) => {
  const doc = new jsPDF();
  
  doc.setFontSize(20);
  doc.setFont('helvetica', 'bold');
  doc.text('Cash Flow Statement', 14, 20);
  
  doc.setFontSize(12);
  doc.setFont('helvetica', 'normal');
  doc.text(`Period: ${report.period_start} to ${report.period_end}`, 14, 30);
  doc.text(`Generated: ${new Date(report.generated_at).toLocaleString()}`, 14, 37);
  
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-KE', {
      style: 'currency',
      currency: 'KES',
      minimumFractionDigits: 2,
    }).format(amount);
  };
  
  let yPos = 50;
  
  // Opening Balance
  doc.setFontSize(11);
  doc.text(`Opening Balance: ${formatCurrency(report.opening_balance)}`, 14, yPos);
  yPos += 10;
  
  // Inflows
  doc.setFontSize(14);
  doc.setFont('helvetica', 'bold');
  doc.setTextColor(0, 128, 0);
  doc.text(`+ Cash Inflows: ${formatCurrency(report.inflows.total_inflows)}`, 14, yPos);
  yPos += 8;
  
  doc.setFontSize(11);
  doc.setFont('helvetica', 'normal');
  doc.setTextColor(0, 0, 0);
  doc.text(`Customer Payments: ${formatCurrency(report.inflows.customer_payments)}`, 20, yPos);
  yPos += 15;
  
  // Outflows
  doc.setFontSize(14);
  doc.setFont('helvetica', 'bold');
  doc.setTextColor(255, 0, 0);
  doc.text(`- Cash Outflows: ${formatCurrency(report.outflows.total_outflows)}`, 14, yPos);
  yPos += 8;
  
  doc.setFontSize(11);
  doc.setFont('helvetica', 'normal');
  doc.setTextColor(0, 0, 0);
  
  Object.entries(report.outflows.by_category).forEach(([category, amount]: [string, any]) => {
    doc.text(`${category}: ${formatCurrency(amount)}`, 20, yPos);
    yPos += 6;
  });
  
  yPos += 8;
  
  // Net Cash Flow
  doc.setFontSize(14);
  doc.setFont('helvetica', 'bold');
  const netColor: [number, number, number] = report.net_cash_flow >= 0 ? [0, 128, 0] : [255, 0, 0];
  doc.setTextColor(...netColor);
  doc.text(`Net Cash Flow: ${formatCurrency(report.net_cash_flow)}`, 14, yPos);
  yPos += 8;
  
  doc.setTextColor(0, 0, 0);
  doc.text(`Closing Balance: ${formatCurrency(report.closing_balance)}`, 14, yPos);
  
  doc.save(`cash_flow_${report.period_start}_${report.period_end}.pdf`);
};

// Export Dashboard Metrics to Excel
export const exportDashboardMetricsExcel = (metrics: any) => {
  const data = [
    { Metric: 'Total Revenue', Value: metrics.total_revenue, Category: 'Revenue' },
    { Metric: 'Net Income', Value: metrics.net_income, Category: 'Revenue' },
    { Metric: 'Profit Margin', Value: `${metrics.profit_margin}%`, Category: 'Revenue' },
    { Metric: 'Total Invoices', Value: metrics.total_invoices, Category: 'Invoices' },
    { Metric: 'Paid Invoices', Value: metrics.paid_invoices, Category: 'Invoices' },
    { Metric: 'Pending Invoices', Value: metrics.pending_invoices, Category: 'Invoices' },
    { Metric: 'Overdue Invoices', Value: metrics.overdue_invoices, Category: 'Invoices' },
    { Metric: 'Collection Rate', Value: `${metrics.collection_rate}%`, Category: 'Collections' },
    { Metric: 'DSO', Value: `${metrics.dso} days`, Category: 'Collections' },
    { Metric: 'Total Outstanding', Value: metrics.total_outstanding, Category: 'Collections' },
    { Metric: 'Total Expenses', Value: metrics.total_expenses, Category: 'Expenses' },
    { Metric: 'Top Expense Category', Value: metrics.top_expense_category, Category: 'Expenses' },
    { Metric: 'Total Customers', Value: metrics.total_customers, Category: 'Customers' },
    { Metric: 'Active Customers', Value: metrics.active_customers, Category: 'Customers' },
    { Metric: 'Revenue per Customer', Value: metrics.revenue_per_customer, Category: 'Customers' },
  ];
  
  exportToExcel(data, 'Dashboard Metrics', 'dashboard_metrics.xlsx');
};
