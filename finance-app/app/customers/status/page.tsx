"use client";

import { useSearchParams } from "next/navigation";

export default function PaymentStatusPage() {
  const params = useSearchParams();
  const success = params.get("success") === "true";
  const invoice = params.get("invoice");

  return (
    <div className="p-8 text-center">
      <h1 className="text-2xl font-bold mb-4">
        {success ? "Payment Successful" : "Payment Failed"}
      </h1>
      <p className="text-gray-600 mb-4">
        {success
          ? `Thank you. Payment for ${invoice} has been received.`
          : `Payment for ${invoice} could not be processed.`}
      </p>
      <a href="/customers" className="text-blue-600 underline">
        Back to Customer Portal
      </a>
    </div>
  );
}
