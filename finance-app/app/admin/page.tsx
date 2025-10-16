'use client';

import { useEffect, useState } from 'react';
import { Users, Activity, ShieldAlert, TrendingUp, UserCheck, UserX } from 'lucide-react';

interface AdminStats {
  total_users: number;
  active_users: number;
  users_by_role: Record<string, number>;
  recent_activity_24h: number;
  failed_logins_today: number;
}

interface UserPermissions {
  user_id: string;
  email: string;
  role: string;
  permissions: string[];
}

export default function AdminDashboard() {
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [permissions, setPermissions] = useState<UserPermissions | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchAdminData();
  }, []);

  const fetchAdminData = async () => {
    try {
      setLoading(true);
      setError(null);

      const token = localStorage.getItem('token');
      if (!token) {
        setError('Not authenticated. Please log in.');
        return;
      }

      // Fetch stats
      const statsResponse = await fetch('http://localhost:8000/admin/stats', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!statsResponse.ok) {
        if (statsResponse.status === 401) {
          setError('Session expired. Please log in again.');
          return;
        }
        if (statsResponse.status === 403) {
          setError('Access denied. You do not have admin privileges.');
          return;
        }
        throw new Error(`Failed to fetch stats: ${statsResponse.statusText}`);
      }

      const statsData = await statsResponse.json();
      setStats(statsData);

      // Fetch permissions
      const permResponse = await fetch('http://localhost:8000/admin/permissions', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (permResponse.ok) {
        const permData = await permResponse.json();
        setPermissions(permData);
      }

    } catch (err) {
      console.error('Error fetching admin data:', err);
      setError(err instanceof Error ? err.message : 'Failed to load admin data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="flex items-center justify-center h-[calc(100vh-64px)]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading admin dashboard...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="flex items-center justify-center h-[calc(100vh-64px)]">
          <div className="text-center max-w-md">
            <ShieldAlert className="w-16 h-16 text-red-500 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Access Error</h2>
            <p className="text-gray-600 mb-6">{error}</p>
            <button
              onClick={() => window.location.href = '/'}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Go to Home
            </button>
          </div>
        </div>
      </div>
    );
  }

  const roleColors: Record<string, string> = {
    admin: 'bg-purple-100 text-purple-800',
    owner: 'bg-blue-100 text-blue-800',
    manager: 'bg-green-100 text-green-800',
    accountant: 'bg-yellow-100 text-yellow-800',
    viewer: 'bg-gray-100 text-gray-800'
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
          <p className="mt-2 text-gray-600">
            System overview and management controls
          </p>
          {permissions && (
            <div className="mt-4 flex items-center gap-2">
              <span className="text-sm text-gray-600">Logged in as:</span>
              <span className="text-sm font-semibold text-gray-900">{permissions.email}</span>
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${roleColors[permissions.role] || 'bg-gray-100 text-gray-800'}`}>
                {permissions.role.toUpperCase()}
              </span>
            </div>
          )}
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Total Users */}
          <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Users</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">
                  {stats?.total_users || 0}
                </p>
              </div>
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <Users className="w-6 h-6 text-blue-600" />
              </div>
            </div>
          </div>

          {/* Active Users */}
          <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Active Users</p>
                <p className="text-3xl font-bold text-green-600 mt-2">
                  {stats?.active_users || 0}
                </p>
              </div>
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <UserCheck className="w-6 h-6 text-green-600" />
              </div>
            </div>
          </div>

          {/* Recent Activity */}
          <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Activity (24h)</p>
                <p className="text-3xl font-bold text-indigo-600 mt-2">
                  {stats?.recent_activity_24h || 0}
                </p>
              </div>
              <div className="w-12 h-12 bg-indigo-100 rounded-lg flex items-center justify-center">
                <Activity className="w-6 h-6 text-indigo-600" />
              </div>
            </div>
          </div>

          {/* Failed Logins */}
          <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Failed Logins</p>
                <p className="text-3xl font-bold text-red-600 mt-2">
                  {stats?.failed_logins_today || 0}
                </p>
              </div>
              <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
                <UserX className="w-6 h-6 text-red-600" />
              </div>
            </div>
          </div>
        </div>

        {/* Users by Role */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Users by Role</h3>
            <div className="space-y-3">
              {stats?.users_by_role && Object.entries(stats.users_by_role).map(([role, count]) => (
                <div key={role} className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${roleColors[role] || 'bg-gray-100 text-gray-800'}`}>
                      {role.toUpperCase()}
                    </span>
                  </div>
                  <span className="text-2xl font-bold text-gray-900">{count}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
            <div className="space-y-3">
              <button
                onClick={() => window.location.href = '/admin/users'}
                className="w-full flex items-center gap-3 px-4 py-3 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors text-left"
              >
                <Users className="w-5 h-5 text-blue-600" />
                <div>
                  <p className="font-medium text-gray-900">Manage Users</p>
                  <p className="text-sm text-gray-600">Create, edit, and delete users</p>
                </div>
              </button>

              <button
                onClick={() => window.location.href = '/admin/activity'}
                className="w-full flex items-center gap-3 px-4 py-3 bg-indigo-50 hover:bg-indigo-100 rounded-lg transition-colors text-left"
              >
                <Activity className="w-5 h-5 text-indigo-600" />
                <div>
                  <p className="font-medium text-gray-900">View Activity Logs</p>
                  <p className="text-sm text-gray-600">Monitor system activity</p>
                </div>
              </button>

              <button
                onClick={() => window.location.href = '/reports'}
                className="w-full flex items-center gap-3 px-4 py-3 bg-green-50 hover:bg-green-100 rounded-lg transition-colors text-left"
              >
                <TrendingUp className="w-5 h-5 text-green-600" />
                <div>
                  <p className="font-medium text-gray-900">Generate Reports</p>
                  <p className="text-sm text-gray-600">View and schedule reports</p>
                </div>
              </button>
            </div>
          </div>
        </div>

        {/* Permissions Info */}
        {permissions && permissions.permissions.includes('*') && (
          <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg p-6 border border-purple-200">
            <div className="flex items-start gap-4">
              <ShieldAlert className="w-6 h-6 text-purple-600 flex-shrink-0 mt-1" />
              <div>
                <h4 className="font-semibold text-gray-900 mb-2">Full System Access</h4>
                <p className="text-sm text-gray-700">
                  You have unrestricted access to all system features and settings. 
                  Use these privileges responsibly to manage users, view sensitive data, and configure system settings.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
