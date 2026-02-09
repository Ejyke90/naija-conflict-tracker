/**
 * Utility functions for exporting dashboard data to CSV and PDF
 */

interface DataRow {
  [key: string]: string | number | null | undefined;
}

/**
 * Convert array of objects to CSV string
 */
export function convertToCSV(data: DataRow[], filename: string = 'data'): void {
  if (!data || data.length === 0) {
    console.warn('No data to export');
    return;
  }

  // Get headers from first object
  const headers = Object.keys(data[0]);
  
  // Create CSV content
  const csvContent = [
    headers.join(','), // Header row
    ...data.map(row => 
      headers.map(header => {
        const value = row[header];
        // Escape values containing commas or quotes
        if (value === null || value === undefined) return '';
        const stringValue = String(value);
        if (stringValue.includes(',') || stringValue.includes('"')) {
          return `"${stringValue.replace(/"/g, '""')}"`;
        }
        return stringValue;
      }).join(',')
    )
  ].join('\n');

  // Create download link
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  
  link.setAttribute('href', url);
  link.setAttribute('download', `${filename}_${new Date().toISOString().split('T')[0]}.csv`);
  link.style.visibility = 'hidden';
  
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  
  URL.revokeObjectURL(url);
}

/**
 * Export chart data to CSV
 */
export function exportChartDataToCSV(
  chartData: any[],
  filename: string,
  columns?: string[]
): void {
  if (!chartData || chartData.length === 0) return;
  
  // If columns specified, filter the data
  const dataToExport = columns 
    ? chartData.map(row => {
        const filtered: DataRow = {};
        columns.forEach(col => {
          if (col in row) filtered[col] = row[col];
        });
        return filtered;
      })
    : chartData;
  
  convertToCSV(dataToExport, filename);
}

/**
 * Print current page/section
 */
export function printPage(): void {
  window.print();
}

/**
 * Generate PDF by triggering browser print dialog
 * (User can choose "Save as PDF" in print dialog)
 */
export function exportToPDF(): void {
  // Add print-specific styles
  document.body.classList.add('print-mode');
  
  window.print();
  
  // Remove print styles after print dialog closes
  setTimeout(() => {
    document.body.classList.remove('print-mode');
  }, 1000);
}

/**
 * Copy data to clipboard as tab-separated values (Excel-friendly)
 */
export function copyToClipboard(data: DataRow[]): Promise<void> {
  if (!data || data.length === 0) {
    return Promise.reject('No data to copy');
  }

  const headers = Object.keys(data[0]);
  const tsvContent = [
    headers.join('\t'),
    ...data.map(row => 
      headers.map(header => String(row[header] ?? '')).join('\t')
    )
  ].join('\n');

  return navigator.clipboard.writeText(tsvContent);
}
