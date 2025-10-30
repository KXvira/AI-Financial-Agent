import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import * as XLSX from 'xlsx';

interface Budget {
  id: string;
  category: string;
  subcategory?: string;
  amount: number;
  actual_spent: number;
  period_type: string;
  start_date: string;
  end_date: string;
  alert_threshold: number;
  description?: string;
  status: string;
  alert_level: string;
  created_at: string;
  updated_at: string;
}

interface BudgetSummary {
  total_budgets: number;
  total_budgeted: number;
  total_spent: number;
  total_remaining: number;
  average_utilization: number;
  budgets_exceeded: number;
  budgets_on_track: number;
  budgets_warning: number;
  budgets_critical: number;
}

export const exportBudgetsToPDF = (budgets: Budget[], summary: BudgetSummary | null) => {
  const doc = new jsPDF();
  
  // Title
  doc.setFontSize(20);
  doc.setTextColor(31, 41, 55); // gray-800
  doc.text('Budget Report', 14, 20);
  
  // Date
  doc.setFontSize(10);
  doc.setTextColor(107, 114, 128); // gray-500
  doc.text(`Generated: ${new Date().toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  })}`, 14, 28);
  
  // Summary Section
  if (summary) {
    doc.setFontSize(14);
    doc.setTextColor(31, 41, 55);
    doc.text('Summary Statistics', 14, 40);
    
    const summaryData = [
      ['Total Budgets', summary.total_budgets.toString()],
      ['Total Budgeted', `$${summary.total_budgeted.toLocaleString()}`],
      ['Total Spent', `$${summary.total_spent.toLocaleString()}`],
      ['Total Remaining', `$${summary.total_remaining.toLocaleString()}`],
      ['Average Utilization', `${summary.average_utilization.toFixed(1)}%`],
      ['On Track', summary.budgets_on_track.toString()],
      ['Warning', summary.budgets_warning.toString()],
      ['Critical', summary.budgets_critical.toString()],
      ['Exceeded', summary.budgets_exceeded.toString()]
    ];
    
    autoTable(doc, {
      startY: 45,
      head: [['Metric', 'Value']],
      body: summaryData,
      theme: 'grid',
      headStyles: { fillColor: [59, 130, 246] }, // blue-600
      styles: { fontSize: 9 },
      margin: { left: 14 }
    });
  }
  
  // Budget Details Table
  const startY = summary ? (doc as any).lastAutoTable.finalY + 15 : 45;
  
  doc.setFontSize(14);
  doc.setTextColor(31, 41, 55);
  doc.text('Budget Details', 14, startY);
  
  const tableData = budgets.map(budget => {
    const utilization = budget.amount > 0 ? (budget.actual_spent / budget.amount) * 100 : 0;
    const remaining = budget.amount - budget.actual_spent;
    
    return [
      budget.category,
      budget.subcategory || '-',
      `$${budget.amount.toLocaleString()}`,
      `$${budget.actual_spent.toLocaleString()}`,
      remaining >= 0 ? `$${remaining.toLocaleString()}` : `-$${Math.abs(remaining).toLocaleString()}`,
      `${utilization.toFixed(1)}%`,
      budget.alert_level === 'none' ? 'On Track' : budget.alert_level,
      budget.period_type,
      new Date(budget.start_date).toLocaleDateString(),
      new Date(budget.end_date).toLocaleDateString()
    ];
  });
  
  autoTable(doc, {
    startY: startY + 5,
    head: [['Category', 'Subcategory', 'Budgeted', 'Spent', 'Remaining', 'Usage', 'Status', 'Period', 'Start', 'End']],
    body: tableData,
    theme: 'striped',
    headStyles: { fillColor: [59, 130, 246] }, // blue-600
    styles: { fontSize: 8 },
    columnStyles: {
      0: { cellWidth: 25 },
      1: { cellWidth: 20 },
      2: { cellWidth: 20 },
      3: { cellWidth: 20 },
      4: { cellWidth: 20 },
      5: { cellWidth: 15 },
      6: { cellWidth: 18 },
      7: { cellWidth: 15 },
      8: { cellWidth: 18 },
      9: { cellWidth: 18 }
    },
    didParseCell: function(data) {
      // Color-code status column
      if (data.column.index === 6 && data.section === 'body') {
        const status = data.cell.text[0].toLowerCase();
        if (status === 'exceeded') {
          data.cell.styles.textColor = [239, 68, 68]; // red
          data.cell.styles.fontStyle = 'bold';
        } else if (status === 'critical') {
          data.cell.styles.textColor = [251, 146, 60]; // orange
          data.cell.styles.fontStyle = 'bold';
        } else if (status === 'warning') {
          data.cell.styles.textColor = [234, 179, 8]; // yellow
        } else {
          data.cell.styles.textColor = [34, 197, 94]; // green
        }
      }
    }
  });
  
  // Footer
  const pageCount = doc.getNumberOfPages();
  for (let i = 1; i <= pageCount; i++) {
    doc.setPage(i);
    doc.setFontSize(8);
    doc.setTextColor(156, 163, 175); // gray-400
    doc.text(
      `Page ${i} of ${pageCount}`,
      doc.internal.pageSize.getWidth() / 2,
      doc.internal.pageSize.getHeight() - 10,
      { align: 'center' }
    );
  }
  
  // Save the PDF
  doc.save(`budget-report-${new Date().toISOString().split('T')[0]}.pdf`);
};

