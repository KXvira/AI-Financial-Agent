"use client";

import Link from "next/link";

const customerInvoices = [
  {
    number: "INV-2024-002",
    client: "Creative Designs Agency",
    amount: "KES 8,500",
    issueDate: "2024-07-15",
    dueDate: "2024-08-14",
    status: "Unpaid",
  },
  {
    number: "INV-2024-003",
    client: "Modern Tech Ltd",
    amount: "KES 12,000",
    issueDate: "2024-07-10",
    dueDate: "2024-08-10",
    status: "Paid",
  },
];

export default function CustomerDashboard() {
  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-6">Customer Invoices</h1>

      <div className="bg-white shadow-lg rounded-lg overflow-hidden">
        <table className="min-w-full text-sm">
          <thead className="bg-gray-100 text-gray-700">
            <tr>
              <th className="p-4 text-left">Invoice #</th>
              <th className="p-4 text-left">Client</th>
              <th className="p-4 text-left">Amount</th>
              <th className="p-4 text-left">Status</th>
              <th className="p-4 text-left">Action</th>
            </tr>
          </thead>
          <tbody>
            {customerInvoices.map((invoice) => (
              <tr key={invoice.number} className="hover:bg-gray-50 transition">
                <td className="p-4 font-medium text-blue-700">{invoice.number}</td>
                <td className="p-4">{invoice.client}</td>
                <td className="p-4">{invoice.amount}</td>
                <td className="p-4">
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-medium ${
                      invoice.status === "Paid"
                        ? "bg-green-100 text-green-800"
                        : "bg-yellow-100 text-yellow-800"
                    }`}
                  >
                    {invoice.status}
                  </span>
                </td>
                <td className="p-4">
                  <Link
                    href={{
                      pathname: `/customers/invoice/${invoice.number}`,
                      query: {
                        client: invoice.client,
                        amount: invoice.amount,
                        issueDate: invoice.issueDate,
                        dueDate: invoice.dueDate,
                        status: invoice.status,
                      },
                    }}
                    className="text-blue-600 underline hover:text-blue-800"
                  >
                    View Invoice
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

