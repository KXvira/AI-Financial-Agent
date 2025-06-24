// components/StatCard.tsx
type StatCardProps = {
    title: string;
    amount: string;
    change: string;
    isPositive: boolean;
  };
  
  export default function StatCard({ title, amount, change, isPositive }: StatCardProps) {
    return (
      <div className="bg-gray-100 p-4 rounded-lg shadow-sm">
        <h4 className="text-sm text-gray-500">{title}</h4>
        <p className="text-xl font-bold">{amount}</p>
        <p className={`text-sm ${isPositive ? 'text-green-600' : 'text-red-500'}`}>
          {isPositive ? '+' : ''}{change}
        </p>
      </div>
    );
  }
  