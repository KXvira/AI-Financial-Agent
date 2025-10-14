'use client';

import React, { useState, useEffect } from 'react';
import { X, User, Mail, Phone, Building2, Shield, Lock, AlertCircle } from 'lucide-react';

interface UserFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  user?: {
    _id: string;
    email: string;
    company_name: string;
    phone_number?: string;
    role: string;
    status: string;
  } | null;
  mode: 'create' | 'edit';
}

interface FormData {
  email: string;
  company_name: string;
  phone_number: string;
  role: string;
  status: string;
  password?: string;
  confirmPassword?: string;
}

interface FormErrors {
  email?: string;
  company_name?: string;
  phone_number?: string;
  password?: string;
  confirmPassword?: string;
  general?: string;
}

const UserFormModal: React.FC<UserFormModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
  user,
  mode,
}) => {
  const [formData, setFormData] = useState<FormData>({
    email: '',
    company_name: '',
    phone_number: '',
    role: 'viewer',
    status: 'active',
    password: '',
    confirmPassword: '',
  });

  const [errors, setErrors] = useState<FormErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  // Populate form when editing
  useEffect(() => {
    if (mode === 'edit' && user) {
      setFormData({
        email: user.email,
        company_name: user.company_name,
        phone_number: user.phone_number || '',
        role: user.role,
        status: user.status,
      });
    } else if (mode === 'create') {
      setFormData({
        email: '',
        company_name: '',
        phone_number: '',
        role: 'viewer',
        status: 'active',
        password: '',
        confirmPassword: '',
      });
    }
    setErrors({});
  }, [mode, user, isOpen]);

  // Validation functions
  const validateEmail = (email: string): string | undefined => {
    if (!email) return 'Email is required';
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) return 'Invalid email format';
    return undefined;
  };

  const validateCompanyName = (name: string): string | undefined => {
    if (!name || name.trim().length === 0) return 'Company name is required';
    if (name.length < 2) return 'Company name must be at least 2 characters';
    return undefined;
  };

  const validatePhoneNumber = (phone: string): string | undefined => {
    if (!phone) return undefined; // Phone is optional
    const phoneRegex = /^[+]?[\d\s\-()]+$/;
    if (!phoneRegex.test(phone)) return 'Invalid phone number format';
    if (phone.replace(/\D/g, '').length < 10) return 'Phone number must be at least 10 digits';
    return undefined;
  };

  const validatePassword = (password: string): string | undefined => {
    if (mode === 'create') {
      if (!password) return 'Password is required';
      if (password.length < 8) return 'Password must be at least 8 characters';
      if (!/(?=.*[a-z])/.test(password)) return 'Password must contain lowercase letter';
      if (!/(?=.*[A-Z])/.test(password)) return 'Password must contain uppercase letter';
      if (!/(?=.*\d)/.test(password)) return 'Password must contain a number';
    }
    return undefined;
  };

  const validateConfirmPassword = (
    password: string,
    confirmPassword: string
  ): string | undefined => {
    if (mode === 'create') {
      if (!confirmPassword) return 'Please confirm password';
      if (password !== confirmPassword) return 'Passwords do not match';
    }
    return undefined;
  };

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    newErrors.email = validateEmail(formData.email);
    newErrors.company_name = validateCompanyName(formData.company_name);
    newErrors.phone_number = validatePhoneNumber(formData.phone_number);

    if (mode === 'create') {
      newErrors.password = validatePassword(formData.password || '');
      newErrors.confirmPassword = validateConfirmPassword(
        formData.password || '',
        formData.confirmPassword || ''
      );
    }

    setErrors(newErrors);
    return !Object.values(newErrors).some((error) => error !== undefined);
  };

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));

    // Clear error for this field
    if (errors[name as keyof FormErrors]) {
      setErrors((prev) => ({ ...prev, [name]: undefined }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    setErrors({});

    try {
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('Authentication token not found');
      }

      const url =
        mode === 'create'
          ? 'http://localhost:8000/admin/users'
          : `http://localhost:8000/admin/users/${user?._id}`;

      const method = mode === 'create' ? 'POST' : 'PUT';

      // Prepare request body
      const body: any = {
        email: formData.email,
        company_name: formData.company_name,
        role: formData.role,
        status: formData.status,
      };

      if (formData.phone_number) {
        body.phone_number = formData.phone_number;
      }

      if (mode === 'create' && formData.password) {
        body.password = formData.password;
      }

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(body),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to save user');
      }

      // Success
      onSuccess();
      onClose();
    } catch (error) {
      console.error('Error saving user:', error);
      setErrors({
        general:
          error instanceof Error ? error.message : 'An unexpected error occurred',
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isOpen) return null;

  const roleColors: Record<string, string> = {
    admin: 'bg-purple-100 text-purple-800 border-purple-300',
    owner: 'bg-blue-100 text-blue-800 border-blue-300',
    manager: 'bg-green-100 text-green-800 border-green-300',
    accountant: 'bg-yellow-100 text-yellow-800 border-yellow-300',
    viewer: 'bg-gray-100 text-gray-800 border-gray-300',
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <User className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900">
                {mode === 'create' ? 'Create New User' : 'Edit User'}
              </h2>
              <p className="text-sm text-gray-600">
                {mode === 'create'
                  ? 'Add a new user to the system'
                  : 'Update user information and permissions'}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            disabled={isSubmitting}
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* General Error */}
          {errors.general && (
            <div className="flex items-start gap-2 p-4 bg-red-50 border border-red-200 rounded-lg">
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <p className="text-sm font-medium text-red-800">Error</p>
                <p className="text-sm text-red-700">{errors.general}</p>
              </div>
            </div>
          )}

          {/* Email */}
          <div>
            <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
              <Mail className="w-4 h-4" />
              Email Address <span className="text-red-500">*</span>
            </label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              disabled={mode === 'edit' || isSubmitting}
              className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all ${
                errors.email ? 'border-red-300 bg-red-50' : 'border-gray-300'
              } ${mode === 'edit' ? 'bg-gray-100 cursor-not-allowed' : ''}`}
              placeholder="user@example.com"
            />
            {errors.email && (
              <p className="mt-1 text-sm text-red-600">{errors.email}</p>
            )}
            {mode === 'edit' && (
              <p className="mt-1 text-xs text-gray-500">
                Email cannot be changed after account creation
              </p>
            )}
          </div>

          {/* Company Name */}
          <div>
            <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
              <Building2 className="w-4 h-4" />
              Company Name <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              name="company_name"
              value={formData.company_name}
              onChange={handleInputChange}
              disabled={isSubmitting}
              className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all ${
                errors.company_name ? 'border-red-300 bg-red-50' : 'border-gray-300'
              }`}
              placeholder="Acme Corporation"
            />
            {errors.company_name && (
              <p className="mt-1 text-sm text-red-600">{errors.company_name}</p>
            )}
          </div>

          {/* Phone Number */}
          <div>
            <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
              <Phone className="w-4 h-4" />
              Phone Number
            </label>
            <input
              type="tel"
              name="phone_number"
              value={formData.phone_number}
              onChange={handleInputChange}
              disabled={isSubmitting}
              className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all ${
                errors.phone_number ? 'border-red-300 bg-red-50' : 'border-gray-300'
              }`}
              placeholder="+1 (555) 123-4567"
            />
            {errors.phone_number && (
              <p className="mt-1 text-sm text-red-600">{errors.phone_number}</p>
            )}
          </div>

          {/* Role */}
          <div>
            <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
              <Shield className="w-4 h-4" />
              Role <span className="text-red-500">*</span>
            </label>
            <select
              name="role"
              value={formData.role}
              onChange={handleInputChange}
              disabled={isSubmitting}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
            >
              <option value="admin">Admin - Full system access</option>
              <option value="owner">Owner - Full system access</option>
              <option value="manager">Manager - User & data management</option>
              <option value="accountant">Accountant - Financial records</option>
              <option value="viewer">Viewer - Read-only access</option>
            </select>
            <div className="mt-2">
              <span
                className={`inline-flex px-3 py-1 text-xs font-medium rounded-full border ${
                  roleColors[formData.role] || roleColors.viewer
                }`}
              >
                {formData.role.charAt(0).toUpperCase() + formData.role.slice(1)}
              </span>
            </div>
          </div>

          {/* Status */}
          <div>
            <label className="text-sm font-medium text-gray-700 mb-2 block">
              Account Status <span className="text-red-500">*</span>
            </label>
            <select
              name="status"
              value={formData.status}
              onChange={handleInputChange}
              disabled={isSubmitting}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
            >
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
              <option value="locked">Locked</option>
              <option value="pending">Pending</option>
            </select>
          </div>

          {/* Password (Create mode only) */}
          {mode === 'create' && (
            <>
              <div>
                <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
                  <Lock className="w-4 h-4" />
                  Password <span className="text-red-500">*</span>
                </label>
                <div className="relative">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    name="password"
                    value={formData.password}
                    onChange={handleInputChange}
                    disabled={isSubmitting}
                    className={`w-full px-4 py-2 pr-12 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all ${
                      errors.password ? 'border-red-300 bg-red-50' : 'border-gray-300'
                    }`}
                    placeholder="Enter secure password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
                  >
                    {showPassword ? '🙈' : '👁️'}
                  </button>
                </div>
                {errors.password && (
                  <p className="mt-1 text-sm text-red-600">{errors.password}</p>
                )}
                <p className="mt-1 text-xs text-gray-500">
                  At least 8 characters with uppercase, lowercase, and number
                </p>
              </div>

              <div>
                <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
                  <Lock className="w-4 h-4" />
                  Confirm Password <span className="text-red-500">*</span>
                </label>
                <input
                  type={showPassword ? 'text' : 'password'}
                  name="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleInputChange}
                  disabled={isSubmitting}
                  className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all ${
                    errors.confirmPassword
                      ? 'border-red-300 bg-red-50'
                      : 'border-gray-300'
                  }`}
                  placeholder="Re-enter password"
                />
                {errors.confirmPassword && (
                  <p className="mt-1 text-sm text-red-600">{errors.confirmPassword}</p>
                )}
              </div>
            </>
          )}

          {/* Form Actions */}
          <div className="flex items-center justify-end gap-3 pt-4 border-t">
            <button
              type="button"
              onClick={onClose}
              disabled={isSubmitting}
              className="px-6 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-6 py-2 text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {isSubmitting ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  {mode === 'create' ? 'Creating...' : 'Updating...'}
                </>
              ) : (
                <>{mode === 'create' ? 'Create User' : 'Update User'}</>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default UserFormModal;
