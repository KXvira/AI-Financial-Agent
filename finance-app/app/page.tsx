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


