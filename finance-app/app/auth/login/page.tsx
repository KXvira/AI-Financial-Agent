// app/auth/login/page.tsx
// Login page

'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import LoginForm from '../../../components/auth/LoginForm';
import RegisterForm from '../../../components/auth/RegisterForm';

export default function LoginPage() {
  const [isLogin, setIsLogin] = useState(true);
  const router = useRouter();

  const handleAuthSuccess = () => {
    // Redirect to dashboard after successful authentication
    router.push('/');
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        {isLogin ? (
          <LoginForm
            onSuccess={handleAuthSuccess}
            onSwitchToRegister={() => setIsLogin(false)}
          />
        ) : (
          <RegisterForm
            onSuccess={handleAuthSuccess}
            onSwitchToLogin={() => setIsLogin(true)}
          />
        )}
      </div>
    </div>
  );
}