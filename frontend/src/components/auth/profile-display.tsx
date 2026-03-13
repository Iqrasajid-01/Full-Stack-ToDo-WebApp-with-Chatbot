import React from 'react';
import { useAuth } from '@/contexts/auth-context';

export const ProfileDisplay: React.FC = () => {
  const { user, loading } = useAuth();

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!user) {
    return null;
  }

  return (
    <div className="flex items-center space-x-4">
      <div className="text-right">
        <p className="text-sm font-medium text-gray-900">{user.name || user.email}</p>
        <p className="text-xs text-gray-500">Member since {new Date(user.createdAt).toLocaleDateString()}</p>
      </div>
    </div>
  );
};