// app/page.tsx
import StatCard from '../components/StatCard';
import Link from 'next/link';

const recentPayments = [
  { reference: 'PAY-2023-005', client: 'Creative Designs Co.', amount: 'KES 60,000', date: '2023-09-15' },
  { reference: 'PAY-2023-004', client: 'Tech Solutions Ltd.', amount: 'KES 75,000', date: '2023-09-10' },
  { reference: 'PAY-2023-003', client: 'Digital Marketing Agency', amount: 'KES 85,000', date: '2023-09-06' },
  { reference: 'PAY-2023-002', client: 'Global Imports Ltd.', amount: 'KES 100,000', date: '2023-08-26' },
  { reference: 'PAY-2023-001', client: 'Tech Solutions Ltd.', amount: 'KES 50,000', date: '2023-08-16' }
];

export default function Home() {
  return (
    <div>
      <h1 className="text-3xl font-bold mb-1">Dashboard</h1>
      <p className="text-sm text-gray-500 mb-6">Overview of your business finances</p>

      <div className=" grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <StatCard title="Total Invoices" amount="KES 120,000" change="10%" isPositive />
        <StatCard title="Payments Received" amount="KES 95,000" change="15%" isPositive />
        <StatCard title="Outstanding Balance" amount="KES 25,000" change="5%" isPositive={false} />
        <StatCard title="Daily Cash Flow" amount="KES 1,500" change="2%" isPositive />
      </div>

      {/* AI Insights Widget */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6 mb-6 border border-blue-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <svg className="h-5 w-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-800">AI Financial Insights</h3>
              <p className="text-sm text-gray-600">Get intelligent analysis of your financial data</p>
            </div>
          </div>
          <div className="flex space-x-2">
            <Link 
              href="/ai-insights"
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
            >
              Open AI Chat
            </Link>
          </div>
        </div>
        
        <div className="mt-4 grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="bg-white rounded-lg p-4 shadow-sm">
            <h4 className="font-medium text-gray-700 mb-2">💡 Quick Insights</h4>
            <p className="text-sm text-gray-600">Ask AI about your transaction patterns, cash flow, and financial health</p>
          </div>
          <div className="bg-white rounded-lg p-4 shadow-sm">
            <h4 className="font-medium text-gray-700 mb-2">📊 Smart Analysis</h4>
            <p className="text-sm text-gray-600">Get automated analysis of invoices, payments, and financial trends</p>
          </div>
          <div className="bg-white rounded-lg p-4 shadow-sm">
            <h4 className="font-medium text-gray-700 mb-2">🤖 AI Assistant</h4>
            <p className="text-sm text-gray-600">Chat with our AI to get answers about your financial data</p>
          </div>
        </div>
      </div>

      <div className="bg-white shadow-md rounded-lg p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Recent Payments</h2>
          <Link href="/payments/list" className="text-blue-600 hover:underline text-sm">
            View all
          </Link>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm text-left">
            <thead className="text-gray-500 bg-gray-50">
              <tr>
                <th className="px-4 py-2">Reference</th>
                <th className="px-4 py-2">Client</th>
                <th className="px-4 py-2">Amount</th>
                <th className="px-4 py-2">Date</th>
              </tr>
            </thead>
            <tbody>
              {recentPayments.map((payment) => (
                <tr key={payment.reference} className="hover:bg-gray-50 transition">
                  <td className="px-4 py-2 font-medium text-blue-600">
                    <Link href={`/payments/${payment.reference}`} className="hover:underline">
                      {payment.reference}
                    </Link>
                  </td>
                  <td className="px-4 py-2">{payment.client}</td>
                  <td className="px-4 py-2">{payment.amount}</td>
                  <td className="px-4 py-2">{payment.date}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}


