//to create a new invoice with itemized inputs
//app/invoices/new
"use client";

import { useState } from "react";

export default function NewInvoicePage() {
  const [customer, setCustomer] = useState("Tech Solutions Ltd");
  const [newCustomer, setNewCustomer] = useState("");
  const [invoiceNumber, setInvoiceNumber] = useState("");
  const [issueDate, setIssueDate] = useState("");
  const [dueDate, setDueDate] = useState("");
  const [notes, setNotes] = useState("");
  const [items, setItems] = useState([
    { item: "Consulting Services", quantity: 2, price: 5000, amount: 10000 },
  ]);

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>, status: string) => {
    e.preventDefault();
    const finalCustomer = newCustomer || customer;
    const invoice = {
      customer: finalCustomer,
      invoiceNumber,
      issueDate,
      dueDate,
      notes,
      items,
      status,
    };
    console.log("Submitted Invoice:", invoice);
    alert(`Invoice ${status === "draft" ? "saved as draft" : "sent"}`);
  };

  const handleItemChange = (index: number, field: string, value: string | number) => {
    const updatedItems = [...items];
    updatedItems[index] = {
      ...updatedItems[index],
      [field]: value,
      amount:
        field === "quantity" || field === "price"
          ? (field === "quantity" ? Number(value) : updatedItems[index].quantity) *
            (field === "price" ? Number(value) : updatedItems[index].price)
          : updatedItems[index].amount,
    };
    setItems(updatedItems);
  };

  const handleRemoveItem = () => {
    if (items.length > 1) {
      setItems(items.slice(0, -1));
    }
  };

  return (
    <form onSubmit={(e) => handleSubmit(e, "sent")} className="p-8">
      <h1 className="text-2xl font-bold mb-6">New Invoice</h1>

      <div className="space-y-4 max-w-md">
        <label className="block text-sm text-gray-600">Customer</label>
        <select
          value={customer}
          onChange={(e) => setCustomer(e.target.value)}
          className="w-full p-2 border rounded"
        >
          <option value="">Select a customer</option>
          <option value="Tech Solutions Ltd">Tech Solutions Ltd</option>
          <option value="Creative Designs Agency">Creative Designs Agency</option>
        </select>

        <input
          type="text"
          placeholder="Or add new customer name"
          value={newCustomer}
          onChange={(e) => setNewCustomer(e.target.value)}
          className="w-full p-2 border rounded"
        />

        <input
          type="text"
          placeholder="Invoice number"
          value={invoiceNumber}
          onChange={(e) => setInvoiceNumber(e.target.value)}
          className="w-full p-2 border rounded"
        />

        <label className="block text-sm text-gray-600 mb-1">Issue Date</label>
        <input
          type="date"
          value={issueDate}
          onChange={(e) => setIssueDate(e.target.value)}
          className="w-full p-2 border rounded"
        />

        <label className="text-sm text-gray-600 mb-1">Due Date</label>
        <input
          type="date"
          value={dueDate}
          onChange={(e) => setDueDate(e.target.value)}
          className="w-full p-2 border rounded"
        />
      </div>

      <h2 className="text-xl font-semibold mt-8 mb-2">Items</h2>
      <table className="w-full text-sm text-left border-collapse mb-4">
        <thead className="text-gray-500">
          <tr>
            <th className="p-2">Item</th>
            <th className="p-2">Quantity</th>
            <th className="p-2">Price</th>
            <th className="p-2">Amount</th>
          </tr>
        </thead>
        <tbody>
          {items.map((it, idx) => (
            <tr key={idx} className="border-t">
              <td className="p-2">
                <input
                  type="text"
                  value={it.item}
                  onChange={(e) => handleItemChange(idx, "item", e.target.value)}
                  className="w-full border p-1 rounded"
                />
              </td>
              <td className="p-2">
                <input
                  type="number"
                  value={it.quantity}
                  onChange={(e) => handleItemChange(idx, "quantity", Number(e.target.value))}
                  className="w-full border p-1 rounded"
                />
              </td>
              <td className="p-2">
                <input
                  type="number"
                  value={it.price}
                  onChange={(e) => handleItemChange(idx, "price", Number(e.target.value))}
                  className="w-full border p-1 rounded"
                />
              </td>
              <td className="p-2">{it.amount}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <div className="flex gap-2 mb-6">
        <button
          type="button"
          className="bg-green-400 text-white px-3 py-1 rounded"
          onClick={() =>
            setItems([...items, { item: "", quantity: 1, price: 0, amount: 0 }])
          }
        >
          Add Item
        </button>
        <button
          type="button"
          className="bg-red-400 text-white px-3 py-1 rounded"
          onClick={handleRemoveItem}
        >
          Remove Item
        </button>
      </div>

      <textarea
        className="block mt-6 w-full max-w-md h-24 p-2 border rounded"
        placeholder="Notes"
        value={notes}
        onChange={(e) => setNotes(e.target.value)}
      ></textarea>

      <div className="flex space-x-4 mt-6">
        <button
          type="button"
          onClick={(e) => handleSubmit(e as any, "draft")}
          className="bg-gray-200 px-4 py-2 rounded"
        >
          Save the Invoice
        </button>
        <button type="submit" className="bg-blue-400 text-blue-900 text-white px-4 py-2 rounded">
          Send Invoice
        </button>
      </div>
    </form>
  );
}