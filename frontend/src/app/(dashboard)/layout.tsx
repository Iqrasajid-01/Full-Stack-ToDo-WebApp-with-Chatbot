'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/auth-context';
import { ChatbotButton } from '@/components/Chatbot';

export default function ProtectedLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { isAuthenticated, loading } = useAuth();
  const [hasToken, setHasToken] = useState(false);

  // Check for token on client side only
  useEffect(() => {
    const token = localStorage.getItem('auth-token');
    setHasToken(!!token);
    
    if (!loading && !isAuthenticated && !token) {
      router.push('/signin');
    }
  }, [isAuthenticated, loading, router]);

  // Always show loading briefly on initial render to prevent hydration mismatch
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-gray-800 dark:to-gray-900">
        <p className="text-gray-900 dark:text-white">Loading...</p>
      </div>
    );
  }

  if (!isAuthenticated && !hasToken) {
    return null;
  }

  return (
    <>
      {children}
      <ChatbotButton />
    </>
  );
}