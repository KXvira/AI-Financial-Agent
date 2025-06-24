// app/layout.tsx
//Root page
import './globals.css';
import Navbar from '../components/Navbar';

export const metadata = {
  title: 'FinTrack Dashboard',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-gray-50 text-gray-900">
        <Navbar />
        <main className="p-8 max-w-7xl mx-auto">{children}</main>
      </body>
    </html>
  );
}
