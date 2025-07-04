// components/Chart.tsx
//This is just a placeholder component for the chart
// It can be replaced with a real chart library like Chart.js or Recharts

export default function Chart() {
    return (
      <div className="bg-white rounded-lg p-6 mt-6 shadow-sm">
        <h4 className="text-sm text-gray-600 mb-1">Daily Cash Flow</h4>
        <p className="text-2xl font-bold">KES 1,500</p>
        <p className="text-sm text-green-600 mb-4">Last 7 Days +2%</p>
        <div className="w-full h-40 bg-gray-100 rounded animate-pulse" />
      </div>
    );
  }
  