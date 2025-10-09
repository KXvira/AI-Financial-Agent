// app/layout.tsx
//Root page
import './globals.css';
import { AuthProvider } from '../contexts/AuthContext';
import Navbar from '../components/Navbar';
import ClientOnly from '../components/ClientOnly';

export const metadata = {
  title: 'FinTrack Dashboard - AI-Powered Financial Management',
  description: 'Manage your finances with AI-powered insights, M-Pesa integration, and smart expense tracking.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-gray-50 text-gray-900" suppressHydrationWarning={true}>
        <ClientOnly fallback={<div className="h-16 bg-white shadow-sm border-b"></div>}>
          <AuthProvider>
            <Navbar />
            <main className="p-8 max-w-7xl mx-auto">{children}</main>
          </AuthProvider>
        </ClientOnly>
      </body>
    </html>
  );
}