export const exportBudgetsToExcel = (budgets: Budget[], summary: BudgetSummary | null) => {
  // Create workbook
  const wb = XLSX.utils.book_new();
  
  // Summary Sheet
  if (summary) {
    const summaryData = [
      ['Budget Report Summary'],
      ['Generated', new Date().toLocaleDateString()],
      [],
      ['Metric', 'Value'],
      ['Total Budgets', summary.total_budgets],
      ['Total Budgeted', summary.total_budgeted],
      ['Total Spent', summary.total_spent],
      ['Total Remaining', summary.total_remaining],
      ['Average Utilization (%)', summary.average_utilization.toFixed(1)],
      ['Budgets On Track', summary.budgets_on_track],
      ['Budgets Warning', summary.budgets_warning],
      ['Budgets Critical', summary.budgets_critical],
      ['Budgets Exceeded', summary.budgets_exceeded]
    ];
    
    const ws1 = XLSX.utils.aoa_to_sheet(summaryData);
    
    // Style the summary sheet
    ws1['!cols'] = [{ wch: 25 }, { wch: 20 }];
    
    XLSX.utils.book_append_sheet(wb, ws1, 'Summary');
  }
  
  // Budget Details Sheet
  const detailsData = budgets.map(budget => {
    const utilization = budget.amount > 0 ? (budget.actual_spent / budget.amount) * 100 : 0;
    const remaining = budget.amount - budget.actual_spent;
    
    return {
      'Category': budget.category,
      'Subcategory': budget.subcategory || '',
      'Budgeted Amount': budget.amount,
      'Actual Spent': budget.actual_spent,
      'Remaining': remaining,
      'Utilization (%)': parseFloat(utilization.toFixed(1)),
      'Alert Level': budget.alert_level === 'none' ? 'On Track' : budget.alert_level,
      'Status': budget.status,
      'Period Type': budget.period_type,
      'Start Date': new Date(budget.start_date).toLocaleDateString(),
      'End Date': new Date(budget.end_date).toLocaleDateString(),
      'Alert Threshold (%)': budget.alert_threshold,
      'Description': budget.description || ''
    };
  });
  
  const ws2 = XLSX.utils.json_to_sheet(detailsData);
  
  // Set column widths
  ws2['!cols'] = [
    { wch: 20 }, // Category
    { wch: 15 }, // Subcategory
    { wch: 15 }, // Budgeted Amount
    { wch: 15 }, // Actual Spent
    { wch: 15 }, // Remaining
    { wch: 15 }, // Utilization
    { wch: 15 }, // Alert Level
    { wch: 10 }, // Status
    { wch: 12 }, // Period Type
    { wch: 12 }, // Start Date
    { wch: 12 }, // End Date
    { wch: 18 }, // Alert Threshold
    { wch: 30 }  // Description
  ];
  
  XLSX.utils.book_append_sheet(wb, ws2, 'Budget Details');
  
  // Save the file
  XLSX.writeFile(wb, `budget-report-${new Date().toISOString().split('T')[0]}.xlsx`);
};

export const exportSingleBudgetToPDF = (budget: Budget) => {
  const doc = new jsPDF();
  
  // Title
  doc.setFontSize(20);
  doc.text(`Budget Report: ${budget.category}`, 14, 20);
  
  // Date
  doc.setFontSize(10);
  doc.setTextColor(107, 114, 128);
  doc.text(`Generated: ${new Date().toLocaleDateString()}`, 14, 28);
  
  // Budget Details
  doc.setFontSize(12);
  doc.setTextColor(31, 41, 55);
  doc.text('Budget Information', 14, 40);
  
  const utilization = budget.amount > 0 ? (budget.actual_spent / budget.amount) * 100 : 0;
  const remaining = budget.amount - budget.actual_spent;
  
  const details = [
    ['Category', budget.category],
    ['Subcategory', budget.subcategory || '-'],
    ['Budgeted Amount', `$${budget.amount.toLocaleString()}`],
    ['Actual Spent', `$${budget.actual_spent.toLocaleString()}`],
    ['Remaining', remaining >= 0 ? `$${remaining.toLocaleString()}` : `-$${Math.abs(remaining).toLocaleString()}`],
    ['Utilization', `${utilization.toFixed(1)}%`],
    ['Alert Level', budget.alert_level === 'none' ? 'On Track' : budget.alert_level],
    ['Status', budget.status],
    ['Period Type', budget.period_type],
    ['Start Date', new Date(budget.start_date).toLocaleDateString()],
    ['End Date', new Date(budget.end_date).toLocaleDateString()],
    ['Alert Threshold', `${budget.alert_threshold}%`],
    ['Description', budget.description || '-']
  ];
  
  autoTable(doc, {
    startY: 45,
    body: details,
    theme: 'plain',
    styles: { fontSize: 10 },
    columnStyles: {
      0: { fontStyle: 'bold', cellWidth: 50 },
      1: { cellWidth: 130 }
    }
  });
  
  doc.save(`budget-${budget.category.toLowerCase().replace(/\s+/g, '-')}-${new Date().toISOString().split('T')[0]}.pdf`);
};
