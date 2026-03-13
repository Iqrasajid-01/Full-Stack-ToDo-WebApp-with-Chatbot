import React, { useState } from 'react';
import { Input } from '../ui/input';
import { Button } from '../ui/button';

interface AuthFormProps {
  type: 'signup' | 'signin';
  onSubmit: (data: { email: string; password: string; name?: string }) => void;
  loading: boolean;
  error?: string;
}

export const AuthForm: React.FC<AuthFormProps> = ({ type, onSubmit, loading, error }) => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: '',
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (type === 'signup') {
      onSubmit(formData);
    } else {
      onSubmit({
        email: formData.email,
        password: formData.password,
      });
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {error && (
        <div className="rounded-md bg-red-50 p-4">
          <div className="text-sm text-red-700">{error}</div>
        </div>
      )}

      {type === 'signup' && (
        <Input
          label="Full Name"
          id="name"
          name="name"
          type="text"
          required
          placeholder="John Doe"
          value={formData.name}
          onChange={handleChange}
        />
      )}

      <Input
        label="Email Address"
        id="email"
        name="email"
        type="email"
        autoComplete="email"
        required
        placeholder="you@example.com"
        value={formData.email}
        onChange={handleChange}
      />

      <Input
        label="Password"
        id="password"
        name="password"
        type="password"
        autoComplete={type === 'signin' ? 'current-password' : 'new-password'}
        required
        placeholder="••••••••"
        value={formData.password}
        onChange={handleChange}
      />

      <div>
        <Button
          type="submit"
          loading={loading}
          fullWidth
        >
          {loading ? (type === 'signup' ? 'Creating Account...' : 'Signing In...') : (type === 'signup' ? 'Sign Up' : 'Sign In')}
        </Button>
      </div>
    </form>
  );
};