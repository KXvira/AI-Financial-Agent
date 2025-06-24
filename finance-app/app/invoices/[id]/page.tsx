// Here is a complete code of each  invoice detail 
"use client";

import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { jsPDF } from "jspdf";
import { useState } from "react";

type InvoiceItem = {
  item: string;
  quantity: number;
  price: number;
  amount: number;
};

type Payment = {
  method: string;
  date: string;
  transactionId: string;
} | null;

type Invoice = {
  number: string;
  client: string;
  issueDate: string;
  dueDate: string;
  amount: string;
  status: string;
  items: InvoiceItem[];
  notes: string;
  payment: Payment;
};

const mockInvoices: { [key: string]: Invoice } = {
  "INV-2024–001": {
    number: "INV-2024–001",
    client: "Tech Solutions Ltd",
    issueDate: "2024-07-20",
    dueDate: "2024-08-19",
    amount: "KES 15,000",
    status: "Paid",
    items: [{ item: "Website Design", quantity: 1, price: 15000, amount: 15000 }],
    notes: "Thanks for the business!",
    payment: {
      method: "Bank Transfer",
      date: "2024-07-21",
      transactionId: "PAY-2023-001",
    },
  },
  "INV-2024–002": {
    number: "INV-2024–002",
    client: "Creative Designs Agency",
    issueDate: "2024-07-15",
    dueDate: "2024-08-14",
    amount: "KES 8,500",
    status: "Unpaid",
    items: [{ item: "Logo Design", quantity: 1, price: 8500, amount: 8500 }],
    notes: "Please pay by the due date.",
    payment: null,
  },
};

export default function InvoiceDetailPage() {
  const params = useParams();
  const router = useRouter();
  const invoiceId = decodeURIComponent(params.id as string);
  const invoice = mockInvoices[invoiceId];

  const [invoiceData, setInvoiceData] = useState(invoice);
  const [paymentRef, setPaymentRef] = useState("");

  if (!invoiceData) {
    return (
      <div className="p-8">
        <h1 className="text-xl font-semibold text-red-500">Invoice not found</h1>
        <Link href="/invoices" className="text-blue-600 underline">Back to Invoices</Link>
      </div>
    );
  }

  const handleMarkAsPaid = () => {
    const newPayment = {
      method: "Manual Entry",
      date: new Date().toISOString().split("T")[0],
      transactionId: paymentRef || `TX-${Date.now()}`,
    };
    setInvoiceData({
      ...invoiceData,
      status: "Paid",
      payment: newPayment,
    });
  };

  const handleDelete = () => {
    alert("Invoice deleted");
    router.push("/invoices");
  };

  const generatePDF = () => {
    const doc = new jsPDF();
    doc.setFontSize(14);
    doc.text("Invoice #: " + invoiceData.number, 10, 20);
    doc.text("Client: " + invoiceData.client, 10, 30);
    doc.text("Status: " + (invoiceData.payment ? "Paid" : "Unpaid"), 10, 40);
    doc.text("Issue Date: " + invoiceData.issueDate, 10, 50);
    doc.text("Due Date: " + invoiceData.dueDate, 10, 60);
    doc.text("Amount: " + invoiceData.amount, 10, 70);

    let y = 90;
    invoiceData.items.forEach((item) => {
      doc.text(
        `${item.item} | Qty: ${item.quantity} | Price: KES ${item.price} | Amount: KES ${item.amount}`,
        10,
        y
      );
      y += 10;
    });

    if (invoiceData.notes) {
      doc.text("Notes: " + invoiceData.notes, 10, y + 10);
    }

    doc.save(`${invoiceData.number}.pdf`);
  };

  return (
    <div className="p-8 max-w-3xl mx-auto">
      <div className="flex justify-between items-center mb-4">
        <div>
          <h1 className="text-2xl font-bold">Invoice Details</h1>
          <p className="text-gray-600">Invoice #: {invoiceData.number}</p>
        </div>
        <button
          onClick={generatePDF}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          Download PDF
        </button>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-6">
        <div>
          <h2 className="font-semibold">Client</h2>
          <p>{invoiceData.client}</p>
        </div>
        <div>
          <h2 className="font-semibold">Status</h2>
          <p className={invoiceData.payment ? "text-green-600" : "text-red-600"}>
            {invoiceData.payment ? "Paid" : "Unpaid"}
          </p>
        </div>
        <div>
          <h2 className="font-semibold">Issue Date</h2>
          <p>{invoiceData.issueDate}</p>
        </div>
        <div>
          <h2 className="font-semibold">Due Date</h2>
          <p>{invoiceData.dueDate}</p>
        </div>
        <div>
          <h2 className="font-semibold">Total Amount</h2>
          <p>{invoiceData.amount}</p>
        </div>
      </div>

      <h3 className="font-semibold mb-2">Items</h3>
      <table className="w-full mb-6 text-sm border">
        <thead>
          <tr className="text-left bg-gray-100">
            <th className="p-2">Item</th>
            <th className="p-2">Quantity</th>
            <th className="p-2">Price</th>
            <th className="p-2">Amount</th>
          </tr>
        </thead>
        <tbody>
          {invoiceData.items.map((item, idx) => (
            <tr key={idx} className="border-t">
              <td className="p-2">{item.item}</td>
              <td className="p-2">{item.quantity}</td>
              <td className="p-2">KES {item.price.toLocaleString()}</td>
              <td className="p-2">KES {item.amount.toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {invoiceData.notes && (
        <div className="mb-6">
          <h3 className="font-semibold">Notes</h3>
          <p className="text-gray-700">{invoiceData.notes}</p>
        </div>
      )}

      {invoiceData.payment ? (
        <div>
          <h3 className="font-semibold mb-2">Payment Details</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p><span className="font-medium">Method:</span> {invoiceData.payment.method}</p>
              <p><span className="font-medium">Date:</span> {invoiceData.payment.date}</p>
            </div>
            <div>
              <p><span className="font-medium">Transaction ID:</span> {invoiceData.payment.transactionId}</p>
            </div>
          </div>
        </div>
      ) : (
        <div className="mt-6 flex items-center gap-4 max-w-xl">
          <input
            type="text"
            placeholder="Enter Payment Reference"
            value={paymentRef}
            onChange={(e) => setPaymentRef(e.target.value)}
            className="p-2 border rounded w-full max-w-md"
          />
          <button
            className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 whitespace-nowrap"
            onClick={handleMarkAsPaid}
          >
            Mark as Paid
          </button>
        </div>
      )}

      <div className="mt-8 flex justify-between items-center">
        <button
          onClick={() => router.back()}
          className="text-blue-600 hover:underline"
        >
          ← Back
        </button>
        <button
          onClick={handleDelete}
          className="text-red-600 border border-red-600 px-4 py-2 rounded hover:bg-red-50"
        >
          Delete Invoice
        </button>
      </div>
    </div>
  );
}
