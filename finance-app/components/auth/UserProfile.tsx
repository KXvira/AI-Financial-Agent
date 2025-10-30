// components/auth/UserProfile.tsx
// User profile management component

'use client';

import { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { User, PasswordChange } from '../../types/auth';
import { AuthAPIError } from '../../utils/authApi';

interface UserProfileProps {
  onClose?: () => void;
}

export default function UserProfile({ onClose }: UserProfileProps) {
  const { user, updateProfile, changePassword, logout, loading } = useAuth();
  const [activeTab, setActiveTab] = useState<'profile' | 'password' | 'security'>('profile');
  const [isEditing, setIsEditing] = useState(false);
  const [profileData, setProfileData] = useState<Partial<User>>(
    user ? {
      full_name: user.full_name,
      phone_number: user.phone_number || '',
      business_name: user.business_name || '',
    } : {}
  );
  const [passwordData, setPasswordData] = useState<PasswordChange>({
    current_password: '',
    new_password: '',
  });
  const [confirmNewPassword, setConfirmNewPassword] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [successMessage, setSuccessMessage] = useState('');

  if (!user) return null;

  const handleProfileSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      await updateProfile(profileData);
      setIsEditing(false);
      setSuccessMessage('Profile updated successfully');
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (error) {
      if (error instanceof AuthAPIError) {
        setErrors({ profile: error.message });
      } else {
        setErrors({ profile: 'Failed to update profile' });
      }
    }
  };

  const handlePasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate password
    if (passwordData.new_password !== confirmNewPassword) {
      setErrors({ password: 'Passwords do not match' });
      return;
    }

    if (passwordData.new_password.length < 8) {
      setErrors({ password: 'Password must be at least 8 characters' });
      return;
    }

    try {
      await changePassword(passwordData);
      setPasswordData({ current_password: '', new_password: '' });
      setConfirmNewPassword('');
      setSuccessMessage('Password changed successfully');
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (error) {
      if (error instanceof AuthAPIError) {
        setErrors({ password: error.message });
      } else {
        setErrors({ password: 'Failed to change password' });
      }
    }
  };

  const getRoleBadgeColor = (role: string) => {
    switch (role) {
      case 'owner': return 'bg-purple-100 text-purple-800';
      case 'accountant': return 'bg-blue-100 text-blue-800';
      case 'employee': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md max-w-2xl mx-auto">
      <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
        <h2 className="text-xl font-semibold text-gray-900">User Profile</h2>
        {onClose && (
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </div>

      {successMessage && (
        <div className="mx-6 mt-4 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-md">
          {successMessage}
        </div>
      )}

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8 px-6">
          {[
            { key: 'profile', label: 'Profile' },
            { key: 'password', label: 'Password' },
            { key: 'security', label: 'Security' },
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as any)}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.key
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      <div className="p-6">
        {/* Profile Tab */}
        {activeTab === 'profile' && (
          <div className="space-y-6">
            <div className="flex items-center space-x-4">
              <div className="h-16 w-16 bg-blue-100 rounded-full flex items-center justify-center">
                <span className="text-xl font-semibold text-blue-600">
                  {user.full_name.split(' ').map(n => n[0]).join('').toUpperCase()}
                </span>
              </div>
              <div>
                <h3 className="text-lg font-medium text-gray-900">{user.full_name}</h3>
                <p className="text-gray-600">{user.email}</p>
                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getRoleBadgeColor(user.role)}`}>
                  {user.role.charAt(0).toUpperCase() + user.role.slice(1)}
                </span>
              </div>
            </div>

            <form onSubmit={handleProfileSubmit}>
              <div className="grid grid-cols-1 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Full Name
                  </label>
                  <input
                    type="text"
                    value={profileData.full_name || ''}
                    onChange={(e) => setProfileData(prev => ({ ...prev, full_name: e.target.value }))}
                    disabled={!isEditing || loading}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email Address
                  </label>
                  <input
                    type="email"
                    value={user.email}
                    disabled
                    className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-500"
                  />
                  <p className="mt-1 text-xs text-gray-500">Email cannot be changed</p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Phone Number
                  </label>
                  <input
                    type="tel"
                    value={profileData.phone_number || ''}
                    onChange={(e) => setProfileData(prev => ({ ...prev, phone_number: e.target.value }))}
                    disabled={!isEditing || loading}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50"
                    placeholder="+254 700 000 000"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Business Name
                  </label>
                  <input
                    type="text"
                    value={profileData.business_name || ''}
                    onChange={(e) => setProfileData(prev => ({ ...prev, business_name: e.target.value }))}
                    disabled={!isEditing || loading}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50"
                    placeholder="Your business name"
                  />
                </div>
              </div>

              {errors.profile && (
                <div className="mt-4 text-red-600 text-sm">{errors.profile}</div>
              )}

              <div className="mt-6 flex space-x-3">
                {isEditing ? (
                  <>
                    <button
                      type="submit"
                      disabled={loading}
                      className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
                    >
                      Save Changes
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        setIsEditing(false);
                        setProfileData({
                          full_name: user.full_name,
                          phone_number: user.phone_number || '',
                          business_name: user.business_name || '',
                        });
                      }}
                      className="bg-gray-300 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-400"
                    >
                      Cancel
                    </button>
                  </>
                ) : (
                  <button
                    type="button"
                    onClick={() => setIsEditing(true)}
                    className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
                  >
                    Edit Profile
                  </button>
                )}
              </div>
            </form>
          </div>
        )}

        {/* Password Tab */}
        {activeTab === 'password' && (
          <form onSubmit={handlePasswordSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Current Password
              </label>
              <input
                type="password"
                value={passwordData.current_password}
                onChange={(e) => setPasswordData(prev => ({ ...prev, current_password: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                New Password
              </label>
              <input
                type="password"
                value={passwordData.new_password}
                onChange={(e) => setPasswordData(prev => ({ ...prev, new_password: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Confirm New Password
              </label>
              <input
                type="password"
                value={confirmNewPassword}
                onChange={(e) => setConfirmNewPassword(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
            </div>

            {errors.password && (
              <div className="text-red-600 text-sm">{errors.password}</div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              Change Password
            </button>
          </form>
        )}

        {/* Security Tab */}
        {activeTab === 'security' && (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Account Security</h3>
              
              <div className="bg-gray-50 rounded-lg p-4 space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">Account Status</span>
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {user.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">Email Verified</span>
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    user.is_verified ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                  }`}>
                    {user.is_verified ? 'Verified' : 'Pending'}
                  </span>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">Last Login</span>
                  <span className="text-sm text-gray-600">
                    {user.last_login ? new Date(user.last_login).toLocaleDateString() : 'Never'}
                  </span>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">Member Since</span>
                  <span className="text-sm text-gray-600">
                    {new Date(user.created_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
            </div>

            <div>
              <h4 className="text-md font-medium text-gray-900 mb-3">Account Actions</h4>
              <button
                onClick={logout}
                disabled={loading}
                className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 disabled:opacity-50"
              >
                Sign Out
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}