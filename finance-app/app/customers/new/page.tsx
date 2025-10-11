'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

interface CustomerFormData {
  name: string;
  email: string;
  phone: string;
  secondary_email: string;
  secondary_phone: string;
  street: string;
  city: string;
  state: string;
  postal_code: string;
  country: string;
  business_type: string;
  tax_id: string;
  payment_terms: string;
  notes: string;
}

export default function NewCustomerPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState<CustomerFormData>({
    name: '',
    email: '',
    phone: '254',
    secondary_email: '',
    secondary_phone: '254',
    street: '',
    city: '',
    state: '',
    postal_code: '',
    country: 'Kenya',
    business_type: '',
    tax_id: '',
    payment_terms: '30',
    notes: ''
  });

  const [errors, setErrors] = useState<Partial<Record<keyof CustomerFormData, string>>>({});

  const validateForm = (): boolean => {
    const newErrors: Partial<Record<keyof CustomerFormData, string>> = {};

    // Required fields
    if (!formData.name.trim()) {
      newErrors.name = 'Customer name is required';
    }

    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Invalid email format';
    }

    if (!formData.phone.trim()) {
      newErrors.phone = 'Phone number is required';
    } else if (!/^254\d{9}$/.test(formData.phone)) {
      newErrors.phone = 'Phone must be in format 254XXXXXXXXX (12 digits)';
    }

    // Optional secondary email validation
    if (formData.secondary_email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.secondary_email)) {
      newErrors.secondary_email = 'Invalid email format';
    }

    // Optional secondary phone validation
    if (formData.secondary_phone && formData.secondary_phone !== '254' && !/^254\d{9}$/.test(formData.secondary_phone)) {
      newErrors.secondary_phone = 'Phone must be in format 254XXXXXXXXX';
    }

    // Payment terms validation
    if (formData.payment_terms && (isNaN(Number(formData.payment_terms)) || Number(formData.payment_terms) < 0)) {
      newErrors.payment_terms = 'Payment terms must be a positive number';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Prepare data for API
      const apiData: any = {
        name: formData.name.trim(),
        email: formData.email.trim(),
        phone: formData.phone.trim(),
      };

      // Add optional fields only if they have values
      if (formData.secondary_email?.trim()) {
        apiData.secondary_email = formData.secondary_email.trim();
      }

      if (formData.secondary_phone?.trim() && formData.secondary_phone !== '254') {
        apiData.secondary_phone = formData.secondary_phone.trim();
      }

      // Address
      const hasAddress = formData.street || formData.city || formData.state || formData.postal_code || formData.country;
      if (hasAddress) {
        apiData.address = {};
        if (formData.street?.trim()) apiData.address.street = formData.street.trim();
        if (formData.city?.trim()) apiData.address.city = formData.city.trim();
        if (formData.state?.trim()) apiData.address.state = formData.state.trim();
        if (formData.postal_code?.trim()) apiData.address.postal_code = formData.postal_code.trim();
        if (formData.country?.trim()) apiData.address.country = formData.country.trim();
      }

      // Business info
      if (formData.business_type?.trim()) {
        apiData.business_type = formData.business_type.trim();
      }
      if (formData.tax_id?.trim()) {
        apiData.tax_id = formData.tax_id.trim();
      }
      if (formData.payment_terms) {
        apiData.payment_terms = Number(formData.payment_terms);
      }

      // Notes
      if (formData.notes?.trim()) {
        apiData.notes = formData.notes.trim();
      }

      const response = await fetch('http://localhost:8000/api/customers/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(apiData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create customer');
      }

      const customer = await response.json();
      
      // Redirect to the new customer's page
      router.push(`/customers/${customer.customer_id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create customer');
      console.error('Error creating customer:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    // Clear error for this field
    if (errors[name as keyof CustomerFormData]) {
      setErrors(prev => ({
        ...prev,
        [name]: undefined
      }));
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <Link
            href="/customers"
            className="text-blue-600 hover:text-blue-800 mb-2 inline-block"
          >
            ← Back to Customers
          </Link>
          <h1 className="text-3xl font-bold text-gray-900">Create New Customer</h1>
          <p className="text-gray-600 mt-2">Add a new customer to your system</p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow">
          {/* Basic Information */}
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Basic Information</h2>
            <div className="grid grid-cols-1 gap-6">
              <div>
                <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
                  Customer Name <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  id="name"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                    errors.name ? 'border-red-500' : 'border-gray-300'
                  }`}
                  placeholder="e.g., ABC Corporation"
                />
                {errors.name && <p className="mt-1 text-sm text-red-600">{errors.name}</p>}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                    Primary Email <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="email"
                    id="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                      errors.email ? 'border-red-500' : 'border-gray-300'
                    }`}
                    placeholder="email@example.com"
                  />
                  {errors.email && <p className="mt-1 text-sm text-red-600">{errors.email}</p>}
                </div>

                <div>
                  <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-2">
                    Primary Phone <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="tel"
                    id="phone"
                    name="phone"
                    value={formData.phone}
                    onChange={handleChange}
                    className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                      errors.phone ? 'border-red-500' : 'border-gray-300'
                    }`}
                    placeholder="254722000000"
                  />
                  {errors.phone && <p className="mt-1 text-sm text-red-600">{errors.phone}</p>}
                  <p className="mt-1 text-xs text-gray-500">Format: 254XXXXXXXXX (12 digits)</p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label htmlFor="secondary_email" className="block text-sm font-medium text-gray-700 mb-2">
                    Secondary Email
                  </label>
                  <input
                    type="email"
                    id="secondary_email"
                    name="secondary_email"
                    value={formData.secondary_email}
                    onChange={handleChange}
                    className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                      errors.secondary_email ? 'border-red-500' : 'border-gray-300'
                    }`}
                    placeholder="secondary@example.com"
                  />
                  {errors.secondary_email && <p className="mt-1 text-sm text-red-600">{errors.secondary_email}</p>}
                </div>

                <div>
                  <label htmlFor="secondary_phone" className="block text-sm font-medium text-gray-700 mb-2">
                    Secondary Phone
                  </label>
                  <input
                    type="tel"
                    id="secondary_phone"
                    name="secondary_phone"
                    value={formData.secondary_phone}
                    onChange={handleChange}
                    className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                      errors.secondary_phone ? 'border-red-500' : 'border-gray-300'
                    }`}
                    placeholder="254722000000"
                  />
                  {errors.secondary_phone && <p className="mt-1 text-sm text-red-600">{errors.secondary_phone}</p>}
                </div>
              </div>
            </div>
          </div>

          {/* Address */}
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Address</h2>
            <div className="grid grid-cols-1 gap-6">
              <div>
                <label htmlFor="street" className="block text-sm font-medium text-gray-700 mb-2">
                  Street Address
                </label>
                <input
                  type="text"
                  id="street"
                  name="street"
                  value={formData.street}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="123 Main Street"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label htmlFor="city" className="block text-sm font-medium text-gray-700 mb-2">
                    City
                  </label>
                  <input
                    type="text"
                    id="city"
                    name="city"
                    value={formData.city}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Nairobi"
                  />
                </div>

                <div>
                  <label htmlFor="state" className="block text-sm font-medium text-gray-700 mb-2">
                    State/County
                  </label>
                  <input
                    type="text"
                    id="state"
                    name="state"
                    value={formData.state}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Nairobi County"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label htmlFor="postal_code" className="block text-sm font-medium text-gray-700 mb-2">
                    Postal Code
                  </label>
                  <input
                    type="text"
                    id="postal_code"
                    name="postal_code"
                    value={formData.postal_code}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="00100"
                  />
                </div>

                <div>
                  <label htmlFor="country" className="block text-sm font-medium text-gray-700 mb-2">
                    Country
                  </label>
                  <input
                    type="text"
                    id="country"
                    name="country"
                    value={formData.country}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Kenya"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Business Information */}
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Business Information</h2>
            <div className="grid grid-cols-1 gap-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label htmlFor="business_type" className="block text-sm font-medium text-gray-700 mb-2">
                    Business Type
                  </label>
                  <select
                    id="business_type"
                    name="business_type"
                    value={formData.business_type}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">Select business type</option>
                    <option value="Corporation">Corporation</option>
                    <option value="LLC">LLC</option>
                    <option value="Partnership">Partnership</option>
                    <option value="Sole Proprietorship">Sole Proprietorship</option>
                    <option value="Non-Profit">Non-Profit</option>
                    <option value="Other">Other</option>
                  </select>
                </div>

                <div>
                  <label htmlFor="tax_id" className="block text-sm font-medium text-gray-700 mb-2">
                    Tax ID / KRA PIN
                  </label>
                  <input
                    type="text"
                    id="tax_id"
                    name="tax_id"
                    value={formData.tax_id}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="AXXXXXXXXX"
                  />
                </div>
              </div>

              <div>
                <label htmlFor="payment_terms" className="block text-sm font-medium text-gray-700 mb-2">
                  Payment Terms (days)
                </label>
                <input
                  type="number"
                  id="payment_terms"
                  name="payment_terms"
                  value={formData.payment_terms}
                  onChange={handleChange}
                  min="0"
                  className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                    errors.payment_terms ? 'border-red-500' : 'border-gray-300'
                  }`}
                  placeholder="30"
                />
                {errors.payment_terms && <p className="mt-1 text-sm text-red-600">{errors.payment_terms}</p>}
                <p className="mt-1 text-xs text-gray-500">Number of days for payment after invoice date</p>
              </div>
            </div>
          </div>

          {/* Notes */}
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Additional Notes</h2>
            <div>
              <label htmlFor="notes" className="block text-sm font-medium text-gray-700 mb-2">
                Notes
              </label>
              <textarea
                id="notes"
                name="notes"
                value={formData.notes}
                onChange={handleChange}
                rows={4}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Any additional information about this customer..."
              />
            </div>
          </div>

          {/* Form Actions */}
          <div className="p-6 bg-gray-50 flex justify-end gap-3">
            <Link
              href="/customers"
              className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-100"
            >
              Cancel
            </Link>
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-blue-400 disabled:cursor-not-allowed"
            >
              {loading ? 'Creating...' : 'Create Customer'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
