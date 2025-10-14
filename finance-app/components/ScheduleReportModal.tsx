'use client';

import { useState } from 'react';
import { X, Calendar, Clock, Mail, FileText, Users } from 'lucide-react';

interface ScheduleReportModalProps {
  isOpen: boolean;
  onClose: () => void;
  reportTypes: Array<{ id: string; name: string; category: string }>;
  onScheduleCreated?: () => void;
}

interface ScheduleFormData {
  report_type: string;
  frequency: 'daily' | 'weekly' | 'monthly' | 'quarterly';
  schedule_time: string;
  day_of_week?: number;
  day_of_month?: number;
  recipients: string[];
  format: 'pdf' | 'excel' | 'both';
  enabled: boolean;
}

export function ScheduleReportModal({ isOpen, onClose, reportTypes, onScheduleCreated }: ScheduleReportModalProps) {
  const [formData, setFormData] = useState<ScheduleFormData>({
    report_type: '',
    frequency: 'weekly',
    schedule_time: '09:00',
    day_of_week: 1,
    day_of_month: 1,
    recipients: [''],
    format: 'pdf',
    enabled: true,
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      // Validate recipients
      const validRecipients = formData.recipients.filter(email => email.trim() !== '');
      if (validRecipients.length === 0) {
        throw new Error('Please add at least one recipient email address');
      }

      if (!formData.report_type) {
        throw new Error('Please select a report type');
      }

      // Prepare schedule data in backend format
      const scheduleData = {
        name: `${formData.report_type} - ${formData.frequency}`,
        report_type: formData.report_type,
        schedule: {
          frequency: formData.frequency,
          time: formData.schedule_time,
          ...(formData.frequency === 'weekly' && { day_of_week: formData.day_of_week }),
          ...(formData.frequency === 'monthly' && { day_of_month: formData.day_of_month }),
          timezone: 'Africa/Nairobi'
        },
        recipients: validRecipients,
        parameters: {
          format: formData.format
        },
        enabled: formData.enabled,
      };

      const response = await fetch('http://localhost:8000/automation/schedules', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(scheduleData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        
        // Handle different error formats
        let errorMessage = 'Failed to create schedule';
        
        if (typeof errorData.detail === 'string') {
          errorMessage = errorData.detail;
        } else if (Array.isArray(errorData.detail)) {
          // Handle validation errors from FastAPI
          errorMessage = errorData.detail.map((err: any) => 
            `${err.loc?.join('.') || 'Field'}: ${err.msg}`
          ).join(', ');
        } else if (errorData.message) {
          errorMessage = errorData.message;
        }
        
        throw new Error(errorMessage);
      }

      setSuccess(true);
      
      // Refresh schedules list
      if (onScheduleCreated) {
        onScheduleCreated();
      }
      
      setTimeout(() => {
        onClose();
        // Reset form
        setFormData({
          report_type: '',
          frequency: 'weekly',
          schedule_time: '09:00',
          day_of_week: 1,
          day_of_month: 1,
          recipients: [''],
          format: 'pdf',
          enabled: true,
        });
        setSuccess(false);
      }, 2000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create schedule');
    } finally {
      setLoading(false);
    }
  };

  const addRecipient = () => {
    setFormData({ ...formData, recipients: [...formData.recipients, ''] });
  };

  const removeRecipient = (index: number) => {
    const newRecipients = formData.recipients.filter((_, i) => i !== index);
    setFormData({ ...formData, recipients: newRecipients });
  };

  const updateRecipient = (index: number, value: string) => {
    const newRecipients = [...formData.recipients];
    newRecipients[index] = value;
    setFormData({ ...formData, recipients: newRecipients });
  };

  const daysOfWeek = [
    { value: 1, label: 'Monday' },
    { value: 2, label: 'Tuesday' },
    { value: 3, label: 'Wednesday' },
    { value: 4, label: 'Thursday' },
    { value: 5, label: 'Friday' },
    { value: 6, label: 'Saturday' },
    { value: 0, label: 'Sunday' },
  ];

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 sticky top-0 bg-white">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-indigo-100 rounded-lg">
              <Calendar className="text-indigo-600" size={24} />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Schedule Report</h2>
              <p className="text-sm text-gray-600">Automate report generation and delivery</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X size={24} />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Success Message */}
          {success && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-center space-x-3">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
              </div>
              <p className="text-sm font-medium text-green-800">Schedule created successfully!</p>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center space-x-3">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          {/* Report Type */}
          <div>
            <label className="flex items-center space-x-2 text-sm font-medium text-gray-700 mb-2">
              <FileText size={16} />
              <span>Report Type</span>
            </label>
            <select
              value={formData.report_type}
              onChange={(e) => setFormData({ ...formData, report_type: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              required
            >
              <option value="">Select a report...</option>
              {reportTypes.map((report) => (
                <option key={report.id} value={report.id}>
                  {report.name} ({report.category})
                </option>
              ))}
            </select>
          </div>

          {/* Frequency */}
          <div>
            <label className="flex items-center space-x-2 text-sm font-medium text-gray-700 mb-2">
              <Calendar size={16} />
              <span>Frequency</span>
            </label>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {['daily', 'weekly', 'monthly', 'quarterly'].map((freq) => (
                <button
                  key={freq}
                  type="button"
                  onClick={() => setFormData({ ...formData, frequency: freq as any })}
                  className={`px-4 py-2 rounded-lg border-2 font-medium transition-all ${
                    formData.frequency === freq
                      ? 'bg-indigo-100 text-indigo-700 border-indigo-500'
                      : 'bg-white text-gray-700 border-gray-300 hover:border-gray-400'
                  }`}
                >
                  {freq.charAt(0).toUpperCase() + freq.slice(1)}
                </button>
              ))}
            </div>
          </div>

          {/* Schedule Time */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="flex items-center space-x-2 text-sm font-medium text-gray-700 mb-2">
                <Clock size={16} />
                <span>Time</span>
              </label>
              <input
                type="time"
                value={formData.schedule_time}
                onChange={(e) => setFormData({ ...formData, schedule_time: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                required
              />
            </div>

            {/* Day of Week (for weekly) */}
            {formData.frequency === 'weekly' && (
              <div>
                <label className="text-sm font-medium text-gray-700 mb-2 block">Day of Week</label>
                <select
                  value={formData.day_of_week}
                  onChange={(e) => setFormData({ ...formData, day_of_week: Number(e.target.value) })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                >
                  {daysOfWeek.map((day) => (
                    <option key={day.value} value={day.value}>
                      {day.label}
                    </option>
                  ))}
                </select>
              </div>
            )}

            {/* Day of Month (for monthly) */}
            {formData.frequency === 'monthly' && (
              <div>
                <label className="text-sm font-medium text-gray-700 mb-2 block">Day of Month</label>
                <select
                  value={formData.day_of_month}
                  onChange={(e) => setFormData({ ...formData, day_of_month: Number(e.target.value) })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                >
                  {Array.from({ length: 28 }, (_, i) => i + 1).map((day) => (
                    <option key={day} value={day}>
                      Day {day}
                    </option>
                  ))}
                </select>
              </div>
            )}
          </div>

          {/* Recipients */}
          <div>
            <label className="flex items-center space-x-2 text-sm font-medium text-gray-700 mb-2">
              <Users size={16} />
              <span>Recipients</span>
            </label>
            <div className="space-y-2">
              {formData.recipients.map((recipient, index) => (
                <div key={index} className="flex gap-2">
                  <input
                    type="email"
                    value={recipient}
                    onChange={(e) => updateRecipient(index, e.target.value)}
                    placeholder="email@example.com"
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  />
                  {formData.recipients.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removeRecipient(index)}
                      className="px-3 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    >
                      Remove
                    </button>
                  )}
                </div>
              ))}
              <button
                type="button"
                onClick={addRecipient}
                className="text-sm text-indigo-600 hover:text-indigo-700 font-medium"
              >
                + Add another recipient
              </button>
            </div>
          </div>

          {/* Format */}
          <div>
            <label className="text-sm font-medium text-gray-700 mb-2 block">Report Format</label>
            <div className="grid grid-cols-3 gap-3">
              {[
                { value: 'pdf', label: 'PDF' },
                { value: 'excel', label: 'Excel' },
                { value: 'both', label: 'Both' },
              ].map((format) => (
                <button
                  key={format.value}
                  type="button"
                  onClick={() => setFormData({ ...formData, format: format.value as any })}
                  className={`px-4 py-2 rounded-lg border-2 font-medium transition-all ${
                    formData.format === format.value
                      ? 'bg-indigo-100 text-indigo-700 border-indigo-500'
                      : 'bg-white text-gray-700 border-gray-300 hover:border-gray-400'
                  }`}
                >
                  {format.label}
                </button>
              ))}
            </div>
          </div>

          {/* Enable/Disable */}
          <div className="flex items-center space-x-3">
            <input
              type="checkbox"
              id="enabled"
              checked={formData.enabled}
              onChange={(e) => setFormData({ ...formData, enabled: e.target.checked })}
              className="w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
            />
            <label htmlFor="enabled" className="text-sm font-medium text-gray-700">
              Enable schedule immediately
            </label>
          </div>

          {/* Actions */}
          <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="px-6 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors font-medium"
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
            >
              {loading ? (
                <>
                  <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span>Creating...</span>
                </>
              ) : (
                <span>Create Schedule</span>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
