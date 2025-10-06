// app/auth/profile/page.tsx
// User profile page

'use client';

import { useAuth, withAuth } from '../../../contexts/AuthContext';
import UserProfile from '../../../components/auth/UserProfile';

function ProfilePage() {
  return (
    <div className="container mx-auto py-8">
      <UserProfile />
    </div>
  );
}

export default withAuth(ProfilePage);