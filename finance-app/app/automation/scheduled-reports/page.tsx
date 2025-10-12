'use client';

import { useState, useEffect } from 'react';
import { Calendar, Clock, Mail, Play, Pause, Edit, Trash2, Plus, RefreshCw } from 'lucide-react';

interface ScheduleConfig {
  frequency: 'daily' | 'weekly' | 'monthly';
  time: string;
  day_of_week?: number;
  day_of_month?: number;
  timezone?: string;
}

interface Schedule {
  _id: string;
  report_type: string;
  schedule: ScheduleConfig;
  recipients: string[];
  enabled: boolean;
  created_at: string;
  last_run?: string;
  next_run?: string;
  run_count: number;
}

export default function ScheduledReportsPage() {
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingSchedule, setEditingSchedule] = useState<Schedule | null>(null);

  // Form state
  const [formData, setFormData] = useState({
    report_type: 'financial_summary',
    frequency: 'daily' as 'daily' | 'weekly' | 'monthly',
    time: '09:00',
    day_of_week: 1,
    day_of_month: 1,
    recipients: '',
    timezone: 'Africa/Nairobi',
  });

  useEffect(() => {
    fetchSchedules();
  }, []);

  const fetchSchedules = async () => {
    try {
      const response = await fetch('http://localhost:8000/automation/schedules');
      const data = await response.json();
      setSchedules(data.schedules || []);
    } catch (error) {
      console.error('Error fetching schedules:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateSchedule = async (e: React.FormEvent) => {
    e.preventDefault();

    const scheduleData = {
      report_type: formData.report_type,
      schedule: {
        frequency: formData.frequency,
        time: formData.time,
        timezone: formData.timezone,
        ...(formData.frequency === 'weekly' && { day_of_week: formData.day_of_week }),
        ...(formData.frequency === 'monthly' && { day_of_month: formData.day_of_month }),
      },
      recipients: formData.recipients.split(',').map(email => email.trim()),
    };

    try {
      const url = editingSchedule
        ? `http://localhost:8000/automation/schedules/${editingSchedule._id}`
        : 'http://localhost:8000/automation/schedules';
      
      const method = editingSchedule ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(scheduleData),
      });

      if (response.ok) {
        setShowCreateModal(false);
        setEditingSchedule(null);
        fetchSchedules();
        // Reset form
        setFormData({
          report_type: 'financial_summary',
          frequency: 'daily',
          time: '09:00',
          day_of_week: 1,
          day_of_month: 1,
          recipients: '',
          timezone: 'Africa/Nairobi',
        });
      }
    } catch (error) {
      console.error('Error creating/updating schedule:', error);
    }
  };

  const toggleSchedule = async (scheduleId: string) => {
    try {
      await fetch(`http://localhost:8000/automation/schedules/${scheduleId}/toggle`, {
        method: 'POST',
      });
      fetchSchedules();
    } catch (error) {
      console.error('Error toggling schedule:', error);
    }
  };

  const deleteSchedule = async (scheduleId: string) => {
    if (!confirm('Are you sure you want to delete this schedule?')) return;

    try {
      await fetch(`http://localhost:8000/automation/schedules/${scheduleId}`, {
        method: 'DELETE',
      });
      fetchSchedules();
    } catch (error) {
      console.error('Error deleting schedule:', error);
    }
  };

  const editSchedule = (schedule: Schedule) => {
    setEditingSchedule(schedule);
    setFormData({
      report_type: schedule.report_type,
      frequency: schedule.schedule.frequency,
      time: schedule.schedule.time,
      day_of_week: schedule.schedule.day_of_week || 1,
      day_of_month: schedule.schedule.day_of_month || 1,
      recipients: schedule.recipients.join(', '),
      timezone: schedule.schedule.timezone || 'Africa/Nairobi',
    });
    setShowCreateModal(true);
  };

  const formatFrequency = (schedule: ScheduleConfig) => {
    if (schedule.frequency === 'daily') return 'Daily';
    if (schedule.frequency === 'weekly') {
      const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
      return `Weekly on ${days[schedule.day_of_week || 0]}`;
    }
    if (schedule.frequency === 'monthly') {
      return `Monthly on day ${schedule.day_of_month}`;
    }
    return schedule.frequency;
  };

  const formatNextRun = (nextRun?: string) => {
    if (!nextRun) return 'Not scheduled';
    const date = new Date(nextRun);
    const now = new Date();
    const diff = date.getTime() - now.getTime();
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const days = Math.floor(hours / 24);

    if (days > 0) return `in ${days} day${days > 1 ? 's' : ''}`;
    if (hours > 0) return `in ${hours} hour${hours > 1 ? 's' : ''}`;
    return 'Soon';
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Scheduled Reports</h1>
            <p className="text-gray-600 mt-2">Automate your report generation and delivery</p>
          </div>
          <button
            onClick={() => {
              setEditingSchedule(null);
              setFormData({
                report_type: 'financial_summary',
                frequency: 'daily',
                time: '09:00',
                day_of_week: 1,
                day_of_month: 1,
                recipients: '',
                timezone: 'Africa/Nairobi',
              });
              setShowCreateModal(true);
            }}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg flex items-center gap-2 hover:bg-blue-700 transition-colors"
          >
            <Plus size={20} />
            New Schedule
          </button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Total Schedules</p>
                <p className="text-3xl font-bold text-gray-900 mt-1">{schedules.length}</p>
              </div>
              <Calendar className="text-blue-600" size={40} />
            </div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Active</p>
                <p className="text-3xl font-bold text-green-600 mt-1">
                  {schedules.filter(s => s.enabled).length}
                </p>
              </div>
              <Play className="text-green-600" size={40} />
            </div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Total Runs</p>
                <p className="text-3xl font-bold text-gray-900 mt-1">
                  {schedules.reduce((sum, s) => sum + s.run_count, 0)}
                </p>
              </div>
              <RefreshCw className="text-blue-600" size={40} />
            </div>
          </div>
        </div>

        {/* Schedules List */}
        {loading ? (
          <div className="text-center py-12">
            <RefreshCw className="animate-spin mx-auto mb-4 text-blue-600" size={40} />
            <p className="text-gray-600">Loading schedules...</p>
          </div>
        ) : schedules.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <Calendar className="mx-auto mb-4 text-gray-400" size={60} />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No Schedules Yet</h3>
            <p className="text-gray-600 mb-6">Create your first automated report schedule</p>
            <button
              onClick={() => setShowCreateModal(true)}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg inline-flex items-center gap-2 hover:bg-blue-700"
            >
              <Plus size={20} />
              Create Schedule
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-6">
            {schedules.map((schedule) => (
              <div key={schedule._id} className="bg-white rounded-lg shadow p-6">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-3">
                      <h3 className="text-xl font-semibold text-gray-900">
                        {schedule.report_type.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}
                      </h3>
                      <span
                        className={`px-3 py-1 rounded-full text-sm font-medium ${
                          schedule.enabled
                            ? 'bg-green-100 text-green-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}
                      >
                        {schedule.enabled ? 'Active' : 'Paused'}
                      </span>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                      <div className="flex items-center gap-2 text-gray-600">
                        <Clock size={18} />
                        <div>
                          <p className="text-sm font-medium">Schedule</p>
                          <p className="text-sm">{formatFrequency(schedule.schedule)} at {schedule.schedule.time}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2 text-gray-600">
                        <Calendar size={18} />
                        <div>
                          <p className="text-sm font-medium">Next Run</p>
                          <p className="text-sm">{formatNextRun(schedule.next_run)}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2 text-gray-600">
                        <Mail size={18} />
                        <div>
                          <p className="text-sm font-medium">Recipients</p>
                          <p className="text-sm">{schedule.recipients.length} recipient(s)</p>
                        </div>
                      </div>
                    </div>

                    <div className="flex flex-wrap gap-2 mb-2">
                      {schedule.recipients.map((email, index) => (
                        <span
                          key={index}
                          className="bg-blue-50 text-blue-700 px-3 py-1 rounded-full text-sm"
                        >
                          {email}
                        </span>
                      ))}
                    </div>

                    {schedule.last_run && (
                      <p className="text-sm text-gray-500">
                        Last run: {new Date(schedule.last_run).toLocaleString()} ({schedule.run_count} total runs)
                      </p>
                    )}
                  </div>

                  <div className="flex gap-2 ml-4">
                    <button
                      onClick={() => toggleSchedule(schedule._id)}
                      className={`p-2 rounded-lg transition-colors ${
                        schedule.enabled
                          ? 'bg-yellow-100 text-yellow-700 hover:bg-yellow-200'
                          : 'bg-green-100 text-green-700 hover:bg-green-200'
                      }`}
                      title={schedule.enabled ? 'Pause' : 'Resume'}
                    >
                      {schedule.enabled ? <Pause size={20} /> : <Play size={20} />}
                    </button>
                    <button
                      onClick={() => editSchedule(schedule)}
                      className="p-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors"
                      title="Edit"
                    >
                      <Edit size={20} />
                    </button>
                    <button
                      onClick={() => deleteSchedule(schedule._id)}
                      className="p-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors"
                      title="Delete"
                    >
                      <Trash2 size={20} />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Create/Edit Modal */}
        {showCreateModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6">
                <h2 className="text-2xl font-bold text-gray-900 mb-6">
                  {editingSchedule ? 'Edit Schedule' : 'Create New Schedule'}
                </h2>

                <form onSubmit={handleCreateSchedule}>
                  {/* Report Type */}
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Report Type
                    </label>
                    <select
                      value={formData.report_type}
                      onChange={(e) => setFormData({ ...formData, report_type: e.target.value })}
                      className="w-full border border-gray-300 rounded-lg px-4 py-2"
                      required
                    >
                      <option value="financial_summary">Financial Summary</option>
                      <option value="income_statement">Income Statement</option>
                      <option value="cash_flow">Cash Flow Statement</option>
                      <option value="ar_aging">AR Aging Report</option>
                      <option value="transaction_report">Transaction Report</option>
                      <option value="customer_report">Customer Report</option>
                    </select>
                  </div>

                  {/* Frequency */}
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Frequency
                    </label>
                    <select
                      value={formData.frequency}
                      onChange={(e) => setFormData({ ...formData, frequency: e.target.value as any })}
                      className="w-full border border-gray-300 rounded-lg px-4 py-2"
                      required
                    >
                      <option value="daily">Daily</option>
                      <option value="weekly">Weekly</option>
                      <option value="monthly">Monthly</option>
                    </select>
                  </div>

                  {/* Time */}
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Time
                    </label>
                    <input
                      type="time"
                      value={formData.time}
                      onChange={(e) => setFormData({ ...formData, time: e.target.value })}
                      className="w-full border border-gray-300 rounded-lg px-4 py-2"
                      required
                    />
                  </div>

                  {/* Day of Week (for weekly) */}
                  {formData.frequency === 'weekly' && (
                    <div className="mb-4">
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Day of Week
                      </label>
                      <select
                        value={formData.day_of_week}
                        onChange={(e) => setFormData({ ...formData, day_of_week: parseInt(e.target.value) })}
                        className="w-full border border-gray-300 rounded-lg px-4 py-2"
                        required
                      >
                        <option value={0}>Monday</option>
                        <option value={1}>Tuesday</option>
                        <option value={2}>Wednesday</option>
                        <option value={3}>Thursday</option>
                        <option value={4}>Friday</option>
                        <option value={5}>Saturday</option>
                        <option value={6}>Sunday</option>
                      </select>
                    </div>
                  )}

                  {/* Day of Month (for monthly) */}
                  {formData.frequency === 'monthly' && (
                    <div className="mb-4">
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Day of Month
                      </label>
                      <input
                        type="number"
                        min="1"
                        max="31"
                        value={formData.day_of_month}
                        onChange={(e) => setFormData({ ...formData, day_of_month: parseInt(e.target.value) })}
                        className="w-full border border-gray-300 rounded-lg px-4 py-2"
                        required
                      />
                    </div>
                  )}

                  {/* Recipients */}
                  <div className="mb-6">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Email Recipients (comma-separated)
                    </label>
                    <textarea
                      value={formData.recipients}
                      onChange={(e) => setFormData({ ...formData, recipients: e.target.value })}
                      className="w-full border border-gray-300 rounded-lg px-4 py-2"
                      rows={3}
                      placeholder="john@example.com, jane@example.com"
                      required
                    />
                  </div>

                  {/* Buttons */}
                  <div className="flex gap-3">
                    <button
                      type="submit"
                      className="flex-1 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      {editingSchedule ? 'Update Schedule' : 'Create Schedule'}
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        setShowCreateModal(false);
                        setEditingSchedule(null);
                      }}
                      className="px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                    >
                      Cancel
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
