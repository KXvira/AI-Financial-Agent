"use client";

import { useParams, useRouter } from "next/navigation";

const payments = [
  {
    reference: "PAY-2023-001",
    client: "Tech Solutions Ltd.",
    date: "2023-08-16",
    amount: "KES 50,000",
    method: "Bank Transfer",
    items: [
      { item: "Website Design", quantity: 1, price: 50000 },
    ],
  },
  {
    reference: "PAY-2023-002",
    client: "Global Imports Ltd.",
    date: "2023-08-26",
    amount: "KES 100,000",
    method: "Mobile Money",
    items: [
      { item: "Bulk Import Setup", quantity: 2, price: 50000 },
    ],
  },
  {
    reference: "PAY-2023-003",
    client: "Digital Marketing Agency",
    date: "2023-09-06",
    amount: "KES 85,000",
    method: "Bank Transfer",
    items: [
      { item: "SEO Optimization", quantity: 1, price: 85000 },
    ],
  },
  {
    reference: "PAY-2023-004",
    client: "Tech Solutions Ltd.",
    date: "2023-09-10",
    amount: "KES 75,000",
    method: "Mobile Money",
    items: [
      { item: "App Maintenance", quantity: 3, price: 25000 },
    ],
  },
  {
    reference: "PAY-2023-005",
    client: "Creative Designs Co.",
    date: "2023-09-15",
    amount: "KES 60,000",
    method: "Bank Transfer",
    items: [
      { item: "Logo Design", quantity: 1, price: 60000 },
    ],
  },
];

export default function PaymentDetailsPage() {
  const { reference } = useParams();
  const router = useRouter();
  const refStr = Array.isArray(reference) ? reference[0] : reference;

  const data = payments.find((p) => p.reference === refStr);

  const handleDelete = () => {
    if (confirm("Are you sure you want to delete this payment?")) {
      alert("Payment deleted.");
      router.push("/payments/list");
    }
  };

  if (!data) return <div className="p-8 text-red-500">Payment not found.</div>;

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Payment Details</h1>
        <div className="space-x-2">
          
          <button
            onClick={handleDelete}
            className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
          >
            Delete
          </button>
          <button
            onClick={() => router.back()}
            className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
          >
            Back
          </button>
        </div>
      </div>

      <div className="bg-white p-6 rounded shadow border mb-6">
        <h2 className="text-xl font-semibold mb-4">Summary</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <p><strong>Reference:</strong> {data.reference}</p>
          <p><strong>Client:</strong> {data.client}</p>
          <p><strong>Date:</strong> {data.date}</p>
          <p><strong>Amount:</strong> {data.amount}</p>
          <p><strong>Method:</strong> {data.method}</p>
        </div>
      </div>

      <div className="bg-white p-6 rounded shadow border">
        <h2 className="text-xl font-semibold mb-4">Items</h2>
        <table className="w-full text-sm text-left">
          <thead className="bg-gray-50 text-gray-600">
            <tr>
              <th className="p-2">Item</th>
              <th className="p-2">Quantity</th>
              <th className="p-2">Price</th>
              <th className="p-2">Total</th>
            </tr>
          </thead>
          <tbody>
            {data.items?.map((item, index) => (
              <tr key={index} className="border-t">
                <td className="p-2">{item.item}</td>
                <td className="p-2">{item.quantity}</td>
                <td className="p-2">KES {item.price.toLocaleString()}</td>
                <td className="p-2 font-medium">
                  KES {(item.quantity * item.price).toLocaleString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}