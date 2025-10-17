'use client';

import { useEffect, useRef } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  ArcElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
  ChartOptions,
  ChartData,
} from 'chart.js';
import { Bar, Line, Pie, Doughnut } from 'react-chartjs-2';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  ArcElement,
  PointElement,
  Title,
  Tooltip,
  Legend
);

interface ChartProps {
  type: 'bar' | 'line' | 'pie' | 'doughnut';
  data: ChartData<any>;
  options?: ChartOptions<any>;
  height?: number;
  title?: string;
}

export default function ReportChart({ type, data, options, height = 300, title }: ChartProps) {
  const defaultOptions: ChartOptions<any> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          padding: 15,
          font: {
            size: 12,
            family: 'Inter, sans-serif',
          },
          // Filter out empty labels for doughnut/pie charts
          filter: function(item: any) {
            return item.text !== '' && item.text !== undefined && item.text !== null;
          }
        },
      },
      title: {
        display: !!title,
        text: title,
        font: {
          size: 16,
          weight: 'bold',
          family: 'Inter, sans-serif',
        },
        padding: 20,
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        padding: 12,
        titleFont: {
          size: 14,
          weight: 'bold',
        },
        bodyFont: {
          size: 13,
        },
        cornerRadius: 8,
        callbacks: {
          label: function(context: any) {
            // For doughnut/pie charts, use the label instead of dataset.label
            let label = context.label || '';
            
            if (label) {
              label += ': ';
            }
            
            // Get the value
            const value = context.parsed || context.parsed.y || context.raw;
            
            if (value !== null && value !== undefined) {
              // Format as currency if the value is large
              if (Math.abs(value) >= 1000) {
                label += new Intl.NumberFormat('en-KE', {
                  style: 'currency',
                  currency: 'KES',
                  minimumFractionDigits: 0,
                  maximumFractionDigits: 0,
                }).format(value);
              } else {
                label += value;
              }
            }
            return label;
          }
        }
      },
    },
    ...(type === 'bar' || type === 'line' ? {
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: function(value: any) {
              // Format large numbers as K, M
              if (Math.abs(value) >= 1000000) {
                return 'KES ' + (value / 1000000).toFixed(1) + 'M';
              } else if (Math.abs(value) >= 1000) {
                return 'KES ' + (value / 1000).toFixed(0) + 'K';
              }
              return 'KES ' + value;
            },
            font: {
              size: 11,
            },
          },
          grid: {
            color: 'rgba(0, 0, 0, 0.05)',
          },
        },
        x: {
          ticks: {
            font: {
              size: 11,
            },
          },
          grid: {
            display: false,
          },
        },
      },
    } : {}),
  };

  const mergedOptions = {
    ...defaultOptions,
    ...options,
    plugins: {
      ...defaultOptions.plugins,
      ...(options?.plugins || {}),
    },
  };

  const renderChart = () => {
    switch (type) {
      case 'bar':
        return <Bar data={data} options={mergedOptions} height={height} />;
      case 'line':
        return <Line data={data} options={mergedOptions} height={height} />;
      case 'pie':
        return <Pie data={data} options={mergedOptions} height={height} />;
      case 'doughnut':
        return <Doughnut data={data} options={mergedOptions} height={height} />;
      default:
        return null;
    }
  };

  return (
    <div style={{ height: `${height}px`, position: 'relative' }}>
      {renderChart()}
    </div>
  );
}

// Utility function to generate color palette
export const generateColors = (count: number, opacity: number = 1): string[] => {
  const colors = [
    `rgba(59, 130, 246, ${opacity})`,   // Blue
    `rgba(16, 185, 129, ${opacity})`,   // Green
    `rgba(239, 68, 68, ${opacity})`,    // Red
    `rgba(245, 158, 11, ${opacity})`,   // Orange
    `rgba(139, 92, 246, ${opacity})`,   // Purple
    `rgba(236, 72, 153, ${opacity})`,   // Pink
    `rgba(20, 184, 166, ${opacity})`,   // Teal
    `rgba(251, 146, 60, ${opacity})`,   // Amber
    `rgba(168, 85, 247, ${opacity})`,   // Violet
    `rgba(34, 197, 94, ${opacity})`,    // Emerald
    `rgba(248, 113, 113, ${opacity})`,  // Rose
  ];
  
  // Repeat colors if needed
  const result: string[] = [];
  for (let i = 0; i < count; i++) {
    result.push(colors[i % colors.length]);
  }
  return result;
};

// Utility function to prepare chart data
export const prepareChartData = (
  labels: string[],
  datasets: Array<{
    label: string;
    data: number[];
    backgroundColor?: string | string[];
    borderColor?: string | string[];
    borderWidth?: number;
  }>
): ChartData<any> => {
  return {
    labels,
    datasets: datasets.map((dataset, index) => ({
      ...dataset,
      backgroundColor: dataset.backgroundColor || generateColors(labels.length, 0.8),
      borderColor: dataset.borderColor || generateColors(labels.length, 1),
      borderWidth: dataset.borderWidth || 1,
    })),
  };
};
