// components/Navbar.tsx

"use client";

import Link from "next/link";

export default function Navbar() {
  return (
    <header className="flex justify-between items-center p-4 border-b">
      <div className="font-bold text-xl">FinTrack</div>
      <nav className="space-x-6 text-sm font-medium">
        <Link href="/">Dashboard</Link>
        <Link href="/invoices">Invoices</Link>
        <Link href="/payments">Payments</Link>
        <Link href="/customers">Customers</Link>
      </nav>
    </header>
  );
}
  