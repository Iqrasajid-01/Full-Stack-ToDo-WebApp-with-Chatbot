'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/contexts/auth-context';
import { useTheme } from '@/contexts/theme-context';
import { Button } from '@/components/ui/button';
import { MoonIcon, SunIcon } from 'lucide-react';

export default function SignInPage() {
  const router = useRouter();
  const { signIn, refreshSession } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;

    // Check password length when password field is updated
    if (name === 'password' && value.length > 72) {
      setError('Password must be 72 characters or less due to system limitation');
    } else if (name === 'password' && error?.includes('Password must be 72 characters or less')) {
      // Clear the password error if user corrected the password
      setError(null);
    }

    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    // Additional check before submitting
    if (formData.password.length > 72) {
      setError('Password must be 72 characters or less due to system limitation');
      setLoading(false);
      return;
    }

    try {
      const success = await signIn(formData);

      if (success) {
        // Refresh the session to ensure the auth context is updated
        await refreshSession();
        // Redirect to dashboard immediately
        window.location.href = '/dashboard'; // Use window.location for faster redirect
      } else {
        // Retrieve the specific error message from localStorage
        const errorMessage = localStorage.getItem('auth-error');
        if (errorMessage) {
          setError(errorMessage);
          localStorage.removeItem('auth-error'); // Clean up
        } else {
          setError('Sign in failed. Please try again.');
        }
      }
    } catch (err: any) {
      if (err.message?.includes('Incorrect email or password')) {
        setError('Incorrect email or password. Please try again.');
      } else {
        setError(err.message || 'Network error occurred');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-50 py-12 px-4 sm:px-6 lg:px-8 dark:bg-gray-900 dark:text-white">
      <div className="absolute top-4 right-4 z-10">
        <Button
          variant="ghost"
          onClick={toggleTheme}
          className="bg-transparent border-0 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-full p-2 min-w-[32px]"
          aria-label="Toggle theme"
        >
          {theme === 'dark' ? (
            <SunIcon className="h-5 w-5 text-yellow-500" />
          ) : (
            <MoonIcon className="h-5 w-5 text-gray-700" />
          )}
        </Button>
      </div>
      <div className="flex items-center justify-center flex-grow">
        <div className="max-w-md w-full space-y-8">
          <div>
            <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900 dark:text-white">
              Sign in to your account
            </h2>
          </div>
          <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
            {error && (
              <div className="rounded-md bg-red-50 p-4 dark:bg-red-900/30">
                <div className="text-sm text-red-700 dark:text-red-300">{error}</div>
              </div>
            )}

            <div className="rounded-md shadow-sm space-y-4">
              <div>
                <input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  required
                  className="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm dark:text-white dark:bg-gray-700 dark:border-gray-600"
                  placeholder="Email address"
                  value={formData.email}
                  onChange={handleChange}
                />
              </div>
              <div>
                <input
                  id="password"
                  name="password"
                  type="password"
                  autoComplete="current-password"
                  required
                  className="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm dark:text-white dark:bg-gray-700 dark:border-gray-600"
                  placeholder="Password"
                  value={formData.password}
                  onChange={handleChange}
                />
              </div>
            </div>

            <div>
              <button
                type="submit"
                disabled={loading}
                className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 dark:bg-indigo-700 dark:hover:bg-indigo-800"
              >
                {loading ? 'Signing in...' : 'Sign in'}
              </button>
            </div>
          </form>

          <div className="text-center text-sm text-gray-600 dark:text-gray-400">
            Don't have an account?{' '}
            <Link href="/signup" className="font-medium text-indigo-600 hover:text-indigo-500 dark:text-indigo-400 dark:hover:text-indigo-300">
              Sign up
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}