// types/auth.ts
// Authentication type definitions

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: 'owner' | 'accountant' | 'employee';
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  last_login?: string;
  phone_number?: string;
  business_name?: string;
}

export interface UserProfile extends User {
  // Extended profile information
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  full_name: string;
  phone_number?: string;
  business_name?: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface AuthResponse {
  message: string;
  user: User;
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface PasswordChange {
  current_password: string;
  new_password: string;
}

export interface AuditLog {
  id: string;
  user_id: string;
  action: string;
  details: Record<string, any>;
  ip_address: string;
  timestamp: string;
}

export interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<void>;
  updateProfile: (data: Partial<User>) => Promise<void>;
  changePassword: (data: PasswordChange) => Promise<void>;
}