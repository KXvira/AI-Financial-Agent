// types/lucide-react.d.ts
declare module 'lucide-react' {
  import * as React from 'react';
  
  export interface LucideProps {
    className?: string;
    size?: number | string;
    color?: string;
    strokeWidth?: number | string;
  }
  
  export const Send: React.FC<LucideProps>;
  export const Bot: React.FC<LucideProps>;
  export const User: React.FC<LucideProps>;
  export const Loader2: React.FC<LucideProps>;
  export const TrendingUp: React.FC<LucideProps>;
  export const FileText: React.FC<LucideProps>;
  export const DollarSign: React.FC<LucideProps>;
  export const BarChart3: React.FC<LucideProps>;
  export const Activity: React.FC<LucideProps>;
  export const AlertCircle: React.FC<LucideProps>;
  export const CheckCircle: React.FC<LucideProps>;
  export const Upload: React.FC<LucideProps>;
  export const Camera: React.FC<LucideProps>;
  export const X: React.FC<LucideProps>;
  export const Clock: React.FC<LucideProps>;
}
