"use client";

import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { jsPDF } from "jspdf";

const invoice = {
  number: "INV-2024-002",
  client: "Creative Designs Agency",
  issueDate: "2024-07-15",
  dueDate: "2024-08-14",
  amount: "KES 8,500",
  status: "Unpaid",
  items: [{ item: "Logo Design", quantity: 1, price: 8500, amount: 8500 }],
  notes: "Please pay by the due date.",
};

export default function CustomerInvoicePage() {
  const { id } = useParams();
  const router = useRouter();

  const decodedId = decodeURIComponent(id as string);
  if (decodedId !== invoice.number) {
    return (
      <div className="p-8 text-red-600">
        Invoice not found.
        <Link href="/customers" className="mt-4 block underline text-blue-600">
          ← Go Back to Customers
        </Link>
      </div>
    );
  }

  const handleDownload = () => {
    const doc = new jsPDF();
    doc.setFontSize(14);
    doc.text("Invoice #" + invoice.number, 10, 20);
    doc.text("Client: " + invoice.client, 10, 30);
    doc.text("Issue Date: " + invoice.issueDate, 10, 40);
    doc.text("Due Date: " + invoice.dueDate, 10, 50);
    doc.text("Amount: " + invoice.amount, 10, 60);
    doc.text("Status: " + invoice.status, 10, 70);
    let y = 90;
    invoice.items.forEach((item) => {
      doc.text(
        `${item.item} | Qty: ${item.quantity} | Price: KES ${item.price}`,
        10,
        y
      );
      y += 10;
    });
    doc.save(`${invoice.number}.pdf`);
  };

  return (
    <div className="max-w-3xl mx-auto p-8">
      {/* Back to Customers */}
      <Link
        href="/customers"
        className="mb-4 inline-block text-blue-600 underline"
      >
        ← Back to Customers
      </Link>

      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold">Invoice #{invoice.number}</h1>
          <p className="text-gray-600">Client: {invoice.client}</p>
        </div>
        <button
          onClick={handleDownload}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          Download PDF
        </button>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-6">
        <div>
          <p className="font-semibold">Issue Date</p>
          <p>{invoice.issueDate}</p>
        </div>
        <div>
          <p className="font-semibold">Due Date</p>
          <p>{invoice.dueDate}</p>
        </div>
        <div>
          <p className="font-semibold">Amount</p>
          <p>{invoice.amount}</p>
        </div>
        <div>
          <p className="font-semibold">Status</p>
          <p
            className={`${
              invoice.status === "Paid"
                ? "text-green-600"
                : "text-yellow-600 font-medium"
            }`}
          >
            {invoice.status}
          </p>
        </div>
      </div>

      <h3 className="font-semibold mb-2">Items</h3>
      <table className="w-full text-sm border mb-6">
        <thead className="bg-gray-50">
          <tr>
            <th className="p-2 text-left">Item</th>
            <th className="p-2 text-left">Quantity</th>
            <th className="p-2 text-left">Price</th>
            <th className="p-2 text-left">Amount</th>
          </tr>
        </thead>
        <tbody>
          {invoice.items.map((item, idx) => (
            <tr key={idx} className="border-t">
              <td className="p-2">{item.item}</td>
              <td className="p-2">{item.quantity}</td>
              <td className="p-2">KES {item.price.toLocaleString()}</td>
              <td className="p-2">KES {item.amount.toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {invoice.status !== "Paid" && (
        <div className="mt-6">
          <h4 className="font-semibold mb-2">Payment Instructions</h4>
          <p className="mb-2">
            Use our M-Pesa Paybill 123456. 
            Account Number: <strong>{invoice.number}</strong>
          </p>
          <button className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700">
            Pay Now
          </button>
        </div>
      )}
    </div>
  );
}
