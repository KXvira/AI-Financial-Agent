// Here is a complete code of each  invoice detail 
"use client";

import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { jsPDF } from "jspdf";
import { useState, useEffect } from "react";
import SendInvoiceEmailModal from "@/components/SendInvoiceEmailModal";
import EmailHistory from "@/components/EmailHistory";
import { EmailSetupModal } from "@/components/EmailSetupModal";
import { checkEmailConfig } from "@/utils/checkEmailConfig";

type InvoiceItem = {
  description: string;
  quantity: number;
  unit_price: number;
  amount: number;
};

type Payment = {
  method: string;
  date: string;
  amount: number;
  transactionId: string;
};

type Invoice = {
  id: string;
  number: string;
  client: string;
  customerEmail: string;
  customerPhone: string;
  issueDate: string;
  dueDate: string;
  amount: number;
  currency: string;
  status: string;
  description: string;
  items: InvoiceItem[];
  payments: Payment[];
  notes: string;
};

export default function InvoiceDetailPage() {
  const params = useParams();
  const router = useRouter();
  const invoiceNumber = decodeURIComponent(params.id as string);

  const [invoiceData, setInvoiceData] = useState<Invoice | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [paymentRef, setPaymentRef] = useState("");
  const [showEmailModal, setShowEmailModal] = useState(false);
  const [showEmailSetup, setShowEmailSetup] = useState(false);

  useEffect(() => {
    const fetchInvoice = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await fetch(`http://localhost:8000/api/invoices/by-number/${encodeURIComponent(invoiceNumber)}`);
        
        if (!response.ok) {
          if (response.status === 404) {
            throw new Error("Invoice not found");
          }
          throw new Error("Failed to fetch invoice");
        }
        
        const data = await response.json();
        setInvoiceData(data);
      } catch (err) {
        console.error("Error fetching invoice:", err);
        setError(err instanceof Error ? err.message : "Failed to load invoice");
      } finally {
        setLoading(false);
      }
    };

    if (invoiceNumber) {
      fetchInvoice();
    }
  }, [invoiceNumber]);

  if (loading) {
    return (
      <div className="p-8">
        <p>Loading invoice...</p>
      </div>
    );
  }

  if (error || !invoiceData) {
    return (
      <div className="p-8">
        <h1 className="text-xl font-semibold text-red-500">{error || "Invoice not found"}</h1>
        <Link href="/invoices" className="text-blue-600 underline">Back to Invoices</Link>
      </div>
    );
  }

  const handleMarkAsPaid = () => {
    const newPayment: Payment = {
      method: "Manual Entry",
      date: new Date().toISOString().split("T")[0],
      amount: invoiceData.amount,
      transactionId: paymentRef || `TX-${Date.now()}`,
    };
    setInvoiceData({
      ...invoiceData,
      status: "Paid",
      payments: [...invoiceData.payments, newPayment],
    });
  };

  const handleDelete = () => {
    alert("Invoice deleted");
    router.push("/invoices");
  };

  const handleSendInvoice = async () => {
    // Check email configuration first
    const result = await checkEmailConfig();
    
    if (!result.isConfigured) {
      // Show setup modal if email not configured
      setShowEmailSetup(true);
      return;
    }
    
    // If configured, open the email modal
    setShowEmailModal(true);
  };

  const generatePDF = () => {
    const doc = new jsPDF();
    doc.setFontSize(14);
    doc.text("Invoice #: " + invoiceData.number, 10, 20);
    doc.text("Client: " + invoiceData.client, 10, 30);
    doc.text("Status: " + invoiceData.status, 10, 40);
    doc.text("Issue Date: " + invoiceData.issueDate, 10, 50);
    doc.text("Due Date: " + invoiceData.dueDate, 10, 60);
    doc.text(`Amount: ${invoiceData.currency} ${invoiceData.amount.toLocaleString()}`, 10, 70);

    let y = 90;
    if (invoiceData.items && invoiceData.items.length > 0) {
      invoiceData.items.forEach((item) => {
        doc.text(
          `${item.description} | Qty: ${item.quantity} | Price: ${invoiceData.currency} ${item.unit_price} | Amount: ${invoiceData.currency} ${item.amount}`,
          10,
          y
        );
        y += 10;
      });
    }

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
        <div className="flex gap-3">
          <button
            onClick={handleSendInvoice}
            className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 flex items-center gap-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
            Send Invoice
          </button>
          <button
            onClick={generatePDF}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            Download PDF
          </button>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-6">
        <div>
          <h2 className="font-semibold">Client</h2>
          <p>{invoiceData.client}</p>
          {invoiceData.customerEmail && <p className="text-sm text-gray-600">{invoiceData.customerEmail}</p>}
          {invoiceData.customerPhone && <p className="text-sm text-gray-600">{invoiceData.customerPhone}</p>}
        </div>
        <div>
          <h2 className="font-semibold">Status</h2>
          <p className={
            invoiceData.status.toLowerCase() === 'paid' ? "text-green-600 font-semibold" : 
            invoiceData.status.toLowerCase() === 'pending' ? "text-yellow-600 font-semibold" : 
            "text-red-600 font-semibold"
          }>
            {invoiceData.status}
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
          <p className="text-lg font-bold">{invoiceData.currency} {invoiceData.amount.toLocaleString()}</p>
        </div>
        <div>
          <h2 className="font-semibold">Currency</h2>
          <p>{invoiceData.currency}</p>
        </div>
      </div>

      {invoiceData.description && (
        <div className="mb-6">
          <h3 className="font-semibold">Description</h3>
          <p className="text-gray-700">{invoiceData.description}</p>
        </div>
      )}

      {invoiceData.items && invoiceData.items.length > 0 && (
        <>
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
                  <td className="p-2">{item.description}</td>
                  <td className="p-2">{item.quantity}</td>
                  <td className="p-2">{invoiceData.currency} {item.unit_price.toLocaleString()}</td>
                  <td className="p-2">{invoiceData.currency} {item.amount.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}

      {invoiceData.notes && (
        <div className="mb-6">
          <h3 className="font-semibold">Notes</h3>
          <p className="text-gray-700">{invoiceData.notes}</p>
        </div>
      )}

      {invoiceData.payments && invoiceData.payments.length > 0 ? (
        <div className="mb-6">
          <h3 className="font-semibold mb-2">Payment History</h3>
          {invoiceData.payments.map((payment, idx) => (
            <div key={idx} className="grid grid-cols-2 gap-4 border-b pb-2 mb-2">
              <div>
                <p><span className="font-medium">Method:</span> {payment.method}</p>
                <p><span className="font-medium">Date:</span> {payment.date}</p>
              </div>
              <div>
                <p><span className="font-medium">Amount:</span> {invoiceData.currency} {payment.amount.toLocaleString()}</p>
                <p><span className="font-medium">Transaction ID:</span> {payment.transactionId}</p>
              </div>
            </div>
          ))}
        </div>
      ) : invoiceData.status.toLowerCase() !== 'paid' ? (
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
      ) : null}

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

      {/* Email History Section */}
      <div className="mt-8">
        <EmailHistory invoiceId={invoiceData.number} />
      </div>

      {/* Email Modal */}
      {showEmailModal && (
        <SendInvoiceEmailModal
          invoiceId={invoiceData.number}
          customerEmail={invoiceData.customerEmail || "customer@example.com"}
          customerName={invoiceData.client}
          onClose={() => setShowEmailModal(false)}
          onSuccess={() => {
            alert('Invoice sent successfully!');
          }}
        />
      )}

      {/* Email Setup Modal */}
      <EmailSetupModal 
        isOpen={showEmailSetup}
        onClose={() => setShowEmailSetup(false)}
      />
    </div>
  );
}
