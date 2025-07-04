"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

export default function AddPaymentForm() {
  const router = useRouter();

  const [payment, setPayment] = useState({
    reference: "",
    client: "",
    date: "",
    amount: "",
    method: "Bank Transfer",
  });

  type PaymentItem = { item: string; quantity: number; price: number };

  const [items, setItems] = useState<PaymentItem[]>([
    { item: "", quantity: 1, price: 0 }
  ]);

  // Auto-calculate total amount from items
  useEffect(() => {
    const total = items.reduce((sum, item) => sum + item.quantity * item.price, 0);
    setPayment((prev) => ({ ...prev, amount: `KES ${total.toLocaleString()}` }));
  }, [items]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setPayment((prev) => ({ ...prev, [name]: value }));
  };

  const handleItemChange = (index: number, e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    const newItems = [...items];
    if (name === "quantity" || name === "price") {
      newItems[index][name as "quantity" | "price"] = parseFloat(value);
    } else if (name === "item") {
      newItems[index].item = value;
    }
    setItems(newItems);
  };

  const addItem = () => {
    setItems([...items, { item: "", quantity: 1, price: 0 }]);
  };

  const removeItem = (index: number) => {
    const newItems = [...items];
    newItems.splice(index, 1);
    setItems(newItems);
  };

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    alert("Payment added successfully!");
    router.push("/payments/list");
  };

  return (

      <div className="max-w-3xl mx-auto p-8 bg-white shadow-md rounded-md">
        <h1 className="text-2xl font-bold mb-6">Add New Payment</h1>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Payment Reference</label>
              <input
                type="text"
                name="reference"
                value={payment.reference}
                onChange={handleChange}
                placeholder="PAY-2024-001"
                required
                className="mt-1 block w-full p-2 border rounded"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Client</label>
              <input
                type="text"
                name="client"
                value={payment.client}
                onChange={handleChange}
                placeholder="Tech Solutions Ltd."
                required
                className="mt-1 block w-full p-2 border rounded"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Date</label>
              <input
                type="date"
                name="date"
                value={payment.date}
                onChange={handleChange}
                required
                className="mt-1 block w-full p-2 border rounded"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Amount (Auto-calculated)</label>
              <input
                type="text"
                name="amount"
                value={payment.amount}
                readOnly
                placeholder="Auto calculated from items"
                className="mt-1 block w-full p-2 border rounded bg-gray-100"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Payment Method</label>
              <select
                name="method"
                value={payment.method}
                onChange={handleChange}
                className="mt-1 block w-full p-2 border rounded"
              >
                <option>Bank Transfer</option>
                <option>Mobile Money</option>
                <option>Cheque</option>
                <option>Cash</option>
              </select>
            </div>
          </div>

          <div>
            <h2 className="text-lg font-semibold mt-6 mb-2">Items</h2>
            {items.map((item, index) => (
              <div key={index} className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
                <input
                  type="text"
                  name="item"
                  value={item.item}
                  onChange={(e) => handleItemChange(index, e)}
                  placeholder="Item description"
                  className="p-2 border rounded"
                />
                <input
                  type="number"
                  name="quantity"
                  value={item.quantity}
                  onChange={(e) => handleItemChange(index, e)}
                  placeholder="Quantity"
                  className="p-2 border rounded"
                />
                <input
                  type="number"
                  name="price"
                  value={item.price}
                  onChange={(e) => handleItemChange(index, e)}
                  placeholder="Price per item"
                  className="p-2 border rounded"
                />
                <button
                  type="button"
                  onClick={() => removeItem(index)}
                  className="bg-red-500 text-white px-3 rounded hover:bg-red-600"
                >
                  Remove
                </button>
              </div>
            ))}

            <button
              type="button"
              onClick={addItem}
              className="mt-2 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              Add Item
            </button>
          </div>

          <button
            type="submit"
            className="bg-green-600 text-white px-6 py-2 rounded hover:bg-green-700"
          >
            Submit Payment
          </button>
        </form>
      </div>

  );
}


