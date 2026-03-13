import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/auth-context';

export const SessionManager: React.FC = () => {
  const router = useRouter();
  const { user, signOut } = useAuth();

  useEffect(() => {
    // Set up session monitoring
    const checkSession = () => {
      if (user) {
        // Verify token is still valid
        const token = localStorage.getItem('auth-token');
        if (token) {
          try {
            const tokenParts = token.split('.');
            if (tokenParts.length === 3) {
              const payload = JSON.parse(atob(tokenParts[1]));
              const currentTime = Math.floor(Date.now() / 1000);

              // If token is expired, sign out user
              if (payload.exp <= currentTime) {
                signOut();
                router.push('/signin');
              }
            }
          } catch (error) {
            console.error('Error checking session:', error);
            signOut();
            router.push('/signin');
          }
        }
      }
    };

    // Check session initially and set up interval
    checkSession();
    const interval = setInterval(checkSession, 60000); // Check every minute

    // Clean up interval on unmount
    return () => clearInterval(interval);
  }, [user, signOut, router]);

  return null; // This component doesn't render anything
};