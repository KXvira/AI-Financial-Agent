'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

interface AIInvoiceGeneratorProps {
  customerId: string;
  customerName: string;
  onClose?: () => void;
}

interface InvoiceItem {
  description: string;
  quantity: number;
  unit_price: number;
  total: number;
}

interface InvoiceDraft {
  draft_id?: string;
  customer_id: string;
  customer_name: string;
  issue_date: string;
  due_date: string;
  items: InvoiceItem[];
  subtotal: number;
  tax_rate: number;
  tax_amount: number;
  total_amount: number;
  currency: string;
  notes: string;
  status: string;
  generated_by: string;
}

export default function AIInvoiceGenerator({ customerId, customerName, onClose }: AIInvoiceGeneratorProps) {
  const router = useRouter();
  const [step, setStep] = useState<'input' | 'preview' | 'editing'>('input');
  const [prompt, setPrompt] = useState('');
  const [dueDays, setDueDays] = useState('30');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [draft, setDraft] = useState<InvoiceDraft | null>(null);
  const [editedItems, setEditedItems] = useState<InvoiceItem[]>([]);
  const [editedNotes, setEditedNotes] = useState('');

  const examplePrompts = [
    'Invoice for web development services, 40 hours at KES 2,500/hour',
    'Monthly retainer for digital marketing services - KES 50,000',
    'Consulting services for business strategy, 3 days at KES 15,000/day',
    'Software license renewal for 10 users at KES 5,000 per user',
  ];

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      setError('Please enter a description of what to invoice');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/api/ai-invoice/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          customer_id: customerId,
          prompt: prompt.trim(),
          due_days: parseInt(dueDays) || 30,
          currency: 'KES',
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to generate invoice');
      }

      const data = await response.json();
      setDraft(data);
      setEditedItems(data.items);
      setEditedNotes(data.notes);
      setStep('preview');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate invoice');
      console.error('Error generating invoice:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = () => {
    setStep('editing');
  };

  const handleSaveEdits = async () => {
    if (!draft?.draft_id) return;

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`http://localhost:8000/api/ai-invoice/drafts/${draft.draft_id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          items: editedItems,
          notes: editedNotes,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to save edits');
      }

      const updatedDraft = await response.json();
      setDraft(updatedDraft);
      setStep('preview');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save edits');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateInvoice = async () => {
    if (!draft?.draft_id) return;

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`http://localhost:8000/api/ai-invoice/drafts/${draft.draft_id}/convert`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error('Failed to create invoice');
      }

      const result = await response.json();
      
      // Redirect to the new invoice
      router.push(`/invoices/${result.invoice_id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create invoice');
    } finally {
      setLoading(false);
    }
  };

  const handleItemChange = (index: number, field: keyof InvoiceItem, value: string | number) => {
    const newItems = [...editedItems];
    newItems[index] = { ...newItems[index], [field]: value };
    
    // Recalculate total for this item
    if (field === 'quantity' || field === 'unit_price') {
      const qty = field === 'quantity' ? parseFloat(value as string) || 0 : newItems[index].quantity;
      const price = field === 'unit_price' ? parseFloat(value as string) || 0 : newItems[index].unit_price;
      newItems[index].total = qty * price;
    }
    
    setEditedItems(newItems);
  };

  const handleAddItem = () => {
    setEditedItems([
      ...editedItems,
      { description: '', quantity: 1, unit_price: 0, total: 0 }
    ]);
  };

  const handleRemoveItem = (index: number) => {
    setEditedItems(editedItems.filter((_, i) => i !== index));
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-KE', {
      style: 'currency',
      currency: 'KES',
      minimumFractionDigits: 2
    }).format(amount);
  };

  const calculateTotals = () => {
    const subtotal = editedItems.reduce((sum, item) => sum + item.total, 0);
    const taxAmount = subtotal * 0.16;
    const total = subtotal + taxAmount;
    return { subtotal, taxAmount, total };
  };

  // Input Step
  if (step === 'input') {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6 max-w-3xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Generate Invoice with AI</h2>
            <p className="text-gray-600 mt-1">For: {customerName}</p>
          </div>
          {onClose && (
            <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
        </div>

        {error && (
          <div className="mb-4 bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        <div className="space-y-6">
          <div>
            <label htmlFor="prompt" className="block text-sm font-medium text-gray-700 mb-2">
              What would you like to invoice? 🤖
            </label>
            <textarea
              id="prompt"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              rows={4}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Describe what you want to invoice in natural language. Be as detailed as you want!"
            />
            <p className="mt-2 text-sm text-gray-500">
              💡 The AI will analyze customer history and generate appropriate invoice items with pricing
            </p>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="dueDays" className="block text-sm font-medium text-gray-700 mb-2">
                Payment Due (days)
              </label>
              <input
                type="number"
                id="dueDays"
                value={dueDays}
                onChange={(e) => setDueDays(e.target.value)}
                min="1"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Currency
              </label>
              <input
                type="text"
                value="KES"
                disabled
                className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50"
              />
            </div>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p className="text-sm font-medium text-blue-900 mb-2">💡 Example prompts:</p>
            <div className="space-y-2">
              {examplePrompts.map((example, index) => (
                <button
                  key={index}
                  onClick={() => setPrompt(example)}
                  className="block w-full text-left text-sm text-blue-700 hover:text-blue-900 hover:bg-blue-100 px-3 py-2 rounded"
                >
                  "{example}"
                </button>
              ))}
            </div>
          </div>

          <div className="flex justify-end gap-3">
            {onClose && (
              <button
                onClick={onClose}
                className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
            )}
            <button
              onClick={handleGenerate}
              disabled={loading || !prompt.trim()}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-blue-400 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {loading ? (
                <>
                  <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Generating...
                </>
              ) : (
                <>
                  🤖 Generate Invoice
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Preview Step
  if (step === 'preview' && draft) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6 max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Invoice Preview</h2>
            <p className="text-gray-600 mt-1">
              Generated by {draft.generated_by === 'ai' ? '🤖 AI' : 'Mock'} • Review and edit before creating
            </p>
          </div>
          {onClose && (
            <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
        </div>

        {error && (
          <div className="mb-4 bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        <div className="border border-gray-200 rounded-lg p-6 mb-6">
          {/* Invoice Header */}
          <div className="flex justify-between mb-8">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">{draft.customer_name}</h3>
              <p className="text-sm text-gray-600">{draft.customer_id}</p>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-600">Issue Date: {draft.issue_date}</p>
              <p className="text-sm text-gray-600">Due Date: {draft.due_date}</p>
              <span className="inline-block mt-2 px-3 py-1 bg-yellow-100 text-yellow-800 text-xs font-semibold rounded">
                DRAFT
              </span>
            </div>
          </div>

          {/* Invoice Items */}
          <div className="mb-6">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Description</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Qty</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Unit Price</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Total</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {draft.items.map((item, index) => (
                  <tr key={index}>
                    <td className="px-4 py-3 text-sm text-gray-900">{item.description}</td>
                    <td className="px-4 py-3 text-sm text-gray-900 text-right">{item.quantity}</td>
                    <td className="px-4 py-3 text-sm text-gray-900 text-right">{formatCurrency(item.unit_price)}</td>
                    <td className="px-4 py-3 text-sm text-gray-900 text-right font-medium">{formatCurrency(item.total)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Totals */}
          <div className="border-t border-gray-200 pt-4">
            <div className="flex justify-end">
              <div className="w-64 space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Subtotal:</span>
                  <span className="text-gray-900">{formatCurrency(draft.subtotal)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Tax (16%):</span>
                  <span className="text-gray-900">{formatCurrency(draft.tax_amount)}</span>
                </div>
                <div className="flex justify-between text-lg font-bold border-t pt-2">
                  <span className="text-gray-900">Total:</span>
                  <span className="text-gray-900">{formatCurrency(draft.total_amount)}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Notes */}
          {draft.notes && (
            <div className="mt-6 pt-6 border-t border-gray-200">
              <p className="text-sm font-medium text-gray-700 mb-2">Notes:</p>
              <p className="text-sm text-gray-600">{draft.notes}</p>
            </div>
          )}
        </div>

        <div className="flex justify-between items-center">
          <button
            onClick={() => setStep('input')}
            className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
          >
            ← Start Over
          </button>
          <div className="flex gap-3">
            <button
              onClick={handleEdit}
              className="px-6 py-2 border border-blue-600 text-blue-600 rounded-lg hover:bg-blue-50"
            >
              ✏️ Edit Details
            </button>
            <button
              onClick={handleCreateInvoice}
              disabled={loading}
              className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-green-400 disabled:cursor-not-allowed"
            >
              {loading ? 'Creating...' : '✓ Create Invoice'}
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Editing Step
  if (step === 'editing' && draft) {
    const totals = calculateTotals();
    
    return (
      <div className="bg-white rounded-lg shadow-lg p-6 max-w-5xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Edit Invoice Draft</h2>
          {onClose && (
            <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
        </div>

        {error && (
          <div className="mb-4 bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        <div className="space-y-6">
          {/* Items */}
          <div>
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Invoice Items</h3>
              <button
                onClick={handleAddItem}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm"
              >
                + Add Item
              </button>
            </div>

            <div className="space-y-4">
              {editedItems.map((item, index) => (
                <div key={index} className="grid grid-cols-12 gap-4 items-start border border-gray-200 rounded-lg p-4">
                  <div className="col-span-5">
                    <label className="block text-xs font-medium text-gray-700 mb-1">Description</label>
                    <input
                      type="text"
                      value={item.description}
                      onChange={(e) => handleItemChange(index, 'description', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                      placeholder="Item description"
                    />
                  </div>
                  <div className="col-span-2">
                    <label className="block text-xs font-medium text-gray-700 mb-1">Quantity</label>
                    <input
                      type="number"
                      value={item.quantity}
                      onChange={(e) => handleItemChange(index, 'quantity', e.target.value)}
                      min="0"
                      step="0.01"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                    />
                  </div>
                  <div className="col-span-2">
                    <label className="block text-xs font-medium text-gray-700 mb-1">Unit Price</label>
                    <input
                      type="number"
                      value={item.unit_price}
                      onChange={(e) => handleItemChange(index, 'unit_price', e.target.value)}
                      min="0"
                      step="0.01"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                    />
                  </div>
                  <div className="col-span-2">
                    <label className="block text-xs font-medium text-gray-700 mb-1">Total</label>
                    <input
                      type="text"
                      value={formatCurrency(item.total)}
                      disabled
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm bg-gray-50"
                    />
                  </div>
                  <div className="col-span-1 flex items-end">
                    <button
                      onClick={() => handleRemoveItem(index)}
                      className="p-2 text-red-600 hover:bg-red-50 rounded-lg"
                      title="Remove item"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Totals */}
          <div className="border-t border-gray-200 pt-4">
            <div className="flex justify-end">
              <div className="w-64 space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Subtotal:</span>
                  <span className="text-gray-900">{formatCurrency(totals.subtotal)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Tax (16%):</span>
                  <span className="text-gray-900">{formatCurrency(totals.taxAmount)}</span>
                </div>
                <div className="flex justify-between text-lg font-bold border-t pt-2">
                  <span className="text-gray-900">Total:</span>
                  <span className="text-gray-900">{formatCurrency(totals.total)}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Notes */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Notes</label>
            <textarea
              value={editedNotes}
              onChange={(e) => setEditedNotes(e.target.value)}
              rows={3}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg"
              placeholder="Additional notes or payment instructions..."
            />
          </div>

          {/* Actions */}
          <div className="flex justify-between items-center pt-4 border-t">
            <button
              onClick={() => setStep('preview')}
              className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
            >
              ← Cancel
            </button>
            <button
              onClick={handleSaveEdits}
              disabled={loading}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-blue-400 disabled:cursor-not-allowed"
            >
              {loading ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </div>
      </div>
    );
  }

  return null;
}
