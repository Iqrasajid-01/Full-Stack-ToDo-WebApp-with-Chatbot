'use client';

import { AuthProvider } from '@/contexts/auth-context';
import { ThemeProvider } from '@/contexts/theme-context';
import { ReactNode } from 'react';

export default function AuthWrapper({ children }: { children: ReactNode }) {
  // Wrap with both providers
  return (
    <ThemeProvider>
      <AuthProvider>
        {children}
      </AuthProvider>
    </ThemeProvider>
  );
}