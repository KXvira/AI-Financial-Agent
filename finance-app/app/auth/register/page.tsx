// app/auth/register/page.tsx
// Registration/Sign-up page

'use client';

import { useRouter } from 'next/navigation';
import RegisterForm from '../../../components/auth/RegisterForm';

export default function RegisterPage() {
  const router = useRouter();

  const handleAuthSuccess = () => {
    // Redirect to dashboard after successful registration
    router.push('/');
  };

  const handleSwitchToLogin = () => {
    // Navigate to login page
    router.push('/auth/login');
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <RegisterForm
          onSuccess={handleAuthSuccess}
          onSwitchToLogin={handleSwitchToLogin}
        />
      </div>
    </div>
  );
}
